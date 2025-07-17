# 🚀 Deployment Guide - Telegram Audio App

## Quick Start

### Local Development
1. Extract the application files
2. Navigate to the `telegram_audio_app` directory
3. Activate the virtual environment: `source venv/bin/activate`
4. Run the application: `python src/main.py`
5. Access at `http://localhost:8000`
6. Login with username: `admin`, password: `password123`

### Production Deployment Options

#### Option 1: Using Manus Service Deployment
```bash
# Deploy the Flask backend (recommended for production)
cd telegram_audio_app
# The application will be automatically deployed to a public URL
```

#### Option 2: Manual Server Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Install system dependencies
sudo apt-get update
sudo apt-get install ffmpeg

# Configure environment variables
export TELEGRAM_API_ID="your_api_id"
export TELEGRAM_API_HASH="your_api_hash"
export FLASK_ENV="production"

# Run with production WSGI server
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 src.main:app
```

#### Option 3: Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN apt-get update && apt-get install -y ffmpeg
RUN pip install -r requirements.txt

EXPOSE 8000
CMD ["python", "src/main.py"]
```

## Configuration

### Environment Variables
- `TELEGRAM_API_ID`: Your Telegram API ID
- `TELEGRAM_API_HASH`: Your Telegram API Hash
- `SECRET_KEY`: Flask secret key for sessions
- `FLASK_ENV`: Set to "production" for production deployment

### Security Considerations
1. **Change Default Credentials**: Update login credentials in `src/config.py`
2. **Secure API Keys**: Use environment variables for sensitive data
3. **HTTPS**: Use HTTPS in production environments
4. **Firewall**: Configure appropriate firewall rules

### Directory Permissions
Ensure the application has write permissions to:
- `audio/` - For extracted audio files
- `temp/` - For temporary processing
- `uploads/` - For uploaded videos
- `telegram/` - For downloaded Telegram media
- `log.txt` - For application logging

## Features Overview

### 🎧 Audio Extractor
- YouTube channel video search and audio extraction
- Local video file upload and processing
- Bulk audio extraction with progress tracking
- Audio file management and ZIP download
- Real-time progress monitoring

### 📱 Telegram Extractor/Forwarder
- Telegram channel message browsing
- Advanced message filtering (text, photos, videos, documents, audio)
- Message forwarding to target channels
- Media file download from messages
- Bulk operations with progress tracking

### 🔧 Common Features
- User authentication system
- Tabbed interface for easy navigation
- Real-time logging and status updates
- Responsive design for mobile and desktop
- Comprehensive error handling

## API Documentation

### Authentication Endpoints
- `POST /login` - User authentication
- `POST /logout` - User logout
- `GET /check_auth` - Authentication status

### Audio Extractor API
- `POST /api/audio/search_youtube` - Search YouTube channel
- `POST /api/audio/extract_audio` - Extract audio from videos
- `GET /api/audio/get_audio_files` - List extracted audio files
- `POST /api/audio/upload_video` - Upload video file

### Telegram Extractor API
- `POST /api/telegram/search_messages` - Search channel messages
- `POST /api/telegram/forward_messages` - Forward messages
- `POST /api/telegram/download_media` - Download media files
- `GET /api/telegram/get_messages` - Get cached messages

### Common API
- `GET /api/log` - Application logs
- `POST /api/clear_log` - Clear logs

## Troubleshooting

### Common Issues
1. **Port Already in Use**: Change port in `src/main.py`
2. **Permission Denied**: Check directory permissions
3. **FFmpeg Not Found**: Install FFmpeg system package
4. **Telegram Auth Failed**: Verify API credentials

### Performance Optimization
- Use production WSGI server (gunicorn, uwsgi)
- Configure reverse proxy (nginx, apache)
- Enable gzip compression
- Set up proper caching headers

## Monitoring and Maintenance

### Log Monitoring
- Application logs are available at `/api/log`
- System logs should be monitored for errors
- Set up log rotation for production

### Health Checks
- Application status: `GET /check_auth`
- API endpoints return appropriate HTTP status codes
- Monitor disk space for media files

### Backup Strategy
- Backup extracted audio files regularly
- Backup Telegram session files
- Backup application configuration

## Support and Updates

### Getting Help
1. Check application logs for error details
2. Verify all dependencies are installed
3. Ensure proper API configuration
4. Review this deployment guide

### Updating the Application
1. Backup current installation
2. Update source code
3. Update dependencies: `pip install -r requirements.txt`
4. Restart the application

## Security Best Practices

1. **Authentication**: Change default login credentials
2. **API Keys**: Store sensitive data in environment variables
3. **Network**: Use HTTPS and proper firewall configuration
4. **Updates**: Keep dependencies updated regularly
5. **Monitoring**: Set up proper logging and monitoring

## Performance Considerations

- **Concurrent Users**: Use multiple worker processes
- **File Storage**: Consider cloud storage for large files
- **Database**: Consider using a proper database for production
- **Caching**: Implement caching for frequently accessed data
- **Rate Limiting**: Implement rate limiting for API endpoints

