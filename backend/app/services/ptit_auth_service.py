from datetime import datetime, timedelta
import requests
from ..utils.logger import Logger

logger = Logger()

class PTITAuthService:
    def __init__(self):
        self.base_url = "https://uis.ptithcm.edu.vn/api"
        self.access_token = None
        self.token_expiry = None

    def login(self, username, password):
        """Authenticate with PTIT API and get access token"""
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                data={
                    'username': username,
                    'password': password,
                    'grant_type': 'password'
                }
            )

            if response.ok:
                data = response.json()
                self.access_token = data.get('access_token')
                # Set token expiry (typically 24 hours from now)
                self.token_expiry = datetime.now() + timedelta(hours=24)
                return True, None
            else:
                error_msg = response.json().get('error_description', 'Authentication failed')
                return False, error_msg

        except Exception as e:
            logger.log_with_timestamp("AUTH ERROR", str(e))
            return False, str(e)

    def get_current_semester(self):
        """Get current semester information from PTIT API"""
        if not self.access_token:
            return None, "Not authenticated"

        try:
            url = f"{self.base_url}/sch/w-locdshockytkbuser"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            data = {
                "filter": {"is_tieng_anh": None},
                "additional": {
                    "paging": {"limit": 100, "page": 1},
                    "ordering": [{"name": "hoc_ky", "order_type": 1}]
                }
            }

            response = requests.post(url, headers=headers, json=data)

            if response.ok:
                semester_data = response.json()
                if semester_data.get('result') and semester_data.get('data'):
                    semesters = semester_data['data'].get('ds_hoc_ky', [])
                    if semesters:
                        today = datetime.now().date()
                        
                        # Find current semester based on date
                        for semester in semesters:
                            try:
                                start_date = datetime.strptime(semester['ngay_bat_dau_hk'], '%d/%m/%Y').date()
                                end_date = datetime.strptime(semester['ngay_ket_thuc_hk'], '%d/%m/%Y').date()
                                
                                if start_date <= today <= end_date:
                                    return semester, None
                            except (ValueError, KeyError) as e:
                                logger.log_with_timestamp("SEMESTER ERROR", f"Error parsing semester dates: {str(e)}")
                        
                        # If no current semester found, use the most recent one
                        return semesters[0], None

            return None, f"Failed to get semester data: {response.status_code}"

        except Exception as e:
            logger.log_with_timestamp("SEMESTER ERROR", str(e))
            return None, str(e)