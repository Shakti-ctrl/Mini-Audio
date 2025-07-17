import subprocess
import os
import json
import zipfile
from werkzeug.utils import secure_filename
from src.config import AUDIO_DIR, TMP_DIR, UPLOAD_DIR, JSON_CACHE
from src.utils import log

def search_youtube_channel(channel_url):
    """Search for videos in a YouTube channel"""
    try:
        log(f"🔍 Searching YouTube channel: {channel_url}")
        result = subprocess.run(
            f"yt-dlp --flat-playlist --dump-json '{channel_url}' > '{JSON_CACHE}'", 
            shell=True, 
            capture_output=True, 
            text=True
        )
        
        if result.returncode == 0:
            log("✅ YouTube search completed successfully")
            return True
        else:
            log(f"❌ YouTube search failed: {result.stderr}")
            return False
    except Exception as e:
        log(f"❌ Error searching YouTube channel: {str(e)}")
        return False

def get_youtube_videos():
    """Get the list of videos from the JSON cache"""
    videos = []
    if os.path.exists(JSON_CACHE):
        try:
            with open(JSON_CACHE, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and 'title' in line:
                        try:
                            video_data = json.loads(line)
                            videos.append(video_data)
                        except json.JSONDecodeError:
                            continue
            log(f"📋 Loaded {len(videos)} videos from cache")
        except Exception as e:
            log(f"❌ Error reading video cache: {str(e)}")
    return videos

def download_and_extract_audio(video_ids):
    """Download videos and extract audio"""
    log("📥 Starting audio extraction...")
    extracted_files = []
    
    for vid in video_ids:
        try:
            url = f"https://www.youtube.com/watch?v={vid}"
            log(f"🔗 Downloading: {url}")
            
            # Download and extract audio directly to AUDIO_DIR
            result = subprocess.run([
                "yt-dlp", "-x", "--audio-format", "mp3", 
                "--embed-thumbnail", "--add-metadata",
                "-o", f"{AUDIO_DIR}/%(title)s.%(ext)s",
                url
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                log(f"✅ Successfully extracted audio for: {vid}")
                # Find the extracted file
                for file in os.listdir(AUDIO_DIR):
                    if file.endswith(".mp3") and file not in extracted_files:
                        extracted_files.append(file)
                        break
            else:
                log(f"❌ Failed to extract audio for {vid}: {result.stderr}")
                
        except Exception as e:
            log(f"❌ Error processing video {vid}: {str(e)}")
    
    log(f"🎉 Audio extraction completed. {len(extracted_files)} files extracted.")
    return extracted_files

def extract_audio_from_file(filepath):
    """Extract audio from uploaded video file"""
    try:
        title = os.path.splitext(os.path.basename(filepath))[0]
        out_path = os.path.join(AUDIO_DIR, f"{title}.mp3")
        log(f"🎞️ Extracting audio from file: {filepath}")
        
        result = subprocess.run([
            "ffmpeg", "-i", filepath, "-q:a", "0", "-map", "a", out_path
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            os.remove(filepath)
            log(f"✅ Extracted and saved: {out_path}")
            return os.path.basename(out_path)
        else:
            log(f"❌ FFmpeg extraction failed: {result.stderr}")
            return None
            
    except Exception as e:
        log(f"❌ Error extracting audio from file: {str(e)}")
        return None

def get_audio_files():
    """Get list of extracted audio files"""
    try:
        audio_files = sorted([f for f in os.listdir(AUDIO_DIR) if f.endswith(".mp3")])
        return audio_files
    except Exception as e:
        log(f"❌ Error getting audio files: {str(e)}")
        return []

def create_zip_archive(selected_files):
    """Create ZIP archive of selected audio files"""
    try:
        zip_path = os.path.join(TMP_DIR, "audios.zip")
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for file in selected_files:
                file_path = os.path.join(AUDIO_DIR, file)
                if os.path.exists(file_path):
                    zipf.write(file_path, arcname=file)
        
        log(f"📦 Created ZIP archive with {len(selected_files)} files")
        return zip_path
    except Exception as e:
        log(f"❌ Error creating ZIP archive: {str(e)}")
        return None

def save_uploaded_file(file):
    """Save uploaded file to upload directory"""
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_DIR, filename)
        file.save(filepath)
        log(f"📤 Uploaded file saved: {filename}")
        return filepath
    except Exception as e:
        log(f"❌ Error saving uploaded file: {str(e)}")
        return None

