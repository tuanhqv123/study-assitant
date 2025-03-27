from flask import Blueprint, request, jsonify
from ..services.ptit_auth_service import PTITAuthService
from ..services.schedule_service import ScheduleService
from ..utils.logger import Logger

ptit_bp = Blueprint('ptit', __name__)
logger = Logger()

auth_service = PTITAuthService()
schedule_service = ScheduleService(auth_service)

@ptit_bp.route('/login', methods=['POST'])
def login():
    """Handle PTIT user login"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({
            'success': False,
            'error': 'Username and password are required'
        }), 400

    success, error = auth_service.login(username, password)
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({
            'success': False,
            'error': error or 'Login failed'
        }), 401

@ptit_bp.route('/schedule', methods=['GET'])
async def get_schedule():
    """Get schedule for a specific date"""
    try:
        if not schedule_service.check_auth():
            return jsonify({
                'success': False,
                'error': 'Not authenticated. Please log in first.'
            }), 401

        # Get current semester schedule
        schedule_data = await schedule_service.get_schedule_by_semester(None)
        if not schedule_data:
            return jsonify({
                'success': False,
                'error': 'Failed to retrieve schedule'
            }), 500

        return jsonify({
            'success': True,
            'data': schedule_data
        })

    except Exception as e:
        logger.log_with_timestamp("SCHEDULE ERROR", str(e))
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500