# 🎧📱 Telegram Audio App

A comprehensive Flask web application that combines YouTube audio extraction and Telegram message management capabilities. This application provides a unified interface for extracting audio from YouTube videos and managing Telegram channel messages with advanced filtering and forwarding features.

## Features

### 🎧 Audio Extractor
- **YouTube Channel Search**: Search and browse videos from any YouTube channel
- **Bulk Audio Extraction**: Select multiple videos and extract audio in MP3 format
- **Local Video Upload**: Upload local video files for audio extraction
- **Audio Management**: Play, download, and organize extracted audio files
- **Batch Download**: Download multiple audio files as a ZIP archive
- **Progress Tracking**: Real-time progress updates and logging

### 📱 Telegram Extractor/Forwarder
- **Channel Message Search**: Browse messages from any Telegram channel or group
- **Advanced Filtering**: Filter messages by type (text, photos, videos, documents, audio)
- **Message Forwarding**: Forward selected messages to target channels/groups
- **Media Download**: Download media files from selected messages
- **Bulk Operations**: Select all functionality for efficient batch processing
- **Progress Tracking**: Real-time status updates and error handling

### 🔧 Common Features
- **User Authentication**: Secure login system
- **Tabbed Interface**: Clean, organized UI with separate tabs for each functionality
- **Real-time Logging**: Live application logs with automatic refresh
- **Responsive Design**: Works on both desktop and mobile devices
- **Error Handling**: Comprehensive error handling and user feedback

## Installation

### Prerequisites
- Python 3.11+
- FFmpeg (for audio extraction)
- yt-dlp (for YouTube downloads)
- Telegram API credentials (for Telegram functionality)

### Setup Instructions

1. **Clone or extract the application**:
   ```bash
   cd telegram_audio_app
   ```

2. **Activate the virtual environment**:
   ```bash
   source venv/bin/activate
   ```

3. **Install dependencies** (already included):
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Telegram API** (optional):
   - Get your API ID and API Hash from https://my.telegram.org/apps
   - Update `src/config.py` with your credentials or use environment variables:
     ```bash
     export TELEGRAM_API_ID="your_api_id"
     export TELEGRAM_API_HASH="your_api_hash"
     ```

5. **Run the application**:
   ```bash
   python src/main.py
   ```

6. **Access the application**:
   - Open your browser and go to `http://localhost:8000`
   - Login with username: `admin`, password: `password123`

## Usage

### Audio Extractor

1. **Search YouTube Videos**:
   - Enter a YouTube channel URL (e.g., `https://www.youtube.com/@channel_name`)
   - Click "🔍 Search Videos" to load available videos
   - Use "Select All Videos" checkbox for bulk selection

2. **Extract Audio**:
   - Select desired videos from the list
   - Click "🎵 Extract Selected" to start audio extraction
   - Monitor progress in the log section

3. **Manage Audio Files**:
   - Play audio files directly in the browser
   - Download individual files or create ZIP archives
   - Use "🔄 Refresh" to update the audio file list

4. **Upload Local Videos**:
   - Click the upload area or drag & drop video files
   - Audio will be automatically extracted from uploaded videos

### Telegram Extractor/Forwarder

1. **Setup Telegram Access**:
   - Enter your Telegram API ID and API Hash
   - Provide the source channel URL (e.g., `https://t.me/channel_name` or `@channel_name`)
   - Select message filter type (All, Text, Photos, Videos, Documents, Audio)

2. **Search Messages**:
   - Click "🔍 Search Messages" to load channel messages
   - Use "Select All Messages" checkbox for bulk selection
   - Review message details including type, date, and file information

3. **Forward Messages**:
   - Enter target channel/group URL
   - Select messages to forward
   - Click "📤 Forward Selected" to start forwarding

4. **Download Media**:
   - Select messages containing media files
   - Click "💾 Download Selected Media" to download files locally

## Configuration

### Application Settings
Edit `src/config.py` to customize:
- Working directories
- Default YouTube channel
- Telegram API credentials
- User authentication credentials

### Directory Structure
```
telegram_audio_web/
├── audio/          # Extracted audio files
├── temp/           # Temporary files
├── uploads/        # Uploaded video files
├── telegram/       # Downloaded Telegram media
└── log.txt         # Application logs
```

## API Endpoints

### Authentication
- `POST /login` - User login
- `POST /logout` - User logout
- `GET /check_auth` - Check authentication status

### Audio Extractor
- `POST /api/audio/search_youtube` - Search YouTube channel
- `GET /api/audio/get_videos` - Get cached video list
- `POST /api/audio/extract_audio` - Extract audio from videos
- `GET /api/audio/get_audio_files` - Get extracted audio files
- `POST /api/audio/upload_video` - Upload video file

### Telegram Extractor
- `POST /api/telegram/search_messages` - Search channel messages
- `GET /api/telegram/get_messages` - Get cached messages
- `POST /api/telegram/forward_messages` - Forward selected messages
- `POST /api/telegram/download_media` - Download media files

### Common
- `GET /api/log` - Get application logs
- `POST /api/clear_log` - Clear application logs

## Security Notes

- Change default login credentials in production
- Keep Telegram API credentials secure
- Use HTTPS in production environments
- Regularly update dependencies

## Troubleshooting

### Common Issues

1. **YouTube Download Fails**:
   - Ensure yt-dlp is installed and updated
   - Check internet connection
   - Verify YouTube channel URL format

2. **Telegram Authentication Fails**:
   - Verify API ID and API Hash are correct
   - Ensure Telegram account is authorized
   - Check network connectivity

3. **Audio Extraction Fails**:
   - Ensure FFmpeg is installed and in PATH
   - Check available disk space
   - Verify video file format is supported

4. **Permission Errors**:
   - Check file system permissions
   - Ensure write access to working directories

### Log Analysis
- Monitor the application log for detailed error messages
- Use the "🗑️ Clear Log" button to reset logs
- Check browser console for frontend errors

## Dependencies

- Flask 3.1.1 - Web framework
- Telethon 1.40.0 - Telegram client library
- flask-cors 6.0.0 - Cross-origin resource sharing
- yt-dlp - YouTube video downloader
- FFmpeg - Audio/video processing

## License

This application is provided as-is for educational and personal use.

## Support

For issues and questions:
1. Check the application logs for error details
2. Verify all dependencies are properly installed
3. Ensure proper configuration of API credentials
4. Review the troubleshooting section above

