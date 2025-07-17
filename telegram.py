from flask import Blueprint, request, jsonify, session, send_file
from threading import Thread
import os
from src.telegram_module import telegram_manager, run_async_function
from src.config import TELEGRAM_DIR
from src.utils import log

telegram_bp = Blueprint('telegram', __name__)

@telegram_bp.route('/search_messages', methods=['POST'])
def search_messages():
    """Search messages in a Telegram channel"""
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    channel_url = data.get('channel_url')
    api_id = data.get('api_id')
    api_hash = data.get('api_hash')
    message_filter = data.get('message_filter', 'all')
    limit = data.get('limit', 100)
    
    if not channel_url:
        return jsonify({'error': 'Channel URL is required'}), 400
    
    if not api_id or not api_hash:
        return jsonify({'error': 'API ID and API Hash are required'}), 400
    
    # Run search in background thread
    Thread(target=search_messages_async, args=(channel_url, api_id, api_hash, message_filter, limit)).start()
    
    return jsonify({'status': 'search_started', 'message': 'Telegram message search started'})

def search_messages_async(channel_url, api_id, api_hash, message_filter, limit):
    """Async function to search messages"""
    try:
        # Initialize client with provided credentials
        success = run_async_function(telegram_manager.initialize_client, api_id, api_hash)
        if not success:
            log("❌ Failed to initialize Telegram client")
            return
        
        # Get messages
        messages = run_async_function(
            telegram_manager.get_channel_messages, 
            channel_url, 
            limit, 
            message_filter
        )
        
        log(f"✅ Found {len(messages)} messages matching filter '{message_filter}'")
        
    except Exception as e:
        log(f"❌ Error in message search: {str(e)}")

@telegram_bp.route('/get_messages', methods=['GET'])
def get_messages():
    """Get cached messages from Telegram search"""
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    messages = telegram_manager.get_cached_messages()
    return jsonify(messages)

@telegram_bp.route('/forward_messages', methods=['POST'])
def forward_messages():
    """Forward selected messages to target channel"""
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    source_channel = data.get('source_channel')
    target_channel = data.get('target_channel')
    message_ids = data.get('message_ids', [])
    api_id = data.get('api_id')
    api_hash = data.get('api_hash')
    
    if not source_channel or not target_channel:
        return jsonify({'error': 'Source and target channels are required'}), 400
    
    if not message_ids:
        return jsonify({'error': 'No messages selected'}), 400
    
    if not api_id or not api_hash:
        return jsonify({'error': 'API ID and API Hash are required'}), 400
    
    # Run forwarding in background thread
    Thread(target=forward_messages_async, args=(source_channel, target_channel, message_ids, api_id, api_hash)).start()
    
    return jsonify({'status': 'forwarding_started', 'message': f'Forwarding {len(message_ids)} messages'})

def forward_messages_async(source_channel, target_channel, message_ids, api_id, api_hash):
    """Async function to forward messages"""
    try:
        # Initialize client
        success = run_async_function(telegram_manager.initialize_client, api_id, api_hash)
        if not success:
            log("❌ Failed to initialize Telegram client")
            return
        
        # Forward messages
        success = run_async_function(
            telegram_manager.forward_messages,
            source_channel,
            target_channel,
            message_ids
        )
        
        if success:
            log("✅ Message forwarding completed successfully")
        else:
            log("❌ Message forwarding failed")
            
    except Exception as e:
        log(f"❌ Error in message forwarding: {str(e)}")

@telegram_bp.route('/download_media', methods=['POST'])
def download_media():
    """Download media from selected messages"""
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    channel_url = data.get('channel_url')
    message_ids = data.get('message_ids', [])
    api_id = data.get('api_id')
    api_hash = data.get('api_hash')
    
    if not channel_url:
        return jsonify({'error': 'Channel URL is required'}), 400
    
    if not message_ids:
        return jsonify({'error': 'No messages selected'}), 400
    
    if not api_id or not api_hash:
        return jsonify({'error': 'API ID and API Hash are required'}), 400
    
    # Run download in background thread
    Thread(target=download_media_async, args=(channel_url, message_ids, api_id, api_hash)).start()
    
    return jsonify({'status': 'download_started', 'message': f'Downloading media from {len(message_ids)} messages'})

def download_media_async(channel_url, message_ids, api_id, api_hash):
    """Async function to download media"""
    try:
        # Initialize client
        success = run_async_function(telegram_manager.initialize_client, api_id, api_hash)
        if not success:
            log("❌ Failed to initialize Telegram client")
            return
        
        # Download media
        success = run_async_function(
            telegram_manager.download_media,
            channel_url,
            message_ids
        )
        
        if success:
            log("✅ Media download completed successfully")
        else:
            log("❌ Media download failed")
            
    except Exception as e:
        log(f"❌ Error in media download: {str(e)}")

@telegram_bp.route('/get_downloaded_files', methods=['GET'])
def get_downloaded_files():
    """Get list of downloaded Telegram files"""
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        files = []
        if os.path.exists(TELEGRAM_DIR):
            for filename in os.listdir(TELEGRAM_DIR):
                if filename.endswith('.session'):
                    continue  # Skip session files
                
                filepath = os.path.join(TELEGRAM_DIR, filename)
                if os.path.isfile(filepath):
                    file_size = os.path.getsize(filepath)
                    files.append({
                        'name': filename,
                        'size': file_size,
                        'size_mb': round(file_size / (1024 * 1024), 2)
                    })
        
        return jsonify(files)
    except Exception as e:
        log(f"❌ Error getting downloaded files: {str(e)}")
        return jsonify({'error': 'Failed to get downloaded files'}), 500

@telegram_bp.route('/download_file/<filename>')
def download_file(filename):
    """Download a specific Telegram file"""
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        filepath = os.path.join(TELEGRAM_DIR, filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        log(f"❌ Error downloading file {filename}: {str(e)}")
        return jsonify({'error': 'Download failed'}), 500

@telegram_bp.route('/check_auth', methods=['POST'])
def check_telegram_auth():
    """Check if Telegram client is authorized"""
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    api_id = data.get('api_id')
    api_hash = data.get('api_hash')
    
    if not api_id or not api_hash:
        return jsonify({'error': 'API ID and API Hash are required'}), 400
    
    try:
        # Try to initialize client
        success = run_async_function(telegram_manager.initialize_client, api_id, api_hash)
        
        if success:
            return jsonify({'authorized': True, 'message': 'Telegram client is authorized'})
        else:
            return jsonify({'authorized': False, 'message': 'Telegram client is not authorized'})
            
    except Exception as e:
        log(f"❌ Error checking Telegram auth: {str(e)}")
        return jsonify({'authorized': False, 'message': f'Error: {str(e)}'})

@telegram_bp.route('/get_progress', methods=['GET'])
def get_progress():
    """Get the last processed message ID"""
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    last_id = telegram_manager.load_last_id()
    return jsonify({'last_id': last_id})

