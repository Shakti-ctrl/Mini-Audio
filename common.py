from flask import Blueprint, jsonify, session
from src.utils import get_log_content, clear_log

common_bp = Blueprint('common', __name__)

@common_bp.route('/log', methods=['GET'])
def get_log():
    """Get application log content"""
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    log_content = get_log_content()
    return jsonify({'log': log_content})

@common_bp.route('/clear_log', methods=['POST'])
def clear_log_route():
    """Clear application log"""
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    clear_log()
    return jsonify({'status': 'success', 'message': 'Log cleared'})

@common_bp.route('/status', methods=['GET'])
def get_status():
    """Get application status"""
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    return jsonify({
        'status': 'running',
        'message': 'Application is running normally'
    })

