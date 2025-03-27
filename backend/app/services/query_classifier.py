from unidecode import unidecode
from ..services.ai_service import AiService

class QueryClassifier:
    def __init__(self):
        self.ai_service = AiService()
        self.categories = [
            'schedule',    # Lịch học, thời khóa biểu
            'grades',      # Điểm số, kết quả học tập
            'courses',     # Môn học, tài liệu, giảng viên
            'career',      # Nghề nghiệp, việc làm
            'general',     # Tư vấn học tập chung
            'other'        # Không liên quan đến học tập
        ]

    def normalize_vietnamese(self, text):
        """Convert text with diacritics to non-diacritic form and remove special characters"""
        return unidecode(text).lower()

    def classify_query(self, text):
        """
        Classify the input query using both keyword-based and AI-based methods
        Returns: (category, confidence, method)
        """
        # First try keyword-based classification (faster)
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
            if keyword in text_normalized:
                return True, keyword

        return False, None

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