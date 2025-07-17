from flask import Blueprint, request, jsonify, session, render_template_string
from src.config import USERS

auth_bp = Blueprint('auth', __name__)

LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Login - Telegram Audio App</title>
    <style>
        body { 
            font-family: sans-serif; 
            background: #f8f8f8; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            height: 100vh; 
            margin: 0; 
        }
        .login-form { 
            background: white; 
            padding: 30px; 
            border-radius: 10px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
            width: 300px; 
        }
        .login-form h2 { text-align: center; margin-bottom: 20px; color: #333; }
        .login-form input { 
            width: 100%; 
            padding: 10px; 
            margin: 10px 0; 
            border: 1px solid #ddd; 
            border-radius: 5px; 
            box-sizing: border-box; 
        }
        .login-form button { 
            width: 100%; 
            padding: 12px; 
            background: #007bff; 
            color: white; 
            border: none; 
            border-radius: 5px; 
            cursor: pointer; 
            font-size: 16px; 
        }
        .login-form button:hover { background: #0056b3; }
        .error { color: red; text-align: center; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="login-form">
        <h2>🎧📱 Telegram Audio App</h2>
        <form method="post">
            <input name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
        {% if error %}
            <div class="error">{{ error }}</div>
        {% endif %}
    </div>
</body>
</html>
'''

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if USERS.get(username) == password:
            session['user'] = username
            return jsonify({'status': 'success', 'redirect': '/'})
        else:
            if request.content_type == 'application/json':
                return jsonify({'error': 'Invalid credentials'}), 401
            else:
                return render_template_string(LOGIN_TEMPLATE, error="Invalid credentials"), 401
    
    # GET request - show login form
    return render_template_string(LOGIN_TEMPLATE)

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Handle user logout"""
    session.clear()
    return jsonify({'status': 'success', 'message': 'Logged out successfully'})

@auth_bp.route('/check_auth', methods=['GET'])
def check_auth():
    """Check if user is authenticated"""
    if 'user' in session:
        return jsonify({'authenticated': True, 'user': session['user']})
    else:
        return jsonify({'authenticated': False})

