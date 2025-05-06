from flask import Blueprint, request, jsonify
from ..services.ai_service import AiService
from ..services.query_classifier import QueryClassifier
from ..services.schedule_service import ScheduleService
from ..services.ptit_auth_service import PTITAuthService
from ..utils.logger import Logger
from ..lib.supabase import supabase
import time
from datetime import datetime, timedelta
import json

chat_bp = Blueprint('chat', __name__)
ai_service = AiService()
logger = Logger()
query_classifier = QueryClassifier()
schedule_service = ScheduleService()
ptit_auth_service = PTITAuthService()

# Initialize schedule service with auth service and AI service
schedule_service.set_auth_service(ptit_auth_service)
schedule_service.set_ai_service(ai_service)

@chat_bp.route('/chat', methods=['POST'])
async def chat():
    try:
        data = request.json
        file_id = data.get('file_id')  # handle file context
        message = data.get('message')
        conversation_history = data.get('conversation_history', [])
        if file_id:
            # use file context handler
            response, updated_history = await ai_service.chat_with_file_context(
                message, file_id, conversation_history
            )
            return jsonify({
                'response': response,
                'conversation_history': updated_history,
                'file_context_active': True,
                'file_id': file_id
            })
        
        if not message:
            return jsonify({'error': 'No message provided', 'response': None}), 400

        # Log user message
        logger.log_with_timestamp("USER INPUT", message, f"Message length: {len(message)} chars")
        
        # Use the QueryClassifier to classify the message
        classification_result = query_classifier.classify_query(message)

        # Handle UML/PlantUML diagram requests
        if classification_result.get('category') == 'uml':
            uml_prompt = {
                "role": "system",
                "content": (
                    "Bạn là một trợ lý lập trình chuyên nghiệp. Khi trả về sơ đồ UML, "
                    "hãy luôn bao bọc mã PlantUML trong khối mã dùng dấu ba phẩy ngược và tag `plantuml`, "
                    "ví dụ: ```plantuml ... ``` để frontend có thể hiển thị hình ảnh. "
                    "Không kèm giải thích thêm, chỉ xuất khối mã sơ đồ UML."
                )
            }
            # Get response from AI - REMOVE await since chat_with_ai is not async
            response, updated_history = ai_service.chat_with_ai(
                message,
                [uml_prompt]
            )
            # Ensure PlantUML content is fenced for ReactMarkdown
            content = response.strip()
            if not (content.startswith('```') and content.endswith('```')):
                content = f"```plantuml\n{content}\n```"
            # Update response and history with fenced code
            response = content
            updated_history[-1]["content"] = content  # Update the last message which should be assistant
            return jsonify({
                'response': response,
                'conversation_history': updated_history,
                'query_type': 'uml'
            })
        
        # Log the classification result
        logger.log_with_timestamp(
            "CLASSIFICATION", 
            classification_result['category'].upper(),
            f"Confidence: {classification_result['confidence']:.2f} | Method: {classification_result['method']}"
        )
        
        # Handle non-academic topics immediately
        if classification_result['category'] == 'other':
            non_educational_response = (
                "Xin lỗi, tôi chỉ có thể hỗ trợ bạn với các câu hỏi liên quan đến học tập và giáo dục. "
                "Vui lòng đặt câu hỏi khác về chủ đề học tập."
            )
            logger.log_with_timestamp("STANDARD RESPONSE", non_educational_response, "Non-educational query detected")
            return jsonify({
                'response': non_educational_response,
                'conversation_history': conversation_history,
                'query_type': 'other'
            })
        
        # Handle schedule-related queries with date extraction
        if classification_result['category'] == 'schedule' or classification_result['category'] == 'date_query':
            # Log the detected date type for debugging
            logger.log_with_timestamp(
                "DATE QUERY", 
                f"Processing date query", 
                f"Query type: {classification_result['category']}"
            )
            # Log that we're handling a schedule query
            current_time = datetime.now()
            logger.log_with_timestamp(
                "SCHEDULE QUERY", 
                f"Processing schedule request", 
                f"Current time: {current_time.strftime('%d/%m/%Y %H:%M:%S')}"
            )
            
            try:
                # Get university credentials from request
                credentials = data.get('university_credentials')
                if not credentials:
                    raise Exception("Vui lòng cập nhật thông tin đăng nhập vào hệ thống trường học trong phần Thiết lập.")
                    
                # Login to PTIT system
                success, error = ptit_auth_service.login(
                    credentials['university_username'],
                    credentials['university_password']
                )
                
                if not success:
                    raise Exception("Không thể đăng nhập vào hệ thống trường học. Vui lòng kiểm tra lại thông tin đăng nhập.")
                    
                # Get current semester
                current_semester, semester_error = ptit_auth_service.get_current_semester()
                if semester_error:
                    raise Exception(f"Không thể lấy thông tin học kỳ: {semester_error}")
                    
                # Process schedule query using the schedule service
                schedule_result = await schedule_service.get_schedule_by_semester(current_semester['hoc_ky'])
                
                # Process the schedule data
                date_info_tuple = schedule_service.extract_date_references(message)
                
                # Add safety check to handle None value from extract_date_references
                if date_info_tuple is None:
                    logger.log_with_timestamp(
                        "DATE EXTRACTION ERROR", 
                        "Failed to extract date information from message",
                        f"Message: {message}"
                    )
                    # Default to today's date if extraction fails
                    today = datetime.now().date()
                    date_info_tuple = (today, 'today', 'default')
                    logger.log_with_timestamp(
                        "DATE EXTRACTION", 
                        f"Using fallback date: {today.strftime('%d/%m/%Y')}",
                        "Type: today | Original text: default"
                    )
                
                date_info_value = date_info_tuple[0]  # Get the actual date value (can be a date or a tuple of dates)
                
                # Log the extracted date information for debugging
                if isinstance(date_info_value, tuple):
                    start_date, end_date = date_info_value
                    logger.log_with_timestamp(
                        "DATE EXTRACTION", 
                        f"Date range: {start_date.strftime('%d/%m/%Y')} to {end_date.strftime('%d/%m/%Y')}",
                        f"Type: {date_info_tuple[1]} | Original text: {date_info_tuple[2]}"
                    )
                else:
                    logger.log_with_timestamp(
                        "DATE EXTRACTION", 
                        f"Single date: {date_info_value.strftime('%d/%m/%Y')}",
                        f"Type: {date_info_tuple[1]} | Original text: {date_info_tuple[2]}"
                    )
                
                # Handle date formatting differently depending on whether it's a single date or date range
                if isinstance(date_info_value, tuple):  # It's a date range
                    start_date, end_date = date_info_value
                    formatted_date_info = f"{start_date.strftime('%d/%m/%Y')} to {end_date.strftime('%d/%m/%Y')}"
                    
                    # Get schedule for all days in the range for this_week, next_week, last_week and specific_week
                    if date_info_tuple[1] in ['this_week', 'next_week', 'last_week', 'specific_week']:
                        all_classes = []
                        days_in_range = (end_date - start_date).days + 1
                        days_to_fetch = min(days_in_range, 7)  # Limit to 7 days for week queries
                        
                        logger.log_with_timestamp("SCHEDULE API", f"Processing week range: {start_date.strftime('%d/%m/%Y')} to {end_date.strftime('%d/%m/%Y')}")
                        
                        # Check each day in the range for classes
                        for i in range(days_to_fetch):
                            current_date = start_date + timedelta(days=i)
                            logger.log_with_timestamp("SCHEDULE API", f"Checking day {i+1} of range: {current_date.strftime('%d/%m/%Y')}")
                            
                            daily_classes = schedule_service.get_class_schedule(schedule_result, current_date)
                            if daily_classes:
                                logger.log_with_timestamp("SCHEDULE API", f"Found {len(daily_classes)} classes on {current_date.strftime('%d/%m/%Y')}")
                                for class_info in daily_classes:
                                    # Add date information to each class
                                    class_info['date'] = current_date.strftime('%d/%m/%Y')
                                    class_info['day_of_week'] = current_date.strftime('%A')
                                    all_classes.append(class_info)
                            else:
                                logger.log_with_timestamp("SCHEDULE API", f"No classes on {current_date.strftime('%d/%m/%Y')}")
                        
                        schedule_text = all_classes
                        logger.log_with_timestamp("SCHEDULE API", f"Total classes found across week: {len(all_classes)}")
                    else:
                        # For other date ranges, just get the first day (old behavior)
                        schedule_text = schedule_service.get_class_schedule(schedule_result, start_date)
                else:  # It's a single date
                    formatted_date_info = date_info_value.strftime('%d/%m/%Y')
                    schedule_text = schedule_service.get_class_schedule(schedule_result, date_info_value)
                
                schedule_result = {
                    'date_info': formatted_date_info,
                    'date_type': date_info_tuple[1],
                    'original_text': date_info_tuple[2],
                    'schedule_text': schedule_text
                }
                
                # Log the schedule processing result
                logger.log_with_timestamp(
                    "SCHEDULE RESULT", 
                    f"Date: {schedule_result['date_info']}",
                    f"Type: {schedule_result['date_type']} | Original text: {schedule_result['original_text']}"
                )
                
                # Create a contextualized response using AI
                # Format the schedule text for the single day or other date types
                if isinstance(schedule_result['schedule_text'], list) and len(schedule_result['schedule_text']) == 0:
                    # No classes found for this date/range
                    # Check if we had a default date (when the user's query was unclear)
                    if date_info_tuple[2] == 'default':
                        # The date was a fallback because we couldn't identify a specific date in the query
                        schedule_prompt = {
                            "role": "system",
                            "content": f"""
                            You are a helpful study assistant for university students. The student asked about their schedule but didn't specify a clear date.
                            Their query was: "{message}"
                            
                            Please respond in Vietnamese, politely asking them to specify which day or date they're asking about.
                            Use a professional and respectful tone appropriate for university students - avoid using "em" and instead use more formal language.
                            For example, they could clarify with "thứ 7 tuần này", "thứ 2 tuần sau", or a specific date.
                            Your response should be friendly and helpful, encouraging them to provide more details so you can assist them better.
                            """
                        }
                    else:
                        # We understood the date, but no classes were found
                        vietnamese_weekday_map = {
                            "monday": "Thứ Hai",
                            "tuesday": "Thứ Ba",
                            "wednesday": "Thứ Tư", 
                            "thursday": "Thứ Năm",
                            "friday": "Thứ Sáu",
                            "saturday": "Thứ Bảy",
                            "sunday": "Chủ Nhật"
                        }
                        
                        # Get a friendly date representation
                        date_repr = ""
                        if isinstance(date_info_value, tuple):
                            # It's a date range
                            start_date, end_date = date_info_value
                            start_date_str = start_date.strftime('%d/%m/%Y')
                            end_date_str = end_date.strftime('%d/%m/%Y')
                            date_repr = f"từ {start_date_str} đến {end_date_str}"
                        else:
                            # It's a single date
                            date_str = date_info_value.strftime('%d/%m/%Y')
                            # Get the actual weekday from the date object directly
                            weekday_name = date_info_value.strftime('%A').lower()
                            vn_weekday = vietnamese_weekday_map.get(weekday_name, weekday_name)
                            # Double-check the weekday is correct by comparing with the date
                            actual_day = date_info_value.weekday()
                            correct_weekday = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"][actual_day]
                            if correct_weekday != weekday_name:
                                logger.log_with_timestamp(
                                    "DATE MISMATCH", 
                                    f"Weekday mismatch detected! Label: {weekday_name}, Actual: {correct_weekday}",
                                    f"Date: {date_str}"
                                )
                                # Use the correct weekday based on the actual date
                                vn_weekday = vietnamese_weekday_map.get(correct_weekday, correct_weekday)
                                
                            date_repr = f"{vn_weekday}, ngày {date_str}"
                        
                        schedule_prompt = {
                            "role": "system",
                            "content": f"""
                            You are a helpful study assistant. The student asked about their schedule for {date_repr}.
                            After checking the system, no classes were found for this date.
                            
                            Please respond in Vietnamese, letting them know there are no classes scheduled for {date_repr}.
                            Offer to check another date if they'd like. Be helpful and friendly in your response.
                            """
                        }
                else:
                    # We have schedule data to share
                    # Format the schedule data properly
                    if isinstance(schedule_result['schedule_text'], list):
                        # It's a list of classes
                        formatted_schedule = ""
                        for i, class_info in enumerate(schedule_result['schedule_text'], 1):
                            # Add Vietnamese subject name
                            formatted_schedule += f"{i}. {class_info.get('ten_mon', '')} ({class_info.get('ma_mon', '')})\n"
                            
                            # Add English subject name if available
                            if class_info.get('ten_mon_eg'):
                                formatted_schedule += f"    {class_info.get('ten_mon_eg')}\n"
                                
                            # Add class time
                            formatted_schedule += f"    {class_info.get('time', '')}\n"
                            
                            # Add room information
                            formatted_schedule += f"    Phòng {class_info.get('room', '')}\n"
                            
                            # Add lecturer information with ID
                            formatted_schedule += f"    {class_info.get('lecturer', '')}"
                            if class_info.get('ma_giang_vien'):
                                formatted_schedule += f" (Mã GV: {class_info.get('ma_giang_vien')})"
                            formatted_schedule += "\n"
                            
                            # Add credit hours if available
                            if class_info.get('so_tin_chi'):
                                formatted_schedule += f"    Số tín chỉ: {class_info.get('so_tin_chi')}\n"
                                
                            formatted_schedule += "\n"
                    else:
                        # It's some other format, just convert to string
                        formatted_schedule = str(schedule_result['schedule_text'])
                    
                    # If there's no data after formatting, show a message
                    if not formatted_schedule or formatted_schedule.strip() == "":
                        formatted_schedule = "Không tìm thấy thông tin lớp học cho ngày này."
                    
                    schedule_prompt = {
                        "role": "system",
                        "content": f"""
                        You are a helpful study assistant. The student asked about their schedule.
                        Here is the schedule information retrieved from the system:

                        {formatted_schedule}

                        Please respond in Vietnamese, summarizing this information in a natural, 
                        conversational way. Mention the date and add any relevant reminders 
                        about being on time for classes. Keep your response concise and friendly.
                        """
                    }
                
                print(f"Schedule prompt: {schedule_prompt['content']}")
                
                # Get AI to format the response nicely
                try:
                    enhanced_response, _ = ai_service.chat_with_ai(
                        message, 
                        [schedule_prompt]
                    )
                except Exception as ai_error:
                    # Log the error
                    logger.log_with_timestamp("SCHEDULE AI ERROR", f"Failed to get AI response: {str(ai_error)}")
                    
                    # Generate a simple fallback response in Vietnamese
                    if not isinstance(schedule_result['schedule_text'], list) or len(schedule_result['schedule_text']) == 0:
                        # No classes case
                        enhanced_response = f"Xin chào, không có lớp học nào vào {schedule_result['date_info']}. Bạn có muốn kiểm tra ngày khác không?"
                    else:
                        # We have classes
                        if isinstance(schedule_result['schedule_text'], list):
                            num_classes = len(schedule_result['schedule_text'])
                            enhanced_response = f"Lịch học của bạn vào {schedule_result['date_info']} có {num_classes} lớp:\n\n{formatted_schedule}\n\nHãy đến lớp đúng giờ nhé!"
                        else:
                            enhanced_response = f"Lịch học của bạn vào {schedule_result['date_info']}:\n\n{formatted_schedule}\n\nHãy đến lớp đúng giờ nhé!"
                
                # Add the schedule information to the conversation history
                conversation_history.append({
                    "role": "system",
                    "content": schedule_result['schedule_text']
                })
                conversation_history.append({
                    "role": "assistant",
                    "content": enhanced_response
                })
                
                return jsonify({
                    'response': enhanced_response,
                    'schedule_data': schedule_result,
                    'conversation_history': conversation_history,
                    'query_type': 'schedule'
                })
                
            except Exception as e:
                error_msg = f"Error processing schedule: {str(e)}"
                logger.log_with_timestamp("SCHEDULE ERROR", error_msg)
                return jsonify({
                    'error': error_msg,
                    'schedule_data': None,
                    'conversation_history': conversation_history,
                    'query_type': 'schedule'
                }), 500
        
        # If education-related (but not schedule), proceed with normal processing
        system_message = {
            "role": "system",
            "content": (
                "You are a dedicated study assistant for university students in Vietnam. "
                "Your role includes:\n\n"
                "1. Supporting academic success and engagement\n"
                "2. Providing motivation when students feel like skipping classes\n"
                "3. Helping students understand the importance of attendance\n"
                "4. Offering constructive advice for academic challenges\n"
                "5. Suggesting strategies to maintain focus and motivation\n\n"
                f"The student's query was classified as: {classification_result['category']}\n\n"
                "Keep responses focused, constructive, and supportive. "
                "Use examples and concrete steps when appropriate."
            )
        }
        
        # Add system message to the beginning of the conversation history
        enhanced_history = [system_message]
        if conversation_history:
            enhanced_history.extend(conversation_history)
        
        # Log the AI request
        logger.log_with_timestamp(
            "AI REQUEST", 
            message, 
            f"Query type: {classification_result['category']} | History length: {len(conversation_history)} messages"
        )
        
        # Record start time
        start_time = time.time()
        
        # Get response from AI service
        response, updated_history = ai_service.chat_with_ai(message, enhanced_history)
        
        # Calculate response time
        time_taken = round(time.time() - start_time, 2)
        
        # Log the AI response with timing
        logger.log_with_timestamp(
            "AI RESPONSE", 
            response, 
            f"Time: {time_taken}s"
        )
        
        return jsonify({
            'response': response, 
            'conversation_history': updated_history,
            'query_type': classification_result['category']
        })
        
    except Exception as e:
        error_message = str(e)
        logger.log_with_timestamp("ERROR", error_message)
        print(f"Error in chat endpoint: {e}")
        return jsonify({'error': error_message}), 500