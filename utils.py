import os
from datetime import datetime
from src.config import LOG_FILE

def log(msg):
    """Centralized logging function"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {msg}"
    
    # Ensure log file directory exists
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{log_message}\n")
    
    # Also print to console for debugging
    print(log_message)

def clear_log():
    """Clear the log file"""
    with open(LOG_FILE, 'w') as f:
        f.write("")

def get_log_content():
    """Get the current log content"""
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

