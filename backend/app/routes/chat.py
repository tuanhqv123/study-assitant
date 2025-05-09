from flask import Blueprint, request, jsonify
from ..services.ai_service import AiService
from ..services.query_classifier import QueryClassifier
from ..services.schedule_service import ScheduleService
from ..services.exam_schedule_service import ExamScheduleService
from ..services.ptit_auth_service import PTITAuthService
from ..utils.logger import Logger
from ..lib.supabase import supabase
import time
from datetime import datetime, timedelta
import json
from ..config.agents import get_agent, get_all_agents

chat_bp = Blueprint('chat', __name__)
ai_service = AiService()
logger = Logger()
query_classifier = QueryClassifier()
schedule_service = ScheduleService()
exam_schedule_service = ExamScheduleService()
ptit_auth_service = PTITAuthService()

# Initialize services with auth service and AI service
schedule_service.set_auth_service(ptit_auth_service)
schedule_service.set_ai_service(ai_service)
exam_schedule_service.set_auth_service(ptit_auth_service)
# Set the schedule_service in the exam_schedule_service for date extraction
exam_schedule_service.set_schedule_service(schedule_service)

@chat_bp.route('/agents', methods=['GET'])
def get_agents():
    """
    Get the list of available agents.
    
    Returns:
        JSON response with list of available agents.
    """
    agents = get_all_agents()
    return jsonify({'agents': agents})

@chat_bp.route('/chat', methods=['POST'])
async def chat():
    try:
        data = request.json
        file_id = data.get('file_id')  # handle file context
        message = data.get('message')
        conversation_history = data.get('conversation_history', [])
        agent_id = data.get('agent_id')  # Get agent_id from request
        web_search_enabled = data.get('web_search_enabled', False)  # Get web search flag
        
        # Log which agent is being used
        if agent_id:
            agent = get_agent(agent_id)
            logger.log_with_timestamp(
                "AGENT SELECTION",
                f"Using agent: {agent['display_name']}",
                f"Model: {agent['model']}"
            )
        
        # Handle file context
        if file_id:
            # use file context handler
            response, updated_history = await ai_service.chat_with_file_context(
                message, file_id, conversation_history, agent_id
            )
            return jsonify({
                'response': response,
                'conversation_history': updated_history,
                'file_context_active': True,
                'file_id': file_id,
                'agent_id': agent_id
            })
        
        if not message:
            return jsonify({'error': 'No message provided', 'response': None}), 400

        # Log user message
        logger.log_with_timestamp("USER INPUT", message, f"Message length: {len(message)} chars")
        
        # Check if web search is enabled
        if web_search_enabled:
            logger.log_with_timestamp("WEB_SEARCH_ENABLED", "Using web search for query", "")
            
            # Get chat_id from request
            chat_id = data.get('chat_id')
            
            # Log chat session info with more details
            if chat_id:
                logger.log_with_timestamp("CHAT_SESSION", f"Using chat session: {chat_id}")
            else:
                logger.log_with_timestamp("CHAT_SESSION_WARNING", "No chat_id provided, messages won't be saved to database", f"Request data keys: {list(data.keys())}")
                # Check all the data received to debug
                logger.log_with_timestamp("REQUEST_DATA", f"Request data: {json.dumps(data, default=str)[:500]}")
            
            # Call AI service with web search
            logger.log_with_timestamp("WEB_SEARCH_CALL", "Calling AI service with web search")
            web_response, updated_history = await ai_service.chat_with_web_search(
                message, conversation_history, agent_id, chat_id
            )
            
            # Log the response format for debugging
            logger.log_with_timestamp("WEB_SEARCH_RESPONSE", 
                                   f"Response type: {type(web_response)}, Keys: {list(web_response.keys()) if isinstance(web_response, dict) else 'Not a dict'}")
                                   
            # Log sources count and format
            if isinstance(web_response, dict) and 'sources' in web_response:
                sources = web_response.get('sources', [])
                logger.log_with_timestamp("WEB_SEARCH_SOURCES", 
                                       f"Returning {len(sources)} sources to frontend")
                if sources and len(sources) > 0:
                    logger.log_with_timestamp("FIRST_SOURCE_FORMAT", 
                                           f"First source format: {json.dumps(sources[0]) if sources else 'None'}")
            
            # Prepare response for frontend
            response_data = {
                'response': web_response['content'] if isinstance(web_response, dict) else web_response,
                'sources': web_response.get('sources', []) if isinstance(web_response, dict) else [],
                'web_search_results': True,
                'conversation_history': updated_history,
                'query_type': 'web_search',
                'agent_id': agent_id,
                'chat_id': chat_id  # Echo back the chat_id for client reference
            }
            
            logger.log_with_timestamp("WEB_SEARCH_COMPLETE", "Web search complete, returning response")
            return jsonify(response_data)
        
        # Regular flow continues if web search is not enabled
        # Use the QueryClassifier to classify the message
        classification_result = query_classifier.classify_query(message)

        # Handle UML/PlantUML diagram requests
        if classification_result.get('category') == 'uml':
            uml_prompt = {
                "role": "system",
                "content": (
                    "You are a professional programming assistant. When returning the UML diagram,"
                    "Always cover the Plantuml codes in the code block using the three -point sign and tag` plantuml`, "
                    "For example:` `` Plantuml ... `` `` Frontend can display images. "
                    "Without further explanation, only export the UML diagram."
                )
            }
            # Get response from AI - REMOVE await since chat_with_ai is not async
            response, updated_history = ai_service.chat_with_ai(
                message,
                [uml_prompt],
                agent_id
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
                'query_type': 'uml',
                'agent_id': agent_id
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
                'query_type': 'other',
                'agent_id': agent_id
            })
        
        # Handle schedule-related queries with date extraction
        if classification_result['category'] == 'schedule' or classification_result['category'] == 'date_query':
            # Log that we're handling a schedule/date query
            logger.log_with_timestamp(
                "DATE QUERY", 
                f"Processing date query", 
                f"Query type: {classification_result['category']}"
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
                
                # Process both class schedule and exam schedule for the same date
                # First, process class schedule
                schedule_result = await schedule_service.get_schedule_by_semester(current_semester['hoc_ky'])
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
                
                # Log the extracted date information
                if isinstance(date_info_value, tuple):
                    start_date, end_date = date_info_value
                    logger.log_with_timestamp(
                        "DATE EXTRACTION", 
                        f"Date range: {start_date.strftime('%d/%m/%Y')} to {end_date.strftime('%d/%m/%Y')}",
                        f"Type: {date_info_tuple[1]}"
                    )
                    formatted_date_info = f"{start_date.strftime('%d/%m/%Y')} to {end_date.strftime('%d/%m/%Y')}"
                    
                    # For ranges, we'll focus on class schedule and not exam schedule
                    # (exam schedules are usually more relevant for specific dates)
                    if date_info_tuple[1] in ['this_week', 'next_week', 'last_week', 'specific_week']:
                        all_classes = []
                        days_in_range = (end_date - start_date).days + 1
                        days_to_fetch = min(days_in_range, 7)  # Limit to 7 days for week queries
                        
                        # Check each day in the range for classes
                        for i in range(days_to_fetch):
                            current_date = start_date + timedelta(days=i)
                            daily_classes = schedule_service.get_class_schedule(schedule_result, current_date)
                            if daily_classes:
                                for class_info in daily_classes:
                                    # Add date information to each class
                                    class_info['date'] = current_date.strftime('%d/%m/%Y')
                                    class_info['day_of_week'] = current_date.strftime('%A')
                                    all_classes.append(class_info)
                        
                        schedule_text = all_classes
                        
                        # Also get exam schedules for the date range
                        logger.log_with_timestamp(
                            "EXAM SCHEDULE", 
                            f"Getting exam schedules for week: {start_date.strftime('%d/%m/%Y')} to {end_date.strftime('%d/%m/%Y')}"
                        )
                        
                        # Get exam data for the date range
                        exam_data = await exam_schedule_service.get_exam_schedule_by_semester(current_semester['hoc_ky'], False)
                        exams_in_range = exam_schedule_service.get_exams_by_date_range(exam_data, start_date, end_date)
                        exam_text = exam_schedule_service.format_exam_schedule(exams_in_range) if exams_in_range else None
                        exam_count = len(exams_in_range)
                        
                        logger.log_with_timestamp(
                            "EXAM SCHEDULE", 
                            f"Found {exam_count} exams in the week"
                        )
                    else:
                        # For other date ranges, just get the first day
                        schedule_text = schedule_service.get_class_schedule(schedule_result, start_date)
                        
                        # Also get exam schedule for the start date
                        date_str = start_date.strftime('%d/%m/%Y')
                        exam_data = await exam_schedule_service.get_exam_schedule_by_semester(current_semester['hoc_ky'], False)
                        exams_on_date = exam_schedule_service.get_exams_by_date(exam_data, date_str)
                        exam_text = exam_schedule_service.format_exam_schedule(exams_on_date) if exams_on_date else None
                        exam_count = len(exams_on_date)
                else:  # It's a single date
                    formatted_date_info = date_info_value.strftime('%d/%m/%Y')
                    logger.log_with_timestamp(
                        "DATE EXTRACTION", 
                        f"Single date: {formatted_date_info}",
                        f"Type: {date_info_tuple[1]}"
                    )
                    
                    # Get class schedule for the date
                    schedule_text = schedule_service.get_class_schedule(schedule_result, date_info_value)
                    
                    # Also get exam schedule for the same date
                    date_str = date_info_value.strftime('%d/%m/%Y')
                    exam_data = await exam_schedule_service.get_exam_schedule_by_semester(current_semester['hoc_ky'], False)
                    exams_on_date = exam_schedule_service.get_exams_by_date(exam_data, date_str)
                    exam_text = exam_schedule_service.format_exam_schedule(exams_on_date) if exams_on_date else None
                    exam_count = len(exams_on_date)
                
                schedule_result = {
                    'date_info': formatted_date_info,
                    'date_type': date_info_tuple[1],
                    'original_text': date_info_tuple[2],
                    'schedule_text': schedule_text,
                    'exam_text': exam_text,
                    'exam_count': exam_count
                }
                
                # Log the processing result (reduced verbosity)
                logger.log_with_timestamp(
                    "SCHEDULE RESULT", 
                    f"Date: {schedule_result['date_info']} | Additional info: Type: {schedule_result['date_type']} | Original text: {schedule_result['original_text']}"
                )
                
                # Format the schedule data for display
                has_classes = isinstance(schedule_result['schedule_text'], list) and len(schedule_result['schedule_text']) > 0
                has_exams = exam_count > 0
                
                if not has_classes and not has_exams:
                    # No classes or exams found for this date
                    if date_info_tuple[2] == 'default':
                        # User didn't specify a date clearly
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
                        # We understood the date, but nothing was found
                        # Get friendly date representation
                        if isinstance(date_info_value, tuple):
                            date_repr = f"từ {formatted_date_info}"
                        else:
                            weekday_vn = schedule_service.get_vietnamese_weekday(date_info_value.weekday())
                            date_repr = f"{weekday_vn}, ngày {formatted_date_info}"
                        
                        schedule_prompt = {
                            "role": "system",
                            "content": f"""
                            You are a helpful study assistant. The student asked about their schedule for {date_repr}.
                            After checking the system, no classes or exams were found for this date.
                            
                            Please respond in Vietnamese, letting them know there are no classes or exams scheduled for {date_repr}.
                            Offer to check another date if they'd like. Be helpful and friendly in your response.
                            """
                        }
                else:
                    # We have schedule and/or exam data to share
                    # Format schedule data
                    formatted_schedule = ""
                    if has_classes:
                        # Format class schedule
                        if isinstance(schedule_result['schedule_text'], list):
                            for i, class_info in enumerate(schedule_result['schedule_text'], 1):
                                # Add class details
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

                                # Add class date and thu_kieu_so
                                formatted_schedule += f"    Ngày học: {class_info.get('ngay_hoc', '')}\n"
                                thu_kieu_so = class_info.get('thu_kieu_so', '')
                                if thu_kieu_so:
                                    formatted_schedule += f"    Thứ {thu_kieu_so}\n"
                                    
                                formatted_schedule += "\n"
                    
                    # Prepare combined prompt with both schedule and exam info
                    combined_data = ""
                    
                    if has_classes:
                        combined_data += "LỊCH HỌC:\n" + formatted_schedule + "\n"
                    
                    if has_exams:
                        combined_data += "LỊCH THI:\n" + schedule_result['exam_text']
                    
                    if not combined_data.strip():
                        combined_data = "Không tìm thấy thông tin lớp học hoặc lịch thi cho ngày này."
                    
                    schedule_prompt = {
                        "role": "system",
                        "content": f"""
                        You are a helpful study assistant. The student asked about their schedule.
                        Here is the schedule information retrieved from the system:

                        {combined_data}

                        Please respond in Vietnamese, summarizing this information in a natural, 
                        conversational way. Mention the date and add any relevant reminders 
                        about being on time for classes or exams. 
                        
                        If there are both classes and exams, make sure to clearly distinguish between them.
                        If there are exams, emphasize their importance and suggest preparing well in advance.
                        
                        Keep your response concise and friendly.
                        """
                    }
                
                # Get AI to format the response nicely
                try:
                    enhanced_response, _ = ai_service.chat_with_ai(
                        message, 
                        [schedule_prompt],
                        agent_id
                    )
                except Exception as ai_error:
                    # Log the error and generate fallback response
                    logger.log_with_timestamp("SCHEDULE AI ERROR", f"Failed to get AI response: {str(ai_error)}")
                    
                    # Generate a simple fallback response
                    if not has_classes and not has_exams:
                        enhanced_response = f"Xin chào, không có lớp học hay lịch thi nào vào {formatted_date_info}. Bạn có muốn kiểm tra ngày khác không?"
                    else:
                        enhanced_response = f"Lịch của bạn vào {formatted_date_info}:\n\n{combined_data}\n\nHãy chuẩn bị thật kỹ và đến đúng giờ nhé!"
                
                # Add the information to the conversation history
                conversation_history.append({
                    "role": "system",
                    "content": f"Schedule data: {schedule_result.get('schedule_text')}\nExam data: {schedule_result.get('exam_text')}"
                })
                conversation_history.append({
                    "role": "assistant",
                    "content": enhanced_response
                })
                
                return jsonify({
                    'response': enhanced_response,
                    'schedule_data': schedule_result,
                    'conversation_history': conversation_history,
                    'query_type': 'schedule',
                    'agent_id': agent_id
                })
                
            except Exception as e:
                error_msg = f"Error processing schedule/exam data: {str(e)}"
                logger.log_with_timestamp("SCHEDULE ERROR", error_msg)
                return jsonify({
                    'error': error_msg,
                    'schedule_data': None,
                    'conversation_history': conversation_history,
                    'query_type': 'schedule',
                    'agent_id': agent_id
                }), 500
        
        # Handle exam schedule queries
        if classification_result['category'] == 'examschedule':
            # Log that we're handling an exam schedule query
            logger.log_with_timestamp(
                "EXAM SCHEDULE QUERY", 
                f"Processing exam schedule request", 
                f"Current time: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
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
                
                # Process the exam schedule query
                exam_result = await exam_schedule_service.process_exam_query(
                    message, 
                    current_semester['hoc_ky'],
                    False  # Not midterm by default, could be made configurable
                )
                
                # Log the exam processing result
                logger.log_with_timestamp(
                    "EXAM SCHEDULE RESULT", 
                    f"Filter: {exam_result['filter_type']} = {exam_result['filter_value']}",
                    f"Found {exam_result['exam_count']} exams"
                )
                
                # Create a contextualized response using AI
                if exam_result['exam_count'] == 0:
                    # No exams found
                    exam_prompt = {
                        "role": "system",
                        "content": f"""
                        You are a helpful study assistant. The student asked about their exam schedule.
                        After checking the system, no exams were found matching their query: "{message}"
                        
                        Please respond in Vietnamese, letting them know no exams were found matching their criteria.
                        If their query was for a specific date or date range ({exam_result['filter_value']}), 
                        mention that time period in your response.
                        Offer to check another date or subject if they'd like. Be helpful and friendly in your response.
                        """
                    }
                else:
                    # We have exam data to share
                    # If it's a date range query, include that information
                    date_info = ""
                    week_context = ""
                    if exam_result['filter_type'] == "date_range":
                        date_info = f"cho khoảng thời gian {exam_result['filter_value']}"
                        
                        # Add additional context for week-based queries
                        if "to" in exam_result['filter_value']:
                            week_context = "Đây là danh sách tất cả các kỳ thi trong khoảng thời gian này. "
                    elif exam_result['filter_type'] == "date":
                        date_info = f"cho ngày {exam_result['filter_value']}"
                    
                    exam_prompt = {
                        "role": "system",
                        "content": f"""
                        You are a helpful study assistant. The student asked about their exam schedule.
                        Here is the exam information retrieved from the system {date_info}:

                        {exam_result['exam_text']}

                        {week_context}Please respond in Vietnamese, summarizing this information in a natural, 
                        conversational way. Mention the date or date range if provided, along with any upcoming exams,
                        their format, location and time.
                        Add any relevant reminders about being prepared for exams.
                        Keep your response concise and friendly.
                        """
                    }
                
                logger.log_with_timestamp("EXAM SCHEDULE PROMPT", exam_prompt['content'])
                
                # Get AI to format the response nicely
                try:
                    enhanced_response, _ = ai_service.chat_with_ai(
                        message, 
                        [exam_prompt],
                        agent_id
                    )
                except Exception as ai_error:
                    # Log the error
                    logger.log_with_timestamp("EXAM SCHEDULE AI ERROR", f"Failed to get AI response: {str(ai_error)}")
                    
                    # Generate a simple fallback response in Vietnamese
                    if exam_result['exam_count'] == 0:
                        enhanced_response = "Xin chào, không tìm thấy lịch thi nào phù hợp với yêu cầu của bạn. Bạn có muốn tìm kiếm với thông tin khác không?"
                    else:
                        enhanced_response = f"Lịch thi của bạn:\n\n{exam_result['exam_text']}\n\nHãy chuẩn bị thật kỹ và đến đúng giờ nhé!"
                
                # Add the exam information to the conversation history
                conversation_history.append({
                    "role": "system",
                    "content": exam_result['exam_text']
                })
                conversation_history.append({
                    "role": "assistant",
                    "content": enhanced_response
                })
                
                return jsonify({
                    'response': enhanced_response,
                    'exam_data': exam_result,
                    'conversation_history': conversation_history,
                    'query_type': 'examschedule',
                    'agent_id': agent_id
                })
                
            except Exception as e:
                error_msg = f"Error processing exam schedule: {str(e)}"
                logger.log_with_timestamp("EXAM SCHEDULE ERROR", error_msg)
                return jsonify({
                    'error': error_msg,
                    'exam_data': None,
                    'conversation_history': conversation_history,
                    'query_type': 'examschedule',
                    'agent_id': agent_id
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
        
        # Get response from AI service - pass the agent_id
        response, updated_history = ai_service.chat_with_ai(message, enhanced_history, agent_id)
        
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
            'query_type': classification_result['category'],
            'agent_id': agent_id
        })
        
    except Exception as e:
        error_message = str(e)
        logger.log_with_timestamp("ERROR", error_message)
        print(f"Error in chat endpoint: {e}")
        return jsonify({'error': error_message}), 500

@chat_bp.route('/chat/messages', methods=['GET'])
async def get_chat_messages():
    """
    Endpoint to get messages for a specific chat session.
    This is useful for debugging and verifying that messages are properly saved.
    
    Query parameters:
        chat_id: UUID of the chat session
        
    Returns:
        JSON response with messages from the specified chat session
    """
    try:
        chat_id = request.args.get('chat_id')
        
        if not chat_id:
            return jsonify({'error': 'Missing chat_id parameter'}), 400
            
        logger.log_with_timestamp("GET_MESSAGES", f"Fetching messages for chat: {chat_id}")
        
        # Query the database for messages
        result = supabase.table('messages') \
                        .select('*') \
                        .eq('chat_id', chat_id) \
                        .order('created_at') \
                        .execute()
                        
        # Format and return messages
        messages = []
        if result and hasattr(result, 'data'):
            messages = result.data
            # Log what we found
            logger.log_with_timestamp("GET_MESSAGES", f"Found {len(messages)} messages")
            
            # Check for messages with sources
            messages_with_sources = [msg for msg in messages if msg.get('sources')]
            if messages_with_sources:
                logger.log_with_timestamp("SOURCES_FOUND", f"Found {len(messages_with_sources)} messages with sources")
            
        return jsonify({
            'chat_id': chat_id,
            'messages': messages,
            'count': len(messages)
        })
        
    except Exception as e:
        error_message = str(e)
        logger.log_with_timestamp("ERROR", f"Error fetching messages: {error_message}")
        return jsonify({'error': error_message}), 500