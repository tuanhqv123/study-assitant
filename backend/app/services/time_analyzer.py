from datetime import datetime, timedelta
import calendar
import json
from ..utils.logger import Logger
from unidecode import unidecode

logger = Logger()

class TimeAnalyzer:
    def __init__(self, ai_service):
        self.today = datetime.now().date()
        self.ai_service = ai_service
        
    def analyze_time_references(self, question):
        """
        Analyze time references in a question using AI instead of regex patterns.
        Returns a tuple of (referenced_date, date_type, original_text)
        
        Args:
            question (str): The user's question containing time references
            
        Returns:
            tuple: (referenced_date, date_type, original_text)
                referenced_date can be a single date or a tuple of (start_date, end_date)
                date_type is a string indicating the type of date reference
                original_text is the original text that was matched
        """
        # Safety check for a non-date question
        if not question or question.strip() == '':
            logger.log_with_timestamp("TIME ANALYSIS", "Empty question, returning default today")
            return (self.today, 'today', 'default')
        
        # Normalize query về không dấu, chữ thường
        question_normalized = unidecode(question.lower())
        
        # --- Ưu tiên nhận diện tuần có ngày/tháng/năm ---
        week_with_full_date_patterns = [
            r"tuan.*ngay[\s:]*([0-9]{1,2})[/-]([0-9]{1,2})(?:[/-]([0-9]{4}))?",  # tuan ... ngay DD/MM(/YYYY)
            r"tuan[\s:]*([0-9]{1,2})[/-]([0-9]{1,2})(?:[/-]([0-9]{4}))?",         # tuan DD/MM(/YYYY)
            r"tuan[\s:]*([0-9]{1,2}) thang[\s:]*([0-9]{1,2})(?: nam[\s:]*([0-9]{4}))?"  # tuan 21 thang 4 (nam 2025)
        ]
        import re
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
                logger.log_with_timestamp("TIME ANALYSIS", f"[REGEX] Detected week with full date: {matches.group(0)} => {target_date.strftime('%d/%m/%Y')}, week: {start_of_week.strftime('%d/%m/%Y')} - {end_of_week.strftime('%d/%m/%Y')}")
                return ((start_of_week, end_of_week), 'specific_week', matches.group(0))
        
        # DIRECT PATTERN MATCHING for common Vietnamese weekday references
        # This approach bypasses the AI-based analysis for common weekday references
        import re
        
        # First, check for specific week references with dates like "tuần ngày 19"
        week_with_date_patterns = [
            r'tu[ầâ]n\s*(?:có\s*)?ng[àa]y\s*(\d{1,2})',  # tuần có ngày DD, tuần ngày DD
            r'tu[ầâ]n\s*(?:c[óo]\s*)?ng[àa]y\s*(\d{1,2})',  # tuan co ngay DD, tuan ngay DD
            r'tu[ầâ]n.*ng[àa]y\s*(\d{1,2})',      # tuần ... ngày DD
            r'tuan.*ngay\s*(\d{1,2})',      # tuan ... ngay DD
            r'tu[ầâ]n\s+(\d{1,2})',          # tuần DD
            r'tuan\s+(\d{1,2})'           # tuan DD
        ]
        
        for pattern in week_with_date_patterns:
            matches = re.search(pattern, question.lower())
            if matches:
                day = int(matches.group(1))
                logger.log_with_timestamp("TIME ANALYSIS", f"Found specific week pattern: '{matches.group(0)}' with day {day}")
                
                # Assume current month and year if not specified
                target_date = None
                try:
                    target_date = datetime(self.today.year, self.today.month, day).date()
                    # If the day has passed in current month, check if user might be referring to next month
                    if target_date < self.today and day < 15:  # Assuming if day is small, user might mean next month
                        next_month = self.today.month + 1 if self.today.month < 12 else 1
                        next_year = self.today.year if self.today.month < 12 else self.today.year + 1
                        target_date = datetime(next_year, next_month, day).date()
                except ValueError:
                    # Invalid date, try next month if current month doesn't have this day
                    try:
                        next_month = self.today.month + 1 if self.today.month < 12 else 1
                        next_year = self.today.year if self.today.month < 12 else self.today.year + 1
                        target_date = datetime(next_year, next_month, day).date()
                    except ValueError:
                        # Still invalid, skip this pattern
                        continue
                
                if target_date:
                    logger.log_with_timestamp("TIME ANALYSIS", 
                        f"Detected specific week pattern: '{matches.group(0)}', target date: {target_date.strftime('%d/%m/%Y')}")
                    
                    # Calculate the week containing this date
                    start_of_week = target_date - timedelta(days=target_date.weekday())  # Monday of the week
                    end_of_week = start_of_week + timedelta(days=6)  # Sunday of the week
                    
                    logger.log_with_timestamp("TIME ANALYSIS", 
                        f"Week range: {start_of_week.strftime('%d/%m/%Y')} (Monday) to {end_of_week.strftime('%d/%m/%Y')} (Sunday)")
                    
                    return ((start_of_week, end_of_week), 'specific_week', matches.group(0))
        
        # Map weekday references directly to their proper indices and names
        weekday_mapping = {
            "2": {"index": 0, "name": "monday"},    # thứ 2 → Monday (0)
            "3": {"index": 1, "name": "tuesday"},   # thứ 3 → Tuesday (1)
            "4": {"index": 2, "name": "wednesday"}, # thứ 4 → Wednesday (2)
            "5": {"index": 3, "name": "thursday"},  # thứ 5 → Thursday (3)
            "6": {"index": 4, "name": "friday"},    # thứ 6 → Friday (4)
            "7": {"index": 5, "name": "saturday"},  # thứ 7 → Saturday (5)
            "cn": {"index": 6, "name": "sunday"},   # chủ nhật → Sunday (6)
            "8": {"index": 6, "name": "sunday"}     # thứ 8 → Sunday (6) (alternative)
        }
        
        # Very simple pattern to capture "thu X" or "thứ X" references
        thu_pattern = r'th[uưứ]?\s*([2-8]|cn)'
        thu_match = re.search(thu_pattern, question.lower())
        
        if thu_match:
            day_ref = thu_match.group(1)
            logger.log_with_timestamp("TIME ANALYSIS", f"Direct Vietnamese weekday match: thứ {day_ref}")
            
            # Get the weekday index and name
            if day_ref in weekday_mapping:
                weekday_index = weekday_mapping[day_ref]["index"]
                weekday_name = weekday_mapping[day_ref]["name"]
                
                # Look for week qualifiers in the question (tuần này, tuần sau, tuần trước)
                this_week_pattern = r'tu[ầâ]n\s*n[àa]y|n[àa]y|nay'
                next_week_pattern = r'tu[ầâ]n\s*sau|tu[ầâ]n\s*t[ớơ]i|sau|t[ớơ]i|toi'
                prev_week_pattern = r'tu[ầâ]n\s*tr[ưươ][ớơ]c|tr[ưươ][ớơ]c|truoc'
                
                # Check which week qualifier is present
                is_this_week = re.search(this_week_pattern, question.lower()) is not None
                is_next_week = re.search(next_week_pattern, question.lower()) is not None
                is_prev_week = re.search(prev_week_pattern, question.lower()) is not None
                
                # Calculate the target date based on current day and the week reference
                current_weekday = self.today.weekday()
                
                # Calculate the Monday of the current week
                current_monday = self.today - timedelta(days=current_weekday)
                
                if is_next_week:
                    # For next week, add 7 days to current week's Monday, then add the weekday offset
                    target_date = current_monday + timedelta(days=7 + weekday_index)
                    logger.log_with_timestamp("TIME ANALYSIS", 
                        f"Next week calculation: Current Monday ({current_monday.strftime('%d/%m/%Y')}) + 7 days + {weekday_index} days")
                elif is_prev_week:
                    # For previous week, subtract 7 days from current week's Monday, then add the weekday offset
                    target_date = current_monday + timedelta(days=-7 + weekday_index)
                    logger.log_with_timestamp("TIME ANALYSIS", 
                        f"Previous week calculation: Current Monday ({current_monday.strftime('%d/%m/%Y')}) - 7 days + {weekday_index} days")
                else:
                    # For this week or unspecified, calculate based on the current week's Monday
                    target_date = current_monday + timedelta(days=weekday_index)
                    logger.log_with_timestamp("TIME ANALYSIS", 
                        f"Current week calculation: Current Monday ({current_monday.strftime('%d/%m/%Y')}) + {weekday_index} days")
                
                logger.log_with_timestamp("TIME ANALYSIS", 
                    f"Direct calculation: Today is {calendar.day_name[current_weekday]} (index {current_weekday}), " +
                    f"Target day is {calendar.day_name[weekday_index]} (index {weekday_index}), " +
                    f"Final date: {target_date.strftime('%d/%m/%Y')}")
                
                return (target_date, weekday_name, f"thứ {day_ref}")
        
        # First check if the question is likely about dates/schedule
        # Common Vietnamese date-related keywords
        date_keywords = [
            'hôm nay', 'ngày mai', 'hôm qua', 'thứ', 'tuần', 'tháng', 'lịch', 
            'ngày', 'mai', 'kia', 'mốt', 'today', 'tomorrow', 'yesterday', 
            'schedule', 'week', 'month', 'monday', 'tuesday', 'wednesday',
            'thursday', 'friday', 'saturday', 'sunday', 'chủ nhật', 'cn', 'thu', 'th'
        ]
        
        # Check if any date-related keywords appear in the question
        is_date_related = any(keyword in question.lower() for keyword in date_keywords)
        if not is_date_related:
            logger.log_with_timestamp("TIME ANALYSIS", "Question doesn't appear to be date-related, returning default today")
            return (self.today, 'today', 'default')
        
        # First check for direct date patterns before using AI
        import re
        date_patterns = [
            r'(\d{1,2})[/-](\d{1,2})(?:[/-](\d{4}))?',  # DD/MM or DD/MM/YYYY
            r'ngày (\d{1,2})[/-](\d{1,2})',  # ngày DD/MM
            r'ngay (\d{1,2})[/-](\d{1,2})',   # ngay DD/MM
            r'ngày (\d{1,2})(?![/-])',  # ngày DD (without month/year)
            r'ngay (\d{1,2})(?![/-])'   # ngay DD (without month/year)
        ]
        
        for pattern in date_patterns:
            matches = re.search(pattern, question)
            if matches:
                logger.log_with_timestamp("TIME ANALYSIS", f"Found direct date pattern: {matches.group(0)}")
                day = int(matches.group(1))
                
                # Check if this is a pattern with just the day (ngày DD or ngay DD)
                if pattern.endswith('(?![/-])'):  # Patterns for ngày DD or ngay DD without month/year
                    month = self.today.month
                    year = self.today.year
                    logger.log_with_timestamp("TIME ANALYSIS", f"Found day-only pattern, using current month/year: {day}/{month}/{year}")
                else:  # Regular patterns with month/year
                    month = int(matches.group(2))
                    year = int(matches.group(3)) if len(matches.groups()) > 2 and matches.group(3) else self.today.year
                
                try:
                    specific_date = datetime(year, month, day).date()
                    logger.log_with_timestamp("TIME ANALYSIS", f"Parsed specific date: {specific_date.strftime('%d/%m/%Y')}")
                    return (specific_date, 'specific_date', matches.group(0))
                except ValueError:
                    # Invalid date, like February 30
                    logger.log_with_timestamp("TIME ANALYSIS", f"Invalid date: {day}/{month}/{year}")
                    continue
        
        # Check for specific week containing a date (e.g., "tuần có ngày 3")
        week_with_date_patterns = [
            r'tuần có ngày (\d{1,2})',    # tuần có ngày DD
            r'tuan co ngay (\d{1,2})',    # tuan co ngay DD
            r'tuần.*ngày (\d{1,2})',      # tuần ... ngày DD
            r'tuan.*ngay (\d{1,2})',      # tuan ... ngay DD
            r'tuần ngày (\d{1,2})',       # tuần ngày DD
            r'tuan ngay (\d{1,2})',       # tuan ngay DD
            r'tuần\s+(\d{1,2})',          # tuần DD
            r'tuan\s+(\d{1,2})',          # tuan DD 
            r't\s+co\s+ngay\s+(\d{1,2})',     # t co ngay DD (viết tắt "tuần" thành "t")
            r't\s+ngay\s+(\d{1,2})',          # t ngay DD (viết tắt "tuần" thành "t")
            r'tuan\s+co\s+ng\s+(\d{1,2})',    # tuan co ng DD
            r't\s+co\s+ng\s+(\d{1,2})',       # t co ng DD (viết tắt "tuần" thành "t")
            r'tn\s+co\s+ng\s+(\d{1,2})',      # tn co ng DD (viết tắt "tuần" thành "tn")
            r'tuan\s+ng\s+(\d{1,2})',         # tuan ng DD
            r't\s+ng\s+(\d{1,2})',            # t ng DD (viết tắt "tuần" thành "t")
            r'tn\s+ng\s+(\d{1,2})'          # tn ng DD (viết tắt "tuần" thành "tn")
        
        ]
        
        for pattern in week_with_date_patterns:
            matches = re.search(pattern, question.lower())
            if matches:
                day = int(matches.group(1))
                # Assume current month and year if not specified
                target_date = None
                try:
                    target_date = datetime(self.today.year, self.today.month, day).date()
                    # If the day has passed in current month, check if user might be referring to next month
                    if target_date < self.today and day < 15:  # Assuming if day is small, user might mean next month
                        next_month = self.today.month + 1 if self.today.month < 12 else 1
                        next_year = self.today.year if self.today.month < 12 else self.today.year + 1
                        target_date = datetime(next_year, next_month, day).date()
                except ValueError:
                    # Invalid date, try next month if current month doesn't have this day
                    try:
                        next_month = self.today.month + 1 if self.today.month < 12 else 1
                        next_year = self.today.year if self.today.month < 12 else self.today.year + 1
                        target_date = datetime(next_year, next_month, day).date()
                    except ValueError:
                        # Still invalid, skip this pattern
                        continue
                
                if target_date:
                    logger.log_with_timestamp("TIME ANALYSIS", 
                        f"Detected specific week pattern: '{matches.group(0)}', target date: {target_date.strftime('%d/%m/%Y')}")
                    
                    # Calculate the week containing this date
                    start_of_week = target_date - timedelta(days=target_date.weekday())  # Monday of the week
                    end_of_week = start_of_week + timedelta(days=6)  # Sunday of the week
                    
                    logger.log_with_timestamp("TIME ANALYSIS", 
                        f"Week range: {start_of_week.strftime('%d/%m/%Y')} (Monday) to {end_of_week.strftime('%d/%m/%Y')} (Sunday)")
                    
                    return ((start_of_week, end_of_week), 'specific_week', matches.group(0))
        
        # Before trying AI analysis, check for common patterns of weekday + time reference
        import re
        
        # Define Vietnamese weekday patterns with more flexible matching for abbreviated forms
        # Handles both full forms (thứ bảy) and shortened forms (th 7, t7)
        # Also include thứ 8 as another way to refer to Sunday in Vietnamese
        vn_weekday_pattern = r'(th[ứư]?\s*[2-8]|th[ứư]?\s*[bh]ai|th[ứư]?\s*ba|th[ứư]?\s*t[ưu]|th[ứư]?\s*n[ăa]m|th[ứư]?\s*s[áa]u|th[ứư]?\s*b[ảa]y|ch[uủ]?\s*nh[aậ]t|t[2-8]|cn)'
        
        # Also handle invalid day references like "thứ 100"
        invalid_day_pattern = r'th[ứư]?\s*(\d+)'
        invalid_day_match = re.search(invalid_day_pattern, question.lower())
        if invalid_day_match:
            day_num = int(invalid_day_match.group(1))
            if day_num > 8:  # Vietnamese days are from 2-8 (Monday to Sunday)
                logger.log_with_timestamp("TIME ANALYSIS", f"Found invalid day reference: thứ {day_num}")
                logger.log_with_timestamp("TIME ANALYSIS", "Invalid weekday number, falling back to today")
                return (self.today, 'today', f"thứ {day_num}")
                
        # Define time reference patterns with more variations
        # Handles full forms (tuần này) and shortened forms (này)
        # Also handle variations without accent marks
        time_ref_pattern = r'(tu[ầâ]n\s*n[àa]y|tu[ầâ]n\s*sau|tu[ầâ]n\s*t[ớơ]i|tu[ầâ]n\s*tr[ưươ][ớơ]c|n[àa]y|sau|t[ớơ]i|tr[ưươ][ớơ]c|nay)'
        
        # Log the input for debugging
        logger.log_with_timestamp("TIME ANALYSIS DEBUG", f"Input question: '{question}'")
        
        # Check for pattern "weekday + this/next/last week" or just "weekday + này/sau/trước"
        # The .*? allows for words between weekday and time reference (up to 15 chars to limit over-matching)
        combined_pattern = vn_weekday_pattern + r'.{0,15}?' + time_ref_pattern
        
        # Also look for simple pattern "weekday + này" which is very common in Vietnamese
        simple_pattern = vn_weekday_pattern + r'\s*n[àa]y'
        
        # Add direct pattern match for "thu 7 nay" (without accents)
        direct_pattern = r'th(u|[ưứ])?\s*7\s*nay'
        
        # Add pattern for just weekday with no qualifier (meaning current/next occurrence)
        bare_weekday_pattern = r'(th[ứư]?\s*[2-8]|th[ứư]?\s*[bh]ai|th[ứư]?\s*ba|th[ứư]?\s*t[ưu]|th[ứư]?\s*n[ăa]m|th[ứư]?\s*s[áa]u|th[ứư]?\s*b[ảa]y|ch[uủ]?\s*nh[aậ]t|t[2-8]|cn)$'
        
        # Try all patterns in sequence
        combined_match = re.search(combined_pattern, question.lower())
        simple_match = re.search(simple_pattern, question.lower())
        direct_match = re.search(direct_pattern, question.lower())
        bare_match = re.search(bare_weekday_pattern, question.lower())
        
        # Log pattern matches for debugging
        if combined_match:
            logger.log_with_timestamp("TIME ANALYSIS DEBUG", f"Combined pattern match: '{combined_match.group(0)}'")
        if simple_match:
            logger.log_with_timestamp("TIME ANALYSIS DEBUG", f"Simple pattern match: '{simple_match.group(0)}'")
        if direct_match:
            logger.log_with_timestamp("TIME ANALYSIS DEBUG", f"Direct pattern match: '{direct_match.group(0)}'")
        if bare_match:
            logger.log_with_timestamp("TIME ANALYSIS DEBUG", f"Bare pattern match: '{bare_match.group(0)}'")
        
        # Process the match (checking all pattern types)
        match = combined_match or simple_match or direct_match or bare_match
        if match:
            # We found a pattern like "thứ X tuần này/sau" or "th X này" or just "thứ X" or "thu 7 nay"
            full_match = match.group(0)
            
            # Handle special case for direct_match which doesn't have the same group structure
            if match == direct_match:
                weekday_match = "thu 7"
                week_ref_match = "nay"
            else:
                # For other types of matches
                weekday_match = match.group(1) if match != direct_match else "thu 7"
                
                # Get week_ref_match from combined_match if available, otherwise default to "này" for simple_match
                # or "" for bare_match
                week_ref_match = ""
                if match == combined_match:
                    week_ref_match = combined_match.group(2)
                elif match == simple_match:
                    week_ref_match = "này"
            
            logger.log_with_timestamp("TIME ANALYSIS", f"Found direct pattern: '{full_match}', Weekday: '{weekday_match}', Week: '{week_ref_match}'")
            
            # Special handling for "thu 7" (Saturday) references
            if '7' in weekday_match:
                # Force weekday_index to 5 (Saturday in Python's 0-6 system where Monday is 0)
                weekday_index = 5
                logger.log_with_timestamp("TIME ANALYSIS", "Detected 'thu 7' reference, forcing weekday_index to 5 (Saturday)")
            # Other weekday mappings
            elif '2' in weekday_match or 'hai' in weekday_match:
                weekday_index = 0  # Monday
            elif '3' in weekday_match or 'ba' in weekday_match:
                weekday_index = 1  # Tuesday
            elif '4' in weekday_match or 'tư' in weekday_match or 'tu' in weekday_match:
                weekday_index = 2  # Wednesday
            elif '5' in weekday_match or 'năm' in weekday_match or 'nam' in weekday_match:
                weekday_index = 3  # Thursday
            elif '6' in weekday_match or 'sáu' in weekday_match or 'sau' in weekday_match:
                weekday_index = 4  # Friday
            elif '8' in weekday_match or 'nhật' in weekday_match or 'nhat' in weekday_match or 'cn' in weekday_match:
                weekday_index = 6  # Sunday
            
            if weekday_index is not None:
                # Simple and direct calculation for the correct date
                # Get the current weekday (0 = Monday, 6 = Sunday)
                current_weekday = self.today.weekday()
                
                # Default to finding the next occurrence of the requested day
                # For example, if today is Wednesday (2) and user asks for Saturday (5), 
                # we need to add (5 - 2) = 3 days
                days_to_add = 0
                
                if 'này' in week_ref_match or 'nay' in week_ref_match or not week_ref_match:
                    # Calculate days to add to reach the requested weekday in the current week
                    days_to_add = weekday_index - current_weekday
                    
                    # If the day has already passed this week, go to next week
                    if days_to_add < 0:
                        days_to_add += 7
                        
                elif 'sau' in week_ref_match or 'tới' in week_ref_match or 'toi' in week_ref_match:
                    # Next week - calculate days until the specified day next week
                    # First get to the same day next week (+7) then adjust for different weekday
                    days_to_add = 7 + (weekday_index - current_weekday)
                    
                elif 'trước' in week_ref_match or 'truoc' in week_ref_match:
                    # Previous week - calculate days to the specified day last week
                    # First go back a week (-7) then adjust for different weekday
                    days_to_add = -7 + (weekday_index - current_weekday)
                
                # Calculate the target date
                target_date = self.today + timedelta(days=days_to_add)
                
                # Map weekday index to name
                weekday_types = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
                weekday_type = weekday_types[weekday_index]
                
                # Verify the calculation is correct
                if target_date.weekday() != weekday_index:
                    logger.log_with_timestamp("TIME ANALYSIS ERROR", 
                        f"Calculation error! Expected weekday index {weekday_index}, but calculated date {target_date.strftime('%d/%m/%Y')} has weekday index {target_date.weekday()}")
                
                logger.log_with_timestamp("TIME ANALYSIS", 
                    f"Calculated date: {target_date.strftime('%d/%m/%Y')} | Weekday: {calendar.day_name[target_date.weekday()]} | Days added: {days_to_add}")
                
                return (target_date, weekday_type, full_match)
                
        # Also check for direct week references without specific days
        week_ref_pattern = r'tu[ầâ]n\s*(n[àa]y|sau|t[ớơ]i|tr[ưươ][ớơ]c)'
        week_match = re.search(week_ref_pattern, question.lower())
        
        if week_match:
            full_match = week_match.group(0)
            week_type = week_match.group(1)
            
            # Calculate current week's Monday
            current_monday = self.today - timedelta(days=self.today.weekday())
            
            # Determine the week type
            if 'này' in week_type or 'nay' in week_type:
                start_date = current_monday
                end_date = current_monday + timedelta(days=6)
                week_name = 'this_week'
            elif 'sau' in week_type or 'tới' in week_type or 'toi' in week_type:
                start_date = current_monday + timedelta(days=7)
                end_date = start_date + timedelta(days=6)
                week_name = 'next_week'
            elif 'trước' in week_type or 'truoc' in week_type:
                start_date = current_monday - timedelta(days=7)
                end_date = start_date + timedelta(days=6)
                week_name = 'last_week'
            else:
                # Default to current week
                start_date = current_monday
                end_date = current_monday + timedelta(days=6)
                week_name = 'this_week'
                
            logger.log_with_timestamp("TIME ANALYSIS", 
                f"Direct week match: {start_date.strftime('%d/%m/%Y')} to {end_date.strftime('%d/%m/%Y')} ({week_name})")
                
            return ((start_date, end_date), week_name, full_match)
        
        # If no direct patterns found, use AI-based analysis
        # Create a system prompt for time analysis
        time_analysis_prompt = {
            "role": "system", 
            "content": """
            You are a time reference analysis system for a student assistant application. Your task is to identify time references in user questions and return structured information.
            
            Types of time references to identify (in both Vietnamese and English):
            1. Specific days: today, tomorrow, yesterday, day after tomorrow, etc.
            2. Days of the week: Monday, Tuesday, Wednesday, etc.
            3. Weeks: this week, next week, last week, week before last
            4. Time periods: week containing date X, this month, etc.
            5. Specific dates in formats: DD/MM, DD/MM/YYYY
            6. Multiple days: Monday and Tuesday, Monday to Friday, etc.
            7. Special cases: weekend, holidays, exam period, etc.
            
            Analyze the question and return a JSON object with these fields:
            - "date_type": Type of time reference (today, tomorrow, yesterday, day_after_tomorrow, this_week, next_week, last_week, previous_week, this_month, specific_date, specific_week, monday, tuesday, wednesday, thursday, friday, saturday, sunday, weekend, multiple_days, date_range)
            - "original_text": The original text in the question referring to time
            - "date_value": The date value relative to the current date (today). For single days, this is the day offset (0 for today, 1 for tomorrow, -1 for yesterday, etc.). For time periods, this is an array of two day offsets [start_offset, end_offset]. For specific dates, this is the date string.
            - "is_range": true if this is a time period, false if it's a specific day
            - "multiple_dates": (optional) An array of date values when multiple non-consecutive days are mentioned
            
            Examples:
            
            Question: "What's my schedule for today?"
            Response: {"date_type": "today", "original_text": "today", "date_value": 0, "is_range": false}
            
            Question: "Do I have class on Monday next week?"
            Response: {"date_type": "monday", "original_text": "Monday next week", "date_value": 8, "is_range": false}
            
            Question: "Show me my schedule for this week"
            Response: {"date_type": "this_week", "original_text": "this week", "date_value": [0, 6], "is_range": true}
            
            Question: "What's my schedule for the week containing May 15?"
            Response: {"date_type": "specific_week", "original_text": "week containing May 15", "date_value": "15/5", "is_range": true}
            
            Question: "Do I have classes on Monday and Wednesday?"
            Response: {"date_type": "multiple_days", "original_text": "Monday and Wednesday", "multiple_dates": [1, 3], "is_range": false}
            
            Question: "What's my schedule from Monday to Friday?"
            Response: {"date_type": "date_range", "original_text": "Monday to Friday", "date_value": [1, 5], "is_range": true}
            
            Question: "Lịch học của tôi hôm nay là gì?"
            Response: {"date_type": "today", "original_text": "hôm nay", "date_value": 0, "is_range": false}
            
            Question: "Tôi có lớp học vào thứ hai tuần sau không?"
            Response: {"date_type": "monday", "original_text": "thứ hai tuần sau", "date_value": 8, "is_range": false}
            
            Question: "Cho tôi xem lịch học tuần này"
            Response: {"date_type": "this_week", "original_text": "tuần này", "date_value": [0, 6], "is_range": true}
            
            Question: "Lịch học tuần có ngày 15/5 là gì?"
            Response: {"date_type": "specific_week", "original_text": "tuần có ngày 15/5", "date_value": "15/5", "is_range": true}
            
            Question: "Tôi có lớp học vào thứ hai và thứ tư không?"
            Response: {"date_type": "multiple_days", "original_text": "thứ hai và thứ tư", "multiple_dates": [1, 3], "is_range": false}
            
            Question: "Lịch học từ thứ hai đến thứ sáu của tôi?"
            Response: {"date_type": "date_range", "original_text": "từ thứ hai đến thứ sáu", "date_value": [1, 5], "is_range": true}
            """
        }
        
        try:
            # Send the time analysis request
            response, _ = self.ai_service.chat_with_ai(question, [time_analysis_prompt])
            
            # Extract the JSON response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                result = json.loads(json_str)
                
                # Process the result based on date_type
                date_type = result.get('date_type')
                original_text = result.get('original_text')
                date_value = result.get('date_value')
                is_range = result.get('is_range', False)
                
                # Initialize date_info variable before using it in logging
                date_info = None
                
                # Log the AI analysis result - without the date_info for now
                logger.log_with_timestamp(
                    "TIME ANALYSIS", 
                    f"Type: {date_type} | Text: {original_text}",
                    f"Value: {date_value} | Range: {is_range}"
                )
                
                # Convert the AI result to the expected format
                # Check for multiple_dates first (for non-consecutive days like "Monday and Wednesday")
                multiple_dates = result.get('multiple_dates')
                if date_type == 'multiple_days' and multiple_dates and isinstance(multiple_dates, list):
                    try:
                        # Convert day offsets to actual dates
                        dates = [self.today + timedelta(days=int(offset)) for offset in multiple_dates]
                        return (dates, 'multiple_days', original_text)
                    except Exception as e:
                        logger.log_with_timestamp("TIME ANALYSIS ERROR", f"Error processing multiple days: {str(e)}")
                        # Don't fallback to today immediately, try other formats
                
                # Handle week calculations (this_week, next_week, last_week)
                if date_type in ['this_week', 'next_week', 'last_week']:
                    try:
                        # Calculate Monday of current week
                        current_monday = self.today - timedelta(days=self.today.weekday())
                        
                        if date_type == 'this_week':
                            start_date = current_monday
                            end_date = current_monday + timedelta(days=6)
                        elif date_type == 'next_week':
                            start_date = current_monday + timedelta(days=7)
                            end_date = start_date + timedelta(days=6)
                        elif date_type == 'last_week':
                            start_date = current_monday - timedelta(days=7)
                            end_date = start_date + timedelta(days=6)
                        
                        logger.log_with_timestamp("TIME ANALYSIS", 
                            f"Calculated week range for {date_type}: {start_date.strftime('%d/%m/%Y')} to {end_date.strftime('%d/%m/%Y')}")
                        return ((start_date, end_date), date_type, original_text)
                    except Exception as e:
                        logger.log_with_timestamp("TIME ANALYSIS ERROR", f"Error processing {date_type}: {str(e)}")
                
                if is_range:
                    if date_type == 'specific_week' and isinstance(date_value, str):
                        # Handle specific week containing a date (e.g., "tuần có ngày 15/5")
                        try:
                            # Parse the date string
                            if '/' in date_value:
                                parts = date_value.split('/')
                                if len(parts) == 2:
                                    day, month = int(parts[0]), int(parts[1])
                                    year = self.today.year
                                elif len(parts) == 3:
                                    day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
                                else:
                                    raise ValueError("Invalid date format")
                            else:
                                raise ValueError("Invalid date format")
                                
                            # Create the date object
                            target_date = datetime(year, month, day).date()
                            
                            # Calculate the week containing this date
                            start_of_week = target_date - timedelta(days=target_date.weekday())  # Monday of the week
                            end_of_week = start_of_week + timedelta(days=6)  # Sunday of the week
                            return ((start_of_week, end_of_week), 'specific_week', original_text)
                        except Exception as e:
                            logger.log_with_timestamp("TIME ANALYSIS ERROR", f"Error processing specific week: {str(e)}")
                            # Fallback to today
                            return (self.today, 'today', 'default')
                    else:
                        # Handle other date ranges
                        if isinstance(date_value, list) and len(date_value) == 2:
                            start_offset, end_offset = date_value
                            start_date = self.today + timedelta(days=start_offset)
                            end_date = self.today + timedelta(days=end_offset)
                            return ((start_date, end_date), date_type, original_text)
                else:
                    # Handle single dates
                    if isinstance(date_value, (int, float)):
                        target_date = self.today + timedelta(days=int(date_value))
                        return (target_date, date_type, original_text)
                    
                # We already checked for direct date patterns at the beginning of the method
                # If we reach here, it means AI couldn't identify a date and no direct pattern was found earlier
                
                # If no direct date pattern found, fall back to today
                logger.log_with_timestamp("TIME ANALYSIS", "Falling back to today")
                return (self.today, 'today', 'default')
            else:
                # If JSON parsing fails, fall back to today
                logger.log_with_timestamp("TIME ANALYSIS ERROR", "Failed to parse JSON response")
                return (self.today, 'today', 'default')
                
        except Exception as e:
            # Log the error and fall back to today
            logger.log_with_timestamp("TIME ANALYSIS ERROR", f"Error: {str(e)}")
            return (self.today, 'today', 'default')