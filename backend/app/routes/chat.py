from flask import Blueprint, request, jsonify
from ..services.ai_service import AiService
from ..services.query_classifier import QueryClassifier
from ..services.schedule_service import ScheduleService
from ..services.ptit_auth_service import PTITAuthService
from ..utils.logger import Logger
from ..lib.supabase import supabase
import time
from datetime import datetime
import json

chat_bp = Blueprint('chat', __name__)
ai_service = AiService()
logger = Logger()
query_classifier = QueryClassifier()
schedule_service = ScheduleService()
ptit_auth_service = PTITAuthService()

# Initialize schedule service with auth service
schedule_service.set_auth_service(ptit_auth_service)

@chat_bp.route('/chat', methods=['POST'])
async def chat():
    try:
        data = request.json
        message = data.get('message')
        conversation_history = data.get('conversation_history', [])
        
        if not message:
            return jsonify({'error': 'No message provided', 'response': None}), 400

        # Log user message
        logger.log_with_timestamp("USER INPUT", message, f"Message length: {len(message)} chars")
        
        # Use the QueryClassifier to classify the message
        classification_result = query_classifier.classify_query(message)
        
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
        if classification_result['category'] == 'schedule':
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
                date_info_value = date_info_tuple[0]  # Get the actual date value (can be a date or a tuple of dates)
                
                # Handle date formatting differently depending on whether it's a single date or date range
                if isinstance(date_info_value, tuple):  # It's a date range
                    start_date, end_date = date_info_value
                    formatted_date_info = f"{start_date.strftime('%d/%m/%Y')} to {end_date.strftime('%d/%m/%Y')}"
                    # Get schedule for the first day
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
                schedule_prompt = {
                    "role": "system",
                    "content": f"""
                    You are a helpful study assistant. The student asked about their schedule.
                    Here is the schedule information retrieved from the system:

                    {schedule_result['schedule_text']}

                    Please respond in Vietnamese, summarizing this information in a natural, 
                    conversational way. Mention the date and add any relevant reminders 
                    about being on time for classes. Keep your response concise and friendly.
                    """
                }
                
                # Get AI to format the response nicely
                enhanced_response, _ = ai_service.chat_with_ai(
                    message, 
                    [schedule_prompt]
                )
                
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