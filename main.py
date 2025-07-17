import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.config import SECRET_KEY
from src.routes.auth import auth_bp
from src.routes.audio import audio_bp
from src.routes.telegram import telegram_bp
from src.routes.common import common_bp
from src.utils import clear_log, log

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = SECRET_KEY

# Enable CORS for all routes
CORS(app)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(audio_bp, url_prefix='/api/audio')
app.register_blueprint(telegram_bp, url_prefix='/api/telegram')
app.register_blueprint(common_bp, url_prefix='/api')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    # Clear log on startup
    clear_log()
    log("🚀 Starting Telegram Audio App...")
    
    app.run(host='0.0.0.0', port=8000, debug=True)

