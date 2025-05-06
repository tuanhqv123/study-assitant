from unidecode import unidecode
from ..services.ai_service import AiService
from datetime import datetime, timedelta
import calendar

class QueryClassifier:
    def __init__(self):
        self.ai_service = AiService()
        self.today = datetime.now().date()
        self.categories = [
            'schedule',    # Lịch học, thời khóa biểu
            'grades',      # Điểm số, kết quả học tập
            'courses',     # Môn học, tài liệu, giảng viên
            'career',      # Nghề nghiệp, việc làm
            'general',     # Tư vấn học tập chung
            'other',       # Không liên quan đến học tập
            'date_query',  # Truy vấn về ngày cụ thể
            'uml'          # UML/PlantUML queries
        ]

    def normalize_vietnamese(self, text):
        """Convert text with diacritics to non-diacritic form and remove special characters"""
        return unidecode(text).lower()

    def classify_query(self, text):
        """
        Classify the input query using both keyword-based and AI-based methods
        Returns: (category, confidence, method)
        """
        if not text or text.strip() == '':
            return {
                'category': 'general',
                'confidence': 0.5,
                'method': 'empty-input'
            }
        
        # Detect UML/PlantUML queries first
        text_lower = text.lower()
        text_normalized = self.normalize_vietnamese(text_lower)
        if 'uml' in text_lower or 'plantuml' in text_lower:
            return {
                'category': 'uml',
                'confidence': 0.95,
                'method': 'keyword'
            }
        
        # Check if it's a date query first
        is_date, date_info = self.is_date_query(text)
        if is_date:
            return {
                'category': 'date_query',
                'confidence': 0.95,
                'method': 'keyword',
                'keyword': date_info.get('keyword', ''),
                'date_info': date_info
            }
            
        # Then try schedule-related classification (faster)
        is_schedule, keyword = self.is_schedule_related(text)
        if is_schedule:
            return {
                'category': 'schedule',
                'confidence': 0.9,
                'method': 'keyword',
                'keyword': keyword
            }

        # If not clearly schedule-related by keywords, use AI classification
        return self.classify_with_ai(text)

    def is_schedule_related(self, text):
        """
        Check if the text is related to schedule queries
        Returns: (bool, matched_keyword)
        """
        # Convert to lowercase and normalize
        text_normalized = self.normalize_vietnamese(text.lower())
        text_lower = text.lower()

        # Define schedule related patterns in Vietnamese and English
        schedule_keywords = {
            'vn': [
                'lịch học', 'thời khóa biểu', 'lịch thi', 'khi nào học', 'tiết học', 
                'phòng học', 'khi nào thi', 'lịch', 'ngày thi', 'ca thi'
            ],
            'vn_no_accent': [
                'lich hoc', 'thoi khoa bieu', 'lich thi', 'khi nao hoc', 'tiet hoc',
                'phong hoc', 'khi nao thi', 'lich', 'ngay thi', 'ca thi'
            ],
            'en': [
                'schedule', 'timetable', 'class schedule', 'exam schedule', 'when is class',
                'classroom', 'when is exam', 'calendar', 'exam date', 'class time'
            ]
        }

        # Check Vietnamese with accents
        for keyword in schedule_keywords['vn']:
            if keyword in text_lower:
                return True, keyword
                
        # Check Vietnamese without accents
        for keyword in schedule_keywords['vn_no_accent']:
            if keyword in text_normalized:
                return True, keyword
        
        # Check English
        for keyword in schedule_keywords['en']:
            if keyword in text_normalized or keyword in text_lower:
                return True, keyword
        
        # Not schedule-related
        return False, None
        
    def is_date_query(self, text):
        """
        Check if the text is a query about a specific date or day of the week
        Returns: (bool, date_info)
        """
        # Log that we're checking for a date query
        print(f"Checking if '{text}' is a date query")
        
        # Convert to lowercase and normalize
        text_normalized = self.normalize_vietnamese(text.lower())
        text_lower = text.lower()
        
        # Get current date information
        today = self.today
        current_weekday = today.weekday()  # 0 = Monday, 6 = Sunday
        
        # Vietnamese weekday names (with and without accents)
        weekdays_vn = {
            'thứ hai': 0, 'thu hai': 0, 'thứ 2': 0, 'thu 2': 0,
            'thứ ba': 1, 'thu ba': 1, 'thứ 3': 1, 'thu 3': 1,
            'thứ tư': 2, 'thu tu': 2, 'thứ 4': 2, 'thu 4': 2,
            'thứ năm': 3, 'thu nam': 3, 'thứ 5': 3, 'thu 5': 3,
            'thứ sáu': 4, 'thu sau': 4, 'thứ 6': 4, 'thu 6': 4,
            'thứ bảy': 5, 'thu bay': 5, 'thứ 7': 5, 'thu 7': 5,
            'chủ nhật': 6, 'chu nhat': 6, 'cn': 6
        }
        
        # English weekday names
        weekdays_en = {
            'monday': 0, 'mon': 0,
            'tuesday': 1, 'tue': 1,
            'wednesday': 2, 'wed': 2,
            'thursday': 3, 'thu': 3,
            'friday': 4, 'fri': 4,
            'saturday': 5, 'sat': 5,
            'sunday': 6, 'sun': 6
        }
        
        # Time references in Vietnamese and English
        time_refs = {
            'hôm nay': 0, 'hom nay': 0, 'today': 0,
            'ngày mai': 1, 'ngay mai': 1, 'tomorrow': 1,
            'hôm qua': -1, 'hom qua': -1, 'yesterday': -1,
            'ngày kia': 2, 'ngay kia': 2, 'day after tomorrow': 2,
            'hôm kia': -2, 'hom kia': -2, 'day before yesterday': -2
        }
        
        # Week references in Vietnamese and English
        week_refs = {
            'tuần này': 'this_week', 'tuan nay': 'this_week', 'this week': 'this_week',
            'tuần sau': 'next_week', 'tuan sau': 'next_week', 'next week': 'next_week',
            'tuần trước': 'last_week', 'tuan truoc': 'last_week', 'last week': 'last_week',
            'tuần tới': 'next_week', 'tuan toi': 'next_week', 'coming week': 'next_week'
        }
        
        # Check for direct date references
        for ref, offset in time_refs.items():
            if ref in text_lower or ref in text_normalized:
                target_date = today + timedelta(days=offset)
                return True, {
                    'type': 'specific_date',
                    'date': target_date,
                    'keyword': ref,
                    'weekday': calendar.day_name[target_date.weekday()],
                    'weekday_vn': self.get_vietnamese_weekday(target_date.weekday()),
                    'date_str': target_date.strftime('%d/%m/%Y')
                }
        
        # Check for weekday references
        for day_name, day_index in {**weekdays_vn, **weekdays_en}.items():
            if day_name in text_lower or day_name in text_normalized:
                # Default to the current week
                days_ahead = day_index - current_weekday
                if days_ahead <= 0:  # If the day has passed this week, look at next week
                    days_ahead += 7
                
                # Check if it's for next week
                for next_week_ref in ['tuần sau', 'tuan sau', 'next week', 'tuần tới', 'tuan toi']:
                    if next_week_ref in text_lower or next_week_ref in text_normalized:
                        days_ahead += 7
                        break
                
                # Check if it's for last week
                for last_week_ref in ['tuần trước', 'tuan truoc', 'last week']:
                    if last_week_ref in text_lower or last_week_ref in text_normalized:
                        days_ahead -= 14  # Go back 2 weeks (7 days to get to this week's day, then 7 more for last week)
                        break
                
                target_date = today + timedelta(days=days_ahead)
                return True, {
                    'type': 'weekday',
                    'date': target_date,
                    'keyword': day_name,
                    'weekday': calendar.day_name[target_date.weekday()],
                    'weekday_vn': self.get_vietnamese_weekday(target_date.weekday()),
                    'date_str': target_date.strftime('%d/%m/%Y')
                }
        
        # Check for week references
        for week_ref, week_type in week_refs.items():
            if week_ref in text_lower or week_ref in text_normalized:
                # Calculate the start and end of the week
                if week_type == 'this_week':
                    # Start of current week (Monday)
                    start_of_week = today - timedelta(days=current_weekday)
                    end_of_week = start_of_week + timedelta(days=6)  # Sunday
                elif week_type == 'next_week':
                    # Start of next week
                    start_of_week = today - timedelta(days=current_weekday) + timedelta(days=7)
                    end_of_week = start_of_week + timedelta(days=6)
                elif week_type == 'last_week':
                    # Start of last week
                    start_of_week = today - timedelta(days=current_weekday) - timedelta(days=7)
                    end_of_week = start_of_week + timedelta(days=6)
                
                return True, {
                    'type': 'week',
                    'week_type': week_type,
                    'keyword': week_ref,
                    'start_date': start_of_week,
                    'end_date': end_of_week,
                    'start_date_str': start_of_week.strftime('%d/%m/%Y'),
                    'end_date_str': end_of_week.strftime('%d/%m/%Y')
                }
        
        return False, None
    
    def get_vietnamese_weekday(self, weekday_index):
        """
        Convert weekday index to Vietnamese weekday name
        0 = Monday, 6 = Sunday
        """
        weekday_names = {
            0: 'Thứ Hai',
            1: 'Thứ Ba',
            2: 'Thứ Tư',
            3: 'Thứ Năm',
            4: 'Thứ Sáu',
            5: 'Thứ Bảy',
            6: 'Chủ Nhật'
        }
        return weekday_names.get(weekday_index, '')

    def classify_with_ai(self, question):
        """
        Use AI to classify the question into categories:
        - schedule: questions about class schedules, timetables, exam dates
        - grades: questions about grades, GPA, academic performance
        - courses: questions about course content, materials, credits, subjects
        - career: questions about career advice and future planning
        - general: general academic advice or other topics
        - other: non-academic topics that should be rejected
        """
        # Create a system prompt for classification
        classification_prompt = {
            "role": "system", 
            "content": """
            You are a question classifier for an academic chatbot serving Vietnamese students. Your task is to categorize student questions into one of the following categories:

            1. schedule - Questions about class schedules, timetables, exam dates, classroom locations, or any time-related academic inquiries. This includes ANY mentions of classes in relation to time, even if the student expresses emotions about them.
            2. grades - Questions about academic performance, GPA, exam results, scores, or evaluation metrics
            3. courses - Questions about course content, materials, credits, textbooks, professors, or specific subjects
            4. career - Questions about future career paths, job prospects, professional development, or employment opportunities
            5. general - General academic advice that doesn't fit into the categories above, but is still related to education
            6. other - NON-ACADEMIC topics like relationships, politics, entertainment, personal advice, etc.

            IMPORTANT GUIDELINES:
            - If a query contains ANY mention of classes combined with time references (today, tomorrow, etc.), classify it as "schedule" even if the student expresses emotions about it.
            - Examples of "schedule" that MUST be classified correctly:
              * "I'm sad about my class tomorrow" → schedule (contains class + time reference)
              * "Don't want to attend the lecture today" → schedule (contains lecture + time reference)
              * "So tired of waking up for morning classes" → schedule (about class timing)
            
            - The "other" category is for questions that are NOT related to academics or education.
              * "Do you know about love?" → other
              * "What's the best movie to watch?" → other
              * "How's the weather today?" → other

            Respond with ONLY a JSON object with two fields:
            - "category": one of the category names (schedule, grades, courses, career, general, or other)
            - "confidence": a number between 0 and 1 indicating your confidence in the classification

            Example response:
            {"category": "schedule", "confidence": 0.95}
            """
        }
        
        try:
            # Send the classification request
            response, _ = self.ai_service.chat_with_ai(question, [classification_prompt])
            
            # Extract the JSON response - find the JSON part (between { and })
            import re
            import json
            
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                result = json.loads(json_str)
                
                # Add method information
                result['method'] = 'ai'
                return result
            else:
                # If JSON parsing fails, fall back to simple text-based analysis
                if 'schedule' in response.lower():
                    return {'category': 'schedule', 'confidence': 0.7, 'method': 'ai-text'}
                elif 'grades' in response.lower():
                    return {'category': 'grades', 'confidence': 0.7, 'method': 'ai-text'}
                elif 'courses' in response.lower():
                    return {'category': 'courses', 'confidence': 0.7, 'method': 'ai-text'}
                elif 'career' in response.lower():
                    return {'category': 'career', 'confidence': 0.7, 'method': 'ai-text'}
                elif 'other' in response.lower():
                    return {'category': 'other', 'confidence': 0.7, 'method': 'ai-text'}
                else:
                    return {'category': 'general', 'confidence': 0.5, 'method': 'ai-fallback'}
        
        except Exception as e:
            # Fallback to a basic categorization
            print(f"Error in AI classification: {str(e)}")
            return {'category': 'general', 'confidence': 0.3, 'method': f'error: {str(e)}'}

    def is_academic_topic(self, question):
        """
        Check if the question is related to academic topics.
        Returns True for academic topics, False for non-academic topics.
        """
        # Convert to lowercase and normalize for better matching
        question_lower = question.lower()
        question_normalized = self.normalize_vietnamese(question_lower)
        
        # Define non-academic topics to filter out
        non_academic_topics = {
            'vn': [
                'tình yêu', 'hẹn hò', 'yêu đương', 'tình cảm', 'người yêu', 
                'chính trị', 'đảng', 'chính phủ', 'bầu cử',
                'trò chơi', 'game', 'phim ảnh', 'ca nhạc', 'giải trí',
                'tôn giáo', 'thần linh', 'chúa', 'phật',
                'sức khỏe', 'bệnh tật', 'thuốc', 'khám bệnh',
                'tiền bạc', 'đầu tư', 'chứng khoán', 'tiền mã hóa',
                'cờ bạc', 'cá cược', 'xổ số'
            ],
            'vn_no_accent': [
                'tinh yeu', 'hen ho', 'yeu duong', 'tinh cam', 'nguoi yeu',
                'chinh tri', 'dang', 'chinh phu', 'bau cu',
                'tro choi', 'game', 'phim anh', 'ca nhac', 'giai tri',
                'ton giao', 'than linh', 'chua', 'phat',
                'suc khoe', 'benh tat', 'thuoc', 'kham benh',
                'tien bac', 'dau tu', 'chung khoan', 'tien ma hoa',
                'co bac', 'ca cuoc', 'xo so'
            ],
            'en': [
                'love', 'dating', 'relationship', 'girlfriend', 'boyfriend',
                'politics', 'government', 'election', 'party',
                'game', 'movie', 'music', 'entertainment',
                'religion', 'god', 'spiritual',
                'health', 'disease', 'medicine', 'doctor',
                'money', 'investment', 'stock', 'crypto',
                'gambling', 'betting', 'lottery'
            ]
        }
        
        # Check if question contains non-academic topics
        for category in non_academic_topics.values():
            for keyword in category:
                if keyword in question_normalized or keyword in question_lower:
                    return False
        
        return True