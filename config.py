import os

# Flask Configuration
SECRET_KEY = 'securekey123'

# Directory Configuration
WORK_DIR = os.path.expanduser("~/telegram_audio_web")
AUDIO_DIR = os.path.join(WORK_DIR, "audio")
TMP_DIR = os.path.join(WORK_DIR, "temp")
UPLOAD_DIR = os.path.join(WORK_DIR, "uploads")
TELEGRAM_DIR = os.path.join(WORK_DIR, "telegram")
JSON_CACHE = os.path.join(WORK_DIR, "videos.json")
TELEGRAM_CACHE = os.path.join(WORK_DIR, "telegram_messages.json")
LOG_FILE = os.path.join(WORK_DIR, "log.txt")
PROGRESS_FILE = os.path.join(WORK_DIR, "last_id.txt")

# Ensure directories exist
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(TMP_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(TELEGRAM_DIR, exist_ok=True)

# Authentication
USERS = {'admin': 'password123'}

# Default URLs
DEFAULT_CHANNEL_URL = "https://www.youtube.com/@ncert_audio_books"

# Telegram Configuration (using real provided credentials)
TELEGRAM_API_ID = os.getenv('TELEGRAM_API_ID', '28403662')
TELEGRAM_API_HASH = os.getenv('TELEGRAM_API_HASH', '079509d4ac7f209a1a58facd00d6ff5a')
TELEGRAM_SESSION_NAME = 'telegram_session'
DEFAULT_SOURCE_CHANNEL = 'https://t.me/arjunaa_neet_25'
DEFAULT_GROUP_INVITE = 'Fep9YbeAlNM5ZmU1'

