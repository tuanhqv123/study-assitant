from flask import Blueprint, request, jsonify
from ..services.ptit_auth_service import PTITAuthService
from ..services.schedule_service import ScheduleService
from ..services.exam_schedule_service import ExamScheduleService
from ..utils.logger import Logger

ptit_bp = Blueprint('ptit', __name__)
logger = Logger()

auth_service = PTITAuthService()
schedule_service = ScheduleService(auth_service)
exam_schedule_service = ExamScheduleService(auth_service)

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

@ptit_bp.route('/exam-schedule', methods=['GET'])
async def get_exam_schedule():
    """Get exam schedule data"""
    try:
        if not exam_schedule_service.check_auth():
            return jsonify({
                'success': False,
                'error': 'Not authenticated. Please log in first.'
            }), 401

        # Get parameters with defaults
        hoc_ky = request.args.get('semester', None)
        is_giua_ky = request.args.get('is_midterm', 'false').lower() == 'true'
        
        # Get exam schedule data
        exam_data = await exam_schedule_service.get_exam_schedule_by_semester(hoc_ky, is_giua_ky)
        if not exam_data:
            return jsonify({
                'success': False,
                'error': 'Failed to retrieve exam schedule'
            }), 500

        return jsonify({
            'success': True,
            'data': exam_data
        })

    except Exception as e:
        logger.log_with_timestamp("EXAM SCHEDULE ERROR", str(e))
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500