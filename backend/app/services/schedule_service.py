from datetime import datetime, timedelta
import calendar
import re
import httpx
from unidecode import unidecode
from ..utils.logger import Logger

logger = Logger()

class ScheduleService:
    def __init__(self, auth_service=None, ai_service=None):
        self.today = datetime.now().date()
        self.base_url = "https://uis.ptithcm.edu.vn/api/sch"
        self.auth_service = auth_service
        self.ai_service = ai_service
        self.time_analyzer = None
        
        # Initialize time analyzer if AI service is provided
        if ai_service:
            from .time_analyzer import TimeAnalyzer
            self.time_analyzer = TimeAnalyzer(ai_service)

    def set_auth_service(self, auth_service):
        """Set the authentication service for token management

        Args:
            auth_service (PTITAuthService): The authentication service instance
        """
        self.auth_service = auth_service
        
    def set_ai_service(self, ai_service):
        """Set the AI service for time analysis
        
        Args:
            ai_service (AiService): The AI service instance
        """
        self.ai_service = ai_service
        
        # Initialize or update time analyzer
        if self.ai_service:
            from .time_analyzer import TimeAnalyzer
            self.time_analyzer = TimeAnalyzer(self.ai_service)
        
    def check_auth(self):
        """Check if the service is properly authenticated

        Returns:
            bool: True if authenticated, False otherwise
        """
        return self.auth_service is not None and self.auth_service.access_token is not None
        
    def extract_date_references(self, question):
        """
        Extract date references from a question like "today", "tomorrow", "next Monday", etc.
        Returns a tuple of (referenced_date, date_type, original_text)
        
        This method now uses AI-based time analysis if available, falling back to regex patterns
        if AI service is not configured.
        """
        # Use AI-based time analyzer if available
        if self.time_analyzer and self.ai_service:
            logger.log_with_timestamp("SCHEDULE API", "Using AI-based time analysis")
            time_analysis_result = self.time_analyzer.analyze_time_references(question)
            # Check if the time analyzer returned a valid result
            if time_analysis_result is not None:
                return time_analysis_result
            else:
                # If time analyzer returns None, log it and fall back to regex
                logger.log_with_timestamp("SCHEDULE API", "AI-based time analysis returned None, falling back to regex")
        
        # Fallback to regex-based analysis if AI service is not available
        logger.log_with_timestamp("SCHEDULE API", "Falling back to regex-based time analysis")
        
        # Convert to lowercase và normalize (bỏ dấu)
        question_normalized = self.normalize_vietnamese(question.lower())
        question_lower = question.lower()
        
        # Chỉ cần pattern không dấu cho tuần có ngày/tháng/năm
        week_with_full_date_patterns = [
            r"tuan.*ngay[\s:]*([0-9]{1,2})[/-]([0-9]{1,2})(?:[/-]([0-9]{4}))?",  # tuan ... ngay DD/MM(/YYYY)
            r"tuan[\s:]*([0-9]{1,2})[/-]([0-9]{1,2})(?:[/-]([0-9]{4}))?",         # tuan DD/MM(/YYYY)
            r"tuan[\s:]*([0-9]{1,2}) thang[\s:]*([0-9]{1,2})(?: nam[\s:]*([0-9]{4}))?"  # tuan 21 thang 4 (nam 2025)
        ]
        for pattern in week_with_full_date_patterns:
            matches = re.search(pattern, question_normalized)
            if matches:
                day = int(matches.group(1))
                month = int(matches.group(2)) if matches.lastindex >= 2 and matches.group(2) else self.today.month
                year = int(matches.group(3)) if matches.lastindex >= 3 and matches.group(3) else self.today.year
                try:
                    target_date = datetime(year, month, day).date()
                except ValueError:
                    continue
                start_of_week = target_date - timedelta(days=target_date.weekday())
                end_of_week = start_of_week + timedelta(days=6)
                return ((start_of_week, end_of_week), 'specific_week', matches.group(0))

        # Chỉ cần pattern không dấu cho tuần có ngày
        week_with_date_patterns = [
            r'tuan co ngay (\d{1,2})',  # tuan co ngay DD
            r'tuan.*ngay (\d{1,2})'     # tuan ... ngay DD
        ]
        for pattern in week_with_date_patterns:
            matches = re.search(pattern, question_normalized)
            if matches:
                day = int(matches.group(1))
                target_date = None
                try:
                    target_date = datetime(self.today.year, self.today.month, day).date()
                    if target_date < self.today and day < 15:
                        next_month = self.today.month + 1 if self.today.month < 12 else 1
                        next_year = self.today.year if self.today.month < 12 else self.today.year + 1
                        target_date = datetime(next_year, next_month, day).date()
                except ValueError:
                    try:
                        next_month = self.today.month + 1 if self.today.month < 12 else 1
                        next_year = self.today.year if self.today.month < 12 else self.today.year + 1
                        target_date = datetime(next_year, next_month, day).date()
                    except ValueError:
                        continue
                if target_date:
                    start_of_week = target_date - timedelta(days=target_date.weekday())
                    end_of_week = start_of_week + timedelta(days=6)
                    return ((start_of_week, end_of_week), 'specific_week', matches.group(0))
        
        # Define date reference patterns in Vietnamese and English
        date_patterns = {
            # Today references
            'today': ['hôm nay', 'ngày hôm nay', 'ngay hom nay', 'today', 'this day', 'hnay'],
            # Tomorrow references
            'tomorrow': ['ngày mai', 'mai', 'tomorrow', 'ngay mai', 'hôm sau', 'hom sau'],
            # Yesterday references 
            'yesterday': ['hôm qua', 'hom qua', 'yesterday', 'qua'],
            # Day after tomorrow
            'day_after_tomorrow': ['ngày kia', 'ngay kia', 'kia', 'ngày mốt', 'ngay mot', 'mốt', 'mot'],
            # This week
            'this_week': ['tuần này', 'tuan nay', 'this week', 'trong tuần'],
            # Next week
            'next_week': ['tuần sau', 'tuần tới', 'tuan sau', 'tuan toi', 'next week'],
            # This month
            'this_month': ['tháng này', 'thang nay', 'this month'],
            # Specific weekdays
            'monday': ['thứ hai', 'thu 2', 'thu hai', 'monday', 't2'],
            'tuesday': ['thứ ba', 'thu 3', 'thu ba', 'tuesday', 't3'],
            'wednesday': ['thứ tư', 'thu 4', 'thu tu', 'wednesday', 't4'],
            'thursday': ['thứ năm', 'thu 5', 'thu nam', 'thursday', 't5'],
            'friday': ['thứ sáu', 'thu 6', 'thu sau', 'friday', 't6'],
            'saturday': ['thứ bảy', 'thu 7', 'thu bay', 'saturday', 't7'],
            'sunday': ['chủ nhật', 'chu nhat', 'sunday', 'cn']
        }
        
        # Check for date references
        for date_type, patterns in date_patterns.items():
            for pattern in patterns:
                if pattern in question_normalized or pattern in question_lower:
                    # Calculate the referenced date
                    if date_type == 'today':
                        return (self.today, 'today', pattern)
                    elif date_type == 'tomorrow':
                        return (self.today + timedelta(days=1), 'tomorrow', pattern)
                    elif date_type == 'yesterday':
                        return (self.today - timedelta(days=1), 'yesterday', pattern)
                    elif date_type == 'day_after_tomorrow':
                        return (self.today + timedelta(days=2), 'day_after_tomorrow', pattern)
                    elif date_type == 'this_week':
                        # Return the whole week
                        start_of_week = self.today - timedelta(days=self.today.weekday())
                        end_of_week = start_of_week + timedelta(days=6)
                        return ((start_of_week, end_of_week), 'this_week', pattern)
                    elif date_type == 'next_week':
                        # Return the next week (starting from Monday of next week)
                        # Calculate days until next Monday
                        days_until_next_monday = 7 - self.today.weekday() if self.today.weekday() > 0 else 7
                        start_of_week = self.today + timedelta(days=days_until_next_monday)
                        end_of_week = start_of_week + timedelta(days=6)
                        return ((start_of_week, end_of_week), 'next_week', pattern)
                    elif date_type == 'this_month':
                        # Return the whole month
                        start_of_month = self.today.replace(day=1)
                        last_day = calendar.monthrange(self.today.year, self.today.month)[1]
                        end_of_month = self.today.replace(day=last_day)
                        return ((start_of_month, end_of_month), 'this_month', pattern)
                    elif date_type in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
                        # Map date_type to weekday number (0=Monday, 6=Sunday)
                        weekday_map = {'monday': 0, 'tuesday': 1, 'wednesday': 2, 
                                      'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6}
                        target_weekday = weekday_map[date_type]
                        current_weekday = self.today.weekday()
                        
                        # Check if "next" appears before weekday
                        next_week_patterns = ['tuần sau', 'tuần tới', 'tuan sau', 'tuan toi', 'next']
                        is_next_week = any(next_pattern in question_normalized for next_pattern in next_week_patterns)
                        
                        if is_next_week:
                            # Get next week's specified weekday
                            days_ahead = target_weekday - current_weekday
                            if days_ahead <= 0:  # Target is today or earlier this week
                                days_ahead += 7  # Move to next week
                            days_ahead += 7  # Add another week for "next"
                        else:
                            # Get this week's specified weekday (or next week if we've passed it)
                            days_ahead = target_weekday - current_weekday
                            if days_ahead < 0:  # Target is earlier this week (we missed it)
                                days_ahead += 7  # Move to next week
                        
                        target_date = self.today + timedelta(days=days_ahead)
                        return (target_date, date_type, pattern)
        
        # Check for specific dates in DD/MM or DD/MM/YYYY format
        date_patterns = [
            r'(\d{1,2})[/-](\d{1,2})(?:[/-](\d{4}))?',  # DD/MM or DD/MM/YYYY
            r'ngày (\d{1,2})[/-](\d{1,2})',  # ngày DD/MM
            r'ngay (\d{1,2})[/-](\d{1,2})'   # ngay DD/MM
        ]
        
        # First check if there's a direct date pattern in the question
        for pattern in date_patterns:
            matches = re.search(pattern, question_normalized)
            if matches:
                logger.log_with_timestamp("SCHEDULE API", f"Found date pattern: {matches.group(0)}")
                day = int(matches.group(1))
                month = int(matches.group(2))
                year = int(matches.group(3)) if len(matches.groups()) > 2 and matches.group(3) else self.today.year
                
                try:
                    specific_date = datetime(year, month, day).date()
                    logger.log_with_timestamp("SCHEDULE API", f"Parsed specific date: {specific_date.strftime('%d/%m/%Y')}")
                    return (specific_date, 'specific_date', matches.group(0))
                except ValueError:
                    # Invalid date, like February 30
                    logger.log_with_timestamp("SCHEDULE API", f"Invalid date: {day}/{month}/{year}")
                    continue
        
        # No date reference found, default to today
        return (self.today, 'today', 'default')
    
    def normalize_vietnamese(self, text):
        """
        Convert text with diacritics to non-diacritic form to make matching more robust
        """
        return unidecode(text).lower()

    async def get_schedule_by_semester(self, hoc_ky):
        """Get schedule data for a specific semester

        Args:
            hoc_ky (str): Semester ID

        Returns:
            dict: Schedule data including weekly schedules and class periods
        """
        logger.log_with_timestamp("SCHEDULE API", f"Getting schedule for semester: {hoc_ky}")
        
        if not self.check_auth():
            logger.log_with_timestamp("SCHEDULE API", "No auth token found, getting current semester...")
            current_semester, error = self.auth_service.get_current_semester()
            if error:
                logger.log_with_timestamp("SCHEDULE ERROR", f"Authentication error: {error}")
                raise ValueError(f"Authentication error: {error}")
            hoc_ky = current_semester.get('hoc_ky')
            logger.log_with_timestamp("SCHEDULE API", f"Using semester from current period: {hoc_ky}")

        url = f"{self.base_url}/w-locdstkbtuanusertheohocky"
        headers = {
            "Authorization": f"Bearer {self.auth_service.access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "filter": {
                "hoc_ky": hoc_ky,
                "ten_hoc_ky": ""
            },
            "additional": {
                "paging": {
                    "limit": 100,
                    "page": 1
                },
                "ordering": [{
                    "name": None,
                    "order_type": None
                }]
            }
        }

        try:
            async with httpx.AsyncClient() as client:
                logger.log_with_timestamp("SCHEDULE API", f"Sending request to {url} with semester {hoc_ky}")
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                # Log detailed response information
                logger.log_with_timestamp("SCHEDULE API", f"Received response: Status {response.status_code}")
                logger.log_with_timestamp("SCHEDULE API", "Response data details:")
                
                if data.get('data'):
                    # Log semester information
                    semester_info = data['data'].get('hoc_ky', {})
                    logger.log_with_timestamp("SCHEDULE API", f"Semester: {semester_info.get('ten_hoc_ky', 'N/A')}")
                    
                    # Log weeks information
                    weeks = data['data'].get('ds_tuan_tkb', [])
                    logger.log_with_timestamp("SCHEDULE API", f"Total weeks: {len(weeks)}")
                    
                    # Log schedule details for each week
                    for week in weeks:
                        week_info = f"Week {week.get('tuan')}: {week.get('ngay_bat_dau')} - {week.get('ngay_ket_thuc')}"
                        classes = week.get('ds_thoi_khoa_bieu', [])
                        week_info += f" | Classes: {len(classes)}"
                        logger.log_with_timestamp("SCHEDULE API", week_info)
                        
                        # Log detailed class information for the week
                        for class_info in classes:
                            class_detail = f"- {class_info.get('ten_mon')} ({class_info.get('ma_mon')}) | "
                            class_detail += f"Room: {class_info.get('ma_phong')} | "
                            class_detail += f"Time: Tiết {class_info.get('tiet_bat_dau')} - {class_info.get('tiet_bat_dau') + class_info.get('so_tiet') - 1}"
                            class_detail += f"Day: {class_info.get('ngay_hoc')}"
                            logger.log_with_timestamp("SCHEDULE API", class_detail)
                
                return data
        except Exception as e:
            logger.log_with_timestamp("SCHEDULE ERROR", f"Error getting schedule: {str(e)}")
            raise

    def find_current_week_schedule(self, schedule_data, query_time=None):
        """Find the schedule for the week containing the query time

        Args:
            schedule_data (dict): Full schedule data from API
            query_time (datetime, optional): Time to find schedule for. Defaults to current time.

        Returns:
            dict: Schedule information for the matching week, or None if not found
        """
        if query_time is None:
            query_time = datetime.now()

        for week in schedule_data.get("data", {}).get("ds_tuan_tkb", []):
            start_date = datetime.strptime(week["ngay_bat_dau"], "%d/%m/%Y")
            end_date = datetime.strptime(week["ngay_ket_thuc"], "%d/%m/%Y")

            if start_date <= query_time <= end_date:
                return week

        return None

    def get_class_schedule(self, week_data, query_date):
        """Get class schedule for a specific date within a week

        Args:
            week_data (dict): Week schedule data
            query_date (datetime): Date to get schedule for

        Returns:
            list: List of classes scheduled for the query date
        """
        if not week_data:
            logger.log_with_timestamp("SCHEDULE API", f"No week data found for date: {query_date.strftime('%Y-%m-%d')}")
            return []

        classes = []
        logger.log_with_timestamp("SCHEDULE API", f"Searching classes for date: {query_date.strftime('%Y-%m-%d')}")
        logger.log_with_timestamp("SCHEDULE API", f"Week data structure: {week_data.keys()}")
        
        # Check if we have the correct week data structure or if we're working with the entire schedule data
        # The correct structure should have 'ds_thoi_khoa_bieu', otherwise we need to find the right week first
        if "ds_thoi_khoa_bieu" in week_data:
            class_list = week_data.get("ds_thoi_khoa_bieu", [])
        else:
            # We might have received the entire schedule data instead of a specific week
            # Try to find classes for this date from all weeks
            query_date_obj = query_date.date() if hasattr(query_date, 'date') else query_date
            all_weeks = week_data.get("data", {}).get("ds_tuan_tkb", [])
            
            # Find all classes across all weeks
            all_classes = []
            for week in all_weeks:
                all_classes.extend(week.get("ds_thoi_khoa_bieu", []))
            
            # Filter to only classes for the requested date
            class_list = []
            for class_info in all_classes:
                try:
                    api_date = class_info.get("ngay_hoc", "")
                    class_date_str = api_date.split("T")[0] if "T" in api_date else api_date
                    class_date = datetime.strptime(class_date_str, "%Y-%m-%d").date()
                    
                    if class_date == query_date_obj:
                        class_list.append(class_info)
                except Exception:
                    continue
        
        logger.log_with_timestamp("SCHEDULE API", f"Total classes in week: {len(class_list)}")
        
        for class_info in class_list:
            logger.log_with_timestamp("SCHEDULE API", f"Processing class: {class_info.get('ten_mon')} ({class_info.get('ma_mon')})")
            logger.log_with_timestamp("SCHEDULE API", f"Class data structure: {class_info.keys()}")
            
            api_date = class_info["ngay_hoc"]
            logger.log_with_timestamp("SCHEDULE API", f"Raw API date: {api_date}")
            
            try:
                # Ensure we're comparing dates properly by converting both to date objects
                class_date_str = api_date.split("T")[0] if "T" in api_date else api_date
                class_date = datetime.strptime(class_date_str, "%Y-%m-%d").date()
                
                # Make sure query_date is a date object
                query_date_obj = query_date.date() if hasattr(query_date, 'date') else query_date
                
                logger.log_with_timestamp("SCHEDULE API", f"Parsed class date: {class_date}, Query date: {query_date_obj} | Match: {class_date == query_date_obj}")
                
                if class_date == query_date_obj:
                    start_time = f"Tiết {class_info['tiet_bat_dau']}"
                    end_time = f"Tiết {class_info['tiet_bat_dau'] + class_info['so_tiet'] - 1}"
                    class_detail = {
                        "subject": f"{class_info['ten_mon']} ({class_info['ma_mon']})",
                        "time": f"{start_time} - {end_time}",
                        "room": class_info['ma_phong'],
                        "lecturer": class_info['ten_giang_vien'] or "Chưa cập nhật",
                        "ngay_hoc": class_date.strftime('%d/%m/%Y'),
                        "thu_kieu_so": class_info.get('thu_kieu_so', 0),
                        "ten_mon_eg": class_info.get('ten_mon_eg', ''),
                        "so_tin_chi": class_info.get('so_tin_chi', ''),
                        "ma_giang_vien": class_info.get('ma_giang_vien', ''),
                        "ten_mon": class_info.get('ten_mon', ''),
                        "ma_mon": class_info.get('ma_mon', '')
                    }
                    classes.append(class_detail)
                    logger.log_with_timestamp("SCHEDULE API", f"Found class: {class_detail['subject']} | Room: {class_detail['room']} | Time: {class_detail['time']} | Lecturer: {class_detail['lecturer']}")
            except Exception as e:
                logger.log_with_timestamp("SCHEDULE ERROR", f"Error processing class date: {str(e)}")
                continue
        
        if not classes:
            logger.log_with_timestamp("SCHEDULE API", f"No classes found for date: {query_date.strftime('%Y-%m-%d')}")
        else:
            logger.log_with_timestamp("SCHEDULE API", f"Total classes found for {query_date.strftime('%d/%m/%Y')}: {len(classes)}")
            
        return classes

    async def get_schedule(self, date, hoc_ky):
        """Get schedule for a specific date from PTIT API

        Args:
            date (datetime.date): The date to get schedule for
            hoc_ky (str): Semester ID

        Returns:
            dict: Schedule data for the specified date
        """
        try:
            # Get schedule data from API
            schedule_data = await self.get_schedule_by_semester(hoc_ky)
            
            # Find the current week's schedule
            week_data = self.find_current_week_schedule(schedule_data, date)
            if not week_data:
                return {
                    "date": date.strftime('%Y-%m-%d'),
                    "day_of_week": date.strftime('%A'),
                    "thu_kieu_so": date.weekday() + 2,  # Convert to Vietnamese day format (2=Monday, 8=Sunday)
                    "semester": f"Học kỳ {hoc_ky}",
                    "classes": []
                }
            
            # Get classes for the specific date
            classes = self.get_class_schedule(week_data, date)
            
            return {
                "date": date.strftime('%Y-%m-%d'),
                "day_of_week": date.strftime('%A'),
                "thu_kieu_so": date.weekday() + 2,  # Convert to Vietnamese day format (2=Monday, 8=Sunday)
                "semester": f"Học kỳ {hoc_ky}",
                "classes": classes
            }
            
        except Exception as e:
            print(f"Error getting schedule from PTIT API: {e}")
            return None
    
    def format_schedule_for_display(self, schedule_data, include_header=True):
        """
        Format schedule data for display in the chat.
        
        Args:
            schedule_data (dict): Schedule data to format
            include_header (bool): Whether to include the header with date information
            
        Returns:
            str: Formatted schedule text
        """
        vietnamese_days = {
            "Monday": "Thứ Hai",
            "Tuesday": "Thứ Ba",
            "Wednesday": "Thứ Tư",
            "Thursday": "Thứ Năm",
            "Friday": "Thứ Sáu",
            "Saturday": "Thứ Bảy",
            "Sunday": "Chủ Nhật"
        }
        
        day_name = vietnamese_days.get(schedule_data['day_of_week'], schedule_data['day_of_week'])
        date_parts = schedule_data['date'].split('-')
        formatted_date = f"{date_parts[2]}/{date_parts[1]}/{date_parts[0]}"
        thu_so = schedule_data.get('thu_kieu_so', 0)
        
        if not schedule_data["classes"]:
            if include_header:
                return f"Không có lớp học nào vào {day_name} (Thứ {thu_so}), ngày {formatted_date} ({schedule_data['semester']})."
            else:
                return ""
        
        result = ""
        if include_header:
            result = f"Lịch học ngày {formatted_date} ({day_name} - Thứ {thu_so}) - {schedule_data['semester']}:\n\n"
        
        for i, class_info in enumerate(schedule_data["classes"], 1):
            # Add Vietnamese subject name
            result += f"{i}. {class_info.get('ten_mon', '')} ({class_info.get('ma_mon', '')})\n"
            
            # Add English subject name if available
            if class_info.get('ten_mon_eg'):
                result += f"    {class_info.get('ten_mon_eg')}\n"
                
            # Add class time
            result += f"    {class_info['time']}\n"
            
            # Add room information
            result += f"    Phòng {class_info['room']}\n"
            
            # Add lecturer information with ID
            result += f"    {class_info['lecturer']}"
            if class_info.get('ma_giang_vien'):
                result += f" (Mã GV: {class_info.get('ma_giang_vien')})"
            result += "\n"
            
            # Add credit hours if available
            if class_info.get('so_tin_chi'):
                result += f"    Số tín chỉ: {class_info.get('so_tin_chi')}\n"
            
            # Add class date
            result += f"    Ngày học: {class_info.get('ngay_hoc', '')}\n"
                
            result += "\n"
        
        return result
        
    async def process_schedule_query(self, question, hoc_ky):
        """
        Process a schedule-related query, extract date information,
        and return the appropriate schedule data from PTIT API.
        
        Args:
            question (str): User's question about schedule
            hoc_ky (str): Semester ID for schedule lookup
            
        Returns:
            dict: Schedule information including formatted text and metadata
        """
        # Extract date reference from the question
        date_info, date_type, original_text = self.extract_date_references(question)
        
        # Process based on date type
        if isinstance(date_info, tuple):  # Date range (this_week, next_week, this_month)
            start_date, end_date = date_info
            
            # Get schedule for all days in the range
            formatted_message = f"Đây là lịch học cho {original_text} ({date_type}):\n\n"
            
            # Calculate the number of days in the range
            days_in_range = (end_date - start_date).days + 1
            
            # Limit to 7 days for week queries to avoid excessive API calls
            if date_type in ['this_week', 'next_week']:
                days_to_fetch = min(days_in_range, 7)
            else:
                # For month queries, limit to 14 days to avoid excessive API calls
                days_to_fetch = min(days_in_range, 14)
            
            # Get schedule for each day in the range
            has_classes = False
            for i in range(days_to_fetch):
                current_date = start_date + timedelta(days=i)
                daily_schedule = await self.get_schedule(current_date, hoc_ky)
                
                if daily_schedule and daily_schedule["classes"]:
                    has_classes = True
                    formatted_message += f"--- {current_date.strftime('%d/%m/%Y')} ---\n"
                    formatted_message += self.format_schedule_for_display(daily_schedule)
                    formatted_message += "\n"
            
            if not has_classes:
                formatted_message += f"Không có lớp học nào trong khoảng thời gian từ {start_date.strftime('%d/%m/%Y')} đến {start_date + timedelta(days=days_to_fetch-1)}.\n"
                formatted_message += "Vui lòng kiểm tra lại lịch học trên hệ thống quản lý học tập của trường."
            
            # Format the date range information for the response
            date_range_info = f"{start_date.strftime('%d/%m/%Y')} to {end_date.strftime('%d/%m/%Y')}"
            
        else:  # Single date
            # Get schedule data from PTIT API
            schedule_data = await self.get_schedule(date_info, hoc_ky)
            if schedule_data:
                formatted_message = self.format_schedule_for_display(schedule_data)
            else:
                formatted_message = "Xin lỗi, không thể lấy thông tin lịch học từ hệ thống. Vui lòng thử lại sau."
            
            # Format the single date information for the response
            date_range_info = date_info.strftime('%d/%m/%Y')
        
        return {
            'schedule_text': formatted_message,
            'date_info': date_range_info,
            'date_type': date_type,
            'original_text': original_text
        }