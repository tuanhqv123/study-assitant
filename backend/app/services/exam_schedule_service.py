from datetime import datetime, timedelta
import httpx
from ..utils.logger import Logger

logger = Logger()

class ExamScheduleService:
    def __init__(self, auth_service=None, schedule_service=None):
        self.base_url = "https://uis.ptithcm.edu.vn/api/epm"
        self.auth_service = auth_service
        self.schedule_service = schedule_service
        
    def set_auth_service(self, auth_service):
        """Set the authentication service for token management

        Args:
            auth_service (PTITAuthService): The authentication service instance
        """
        self.auth_service = auth_service
        
    def set_schedule_service(self, schedule_service):
        """Set the schedule service for date extraction

        Args:
            schedule_service (ScheduleService): The schedule service instance
        """
        self.schedule_service = schedule_service
        
    def check_auth(self):
        """Check if the service is properly authenticated

        Returns:
            bool: True if authenticated, False otherwise
        """
        return self.auth_service is not None and self.auth_service.access_token is not None
        
    async def get_exam_schedule_by_semester(self, hoc_ky=None, is_giua_ky=False):
        """Get exam schedule data for a specific semester

        Args:
            hoc_ky (str): Semester ID, will use current semester if None
            is_giua_ky (bool): Whether to get midterm or final exam schedule

        Returns:
            dict: Exam schedule data
        """
        logger.log_with_timestamp("EXAM SCHEDULE API", f"Getting exam schedule for semester: {hoc_ky}, midterm: {is_giua_ky}")
        
        if not self.check_auth():
            logger.log_with_timestamp("EXAM SCHEDULE API", "No auth token found, getting current semester...")
            current_semester, error = self.auth_service.get_current_semester()
            if error:
                logger.log_with_timestamp("EXAM SCHEDULE ERROR", f"Authentication error: {error}")
                raise ValueError(f"Authentication error: {error}")
            hoc_ky = current_semester.get('hoc_ky')
            logger.log_with_timestamp("EXAM SCHEDULE API", f"Using semester from current period: {hoc_ky}")

        url = f"{self.base_url}/w-locdslichthisvtheohocky"
        headers = {
            "Authorization": f"Bearer {self.auth_service.access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "filter": {
                "hoc_ky": hoc_ky,
                "is_giua_ky": is_giua_ky
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
                logger.log_with_timestamp("EXAM SCHEDULE API", f"Sending request to {url} with semester {hoc_ky}")
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                logger.log_with_timestamp("EXAM SCHEDULE API", f"Received response: Status {response.status_code}")
                
                if data.get('data'):
                    exams = data['data'].get('ds_lich_thi', [])
                    logger.log_with_timestamp("EXAM SCHEDULE API", f"Total exams: {len(exams)}")
                    
                    for exam in exams:
                        logger.log_with_timestamp("EXAM SCHEDULE API", 
                            f"Exam: {exam.get('ten_mon')} | Date: {exam.get('ngay_thi')} | Room: {exam.get('ma_phong')}")
                
                return data
        except Exception as e:
            logger.log_with_timestamp("EXAM SCHEDULE ERROR", f"Error getting exam schedule: {str(e)}")
            raise
            
    def get_exams_by_date(self, exam_data, date_str):
        """Get exams for a specific date

        Args:
            exam_data (dict): Full exam schedule data from API
            date_str (str): Date string in DD/MM/YYYY format

        Returns:
            list: List of exams on the specified date
        """
        if not exam_data or not exam_data.get('data') or not exam_data['data'].get('ds_lich_thi'):
            return []
            
        exams = exam_data['data']['ds_lich_thi']
        date_exams = []
        
        for exam in exams:
            if exam.get('ngay_thi') == date_str:
                date_exams.append(exam)
                
        return date_exams
        
    def get_exams_by_date_range(self, exam_data, start_date, end_date):
        """Get exams within a date range (inclusive)

        Args:
            exam_data (dict): Full exam schedule data from API
            start_date (datetime.date): Start date of the range
            end_date (datetime.date): End date of the range

        Returns:
            list: List of exams within the date range
        """
        if not exam_data or not exam_data.get('data') or not exam_data['data'].get('ds_lich_thi'):
            logger.log_with_timestamp("EXAM SCHEDULE", "No exam data available")
            return []
            
        exams = exam_data['data']['ds_lich_thi']
        range_exams = []
        
        # Format dates for comparison
        start_date_str = start_date.strftime('%d/%m/%Y')
        end_date_str = end_date.strftime('%d/%m/%Y')
        
        logger.log_with_timestamp("EXAM SCHEDULE", f"Searching for exams between {start_date_str} and {end_date_str}")
        
        # Convert all dates in the range to strings for comparison
        date_range_strs = []
        current_date = start_date
        while current_date <= end_date:
            date_range_strs.append(current_date.strftime('%d/%m/%Y'))
            current_date += timedelta(days=1)
        
        # Find all exams with dates in the range
        for exam in exams:
            exam_date = exam.get('ngay_thi', '')
            if exam_date in date_range_strs:
                range_exams.append(exam)
                logger.log_with_timestamp("EXAM SCHEDULE", f"Found exam on {exam_date}: {exam.get('ten_mon')}")
                
        logger.log_with_timestamp("EXAM SCHEDULE", f"Found {len(range_exams)} exams in date range")
        return range_exams
        
    def get_exams_by_subject(self, exam_data, subject_keyword):
        """Get exams for a specific subject (by keyword)

        Args:
            exam_data (dict): Full exam schedule data from API
            subject_keyword (str): Subject name or code keyword

        Returns:
            list: List of exams matching the subject keyword
        """
        if not exam_data or not exam_data.get('data') or not exam_data['data'].get('ds_lich_thi'):
            return []
            
        exams = exam_data['data']['ds_lich_thi']
        subject_exams = []
        
        subject_keyword = subject_keyword.lower()
        for exam in exams:
            subject_name = exam.get('ten_mon', '').lower()
            subject_code = exam.get('ma_mon', '').lower()
            
            if subject_keyword in subject_name or subject_keyword in subject_code:
                subject_exams.append(exam)
                
        return subject_exams
    
    def format_exam_schedule(self, exams, is_list=True):
        """Format exam schedule data for display

        Args:
            exams (list): List of exam data
            is_list (bool): Whether to format as a list of multiple exams

        Returns:
            str: Formatted exam schedule text
        """
        if not exams:
            return "Không tìm thấy lịch thi nào phù hợp với yêu cầu."
            
        result = ""
        
        for i, exam in enumerate(exams, 1):
            # Get the key exam information
            ten_mon = exam.get('ten_mon', 'N/A')
            ma_mon = exam.get('ma_mon', 'N/A')
            ky_thi = exam.get('ky_thi', 'N/A')
            hinh_thuc_thi = exam.get('hinh_thuc_thi', 'N/A')
            so_phut = exam.get('so_phut', 'N/A')
            gio_bat_dau = exam.get('gio_bat_dau', 'N/A')
            ngay_thi = exam.get('ngay_thi', 'N/A')
            dia_diem_thi = exam.get('dia_diem_thi', 'N/A')
            ma_phong = exam.get('ma_phong', 'N/A')
            ten_mon_eg = exam.get('ten_mon_eg', '')
            
            # Format the exam entry
            if is_list:
                result += f"{i}. {ten_mon} ({ma_mon})\n"
            else:
                result += f"{ten_mon} ({ma_mon})\n"
                
            # Add English subject name if available
            if ten_mon_eg:
                result += f"   {ten_mon_eg}\n"
                
            # Add exam details
            result += f"   {ky_thi}\n"
            result += f"   Hình thức: {hinh_thuc_thi}\n"
            result += f"   Thời gian: {gio_bat_dau}, {so_phut} phút, ngày {ngay_thi}\n"
            result += f"   Phòng thi: {ma_phong}, {dia_diem_thi}\n\n"
            
        return result
    
    async def process_exam_query(self, question, hoc_ky=None, is_giua_ky=False):
        """Process an exam schedule query and return formatted results
        
        Args:
            question (str): User's question about exam schedule
            hoc_ky (str): Semester ID, will use current semester if None
            is_giua_ky (bool): Whether to get midterm or final exam schedule
            
        Returns:
            dict: Exam schedule information with formatted text
        """
        # Get the complete exam schedule
        exam_data = await self.get_exam_schedule_by_semester(hoc_ky, is_giua_ky)
        
        # Default response (return all exams)
        exams_to_display = exam_data['data']['ds_lich_thi'] if exam_data.get('data') and exam_data['data'].get('ds_lich_thi') else []
        filter_type = "all"
        filter_value = ""
        
        # Use the ScheduleService's date extraction if available
        if self.schedule_service:
            logger.log_with_timestamp("EXAM SCHEDULE", "Using ScheduleService for date extraction")
            
            # Extract date from query
            date_info, date_type, original_text = self.schedule_service.extract_date_references(question)
            
            logger.log_with_timestamp("EXAM SCHEDULE", f"Date extraction result: {date_type}, {original_text}")
            
            # Handle date ranges (weeks, months)
            if isinstance(date_info, tuple):
                start_date, end_date = date_info
                logger.log_with_timestamp("EXAM SCHEDULE", 
                                         f"Date range detected: {start_date.strftime('%d/%m/%Y')} to {end_date.strftime('%d/%m/%Y')}")
                
                # Get exams within the date range
                exams_to_display = self.get_exams_by_date_range(exam_data, start_date, end_date)
                filter_type = "date_range"
                filter_value = f"{start_date.strftime('%d/%m/%Y')} to {end_date.strftime('%d/%m/%Y')}"
            else:
                # Single date
                logger.log_with_timestamp("EXAM SCHEDULE", f"Single date: {date_info.strftime('%d/%m/%Y')}")
                date_str = date_info.strftime('%d/%m/%Y')
                exams_to_display = self.get_exams_by_date(exam_data, date_str)
                filter_type = "date"
                filter_value = date_str
        else:
            # Fallback to basic pattern matching
            logger.log_with_timestamp("EXAM SCHEDULE", "Using basic pattern matching for date extraction")
            
            # Check for date queries - look for DD/MM or DD/MM/YYYY patterns
            date_patterns = [
                r'(\d{1,2})[/-](\d{1,2})(?:[/-](\d{4}))?',  # DD/MM or DD/MM/YYYY
                r'ngày (\d{1,2})[/-](\d{1,2})',              # ngày DD/MM
                r'ngay (\d{1,2})[/-](\d{1,2})'               # ngay DD/MM
            ]
            
            question_lower = question.lower()
            
            # Check for date references
            import re
            for pattern in date_patterns:
                matches = re.search(pattern, question)
                if matches:
                    day = int(matches.group(1))
                    month = int(matches.group(2))
                    year = datetime.now().year
                    if len(matches.groups()) > 2 and matches.group(3):
                        year = int(matches.group(3))
                        
                    try:
                        # Format date as DD/MM/YYYY
                        date_str = f"{day:02d}/{month:02d}/{year}"
                        exams_to_display = self.get_exams_by_date(exam_data, date_str)
                        filter_type = "date"
                        filter_value = date_str
                        break
                    except:
                        continue
            
            # Check for subject queries if no date filter applied
            if filter_type == "all":
                # Common subject-related terms in Vietnamese
                subject_terms = ["môn", "học phần", "mã môn", "mã học phần", "môn học"]
                
                for term in subject_terms:
                    if term in question_lower:
                        # Extract words after the term (simple approach)
                        parts = question_lower.split(term)
                        if len(parts) > 1:
                            subject_keyword = parts[1].strip().split()[0].strip()
                            if len(subject_keyword) > 2:  # Avoid too short keywords
                                exams_to_display = self.get_exams_by_subject(exam_data, subject_keyword)
                                filter_type = "subject"
                                filter_value = subject_keyword
                                break
        
        # Format the filtered exams
        formatted_exams = self.format_exam_schedule(exams_to_display)
        
        return {
            'exam_text': formatted_exams,
            'filter_type': filter_type,
            'filter_value': filter_value,
            'exam_count': len(exams_to_display),
            'is_midterm': is_giua_ky
        } 