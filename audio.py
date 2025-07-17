from flask import Blueprint, request, jsonify, send_file, session, redirect
from threading import Thread
import os
from src.audio_module import (
    search_youtube_channel, get_youtube_videos, download_and_extract_audio,
    extract_audio_from_file, get_audio_files, create_zip_archive, save_uploaded_file
)
from src.config import AUDIO_DIR, DEFAULT_CHANNEL_URL
from src.utils import log

audio_bp = Blueprint('audio', __name__)

@audio_bp.route('/search_youtube', methods=['POST'])
def search_youtube():
    """Search YouTube channel for videos"""
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    channel_url = data.get('channel_url', DEFAULT_CHANNEL_URL)
    
    # Run search in background thread
    Thread(target=search_youtube_channel, args=(channel_url,)).start()
    
    return jsonify({'status': 'search_started', 'message': 'YouTube search started'})

@audio_bp.route('/get_videos', methods=['GET'])
def get_videos():
    """Get list of videos from YouTube search"""
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    videos = get_youtube_videos()
    return jsonify(videos)

@audio_bp.route('/extract_audio', methods=['POST'])
def extract_audio():
    """Extract audio from selected YouTube videos"""
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    video_ids = data.get('video_ids', [])
    
    if not video_ids:
        return jsonify({'error': 'No videos selected'}), 400
    
    # Run extraction in background thread
    Thread(target=download_and_extract_audio, args=(video_ids,)).start()
    
    return jsonify({'status': 'extraction_started', 'message': f'Audio extraction started for {len(video_ids)} videos'})

@audio_bp.route('/get_audio_files', methods=['GET'])
def get_audio_files_route():
    """Get list of extracted audio files"""
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    audio_files = get_audio_files()
    return jsonify(audio_files)

@audio_bp.route('/play/<filename>')
def play_audio(filename):
    """Stream audio file for playing"""
    if 'user' not in session:
        return redirect('/login')
    
    try:
        return send_file(os.path.join(AUDIO_DIR, filename))
    except Exception as e:
        log(f"❌ Error playing audio file {filename}: {str(e)}")
        return "File not found", 404

@audio_bp.route('/download/<filename>')
def download_audio(filename):
    """Download individual audio file"""
    if 'user' not in session:
        return redirect('/login')
    
    try:
        return send_file(os.path.join(AUDIO_DIR, filename), as_attachment=True)
    except Exception as e:
        log(f"❌ Error downloading audio file {filename}: {str(e)}")
        return "File not found", 404

@audio_bp.route('/download_zip', methods=['POST'])
def download_zip():
    """Download ZIP archive of selected audio files"""
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    selected_files = data.get('files', [])
    
    if not selected_files:
        return jsonify({'error': 'No files selected'}), 400
    
    zip_path = create_zip_archive(selected_files)
    if zip_path:
        return send_file(zip_path, as_attachment=True, download_name="audios.zip")
    else:
        return jsonify({'error': 'Failed to create ZIP archive'}), 500

@audio_bp.route('/upload_video', methods=['POST'])
def upload_video():
    """Upload video file for audio extraction"""
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    filepath = save_uploaded_file(file)
    if filepath:
        # Extract audio in background thread
        Thread(target=extract_audio_from_file, args=(filepath,)).start()
        return jsonify({'status': 'upload_successful', 'message': 'File uploaded and audio extraction started'})
    else:
        return jsonify({'error': 'Failed to save uploaded file'}), 500

