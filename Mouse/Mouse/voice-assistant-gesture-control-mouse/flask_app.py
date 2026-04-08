from flask import Flask, render_template, request, jsonify, Response, session, redirect, url_for
import cv2
import threading
import json
import time
import sys
import os
import sqlite3
from datetime import datetime
import hashlib

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import modules with error handling
gesture_available = False
voice_available = False

try:
    from smooth_gesture_control import SmoothGestureController
    gesture_available = True
    print("Gesture control module loaded successfully")
except ImportError as e:
    print(f"Warning: Could not import gesture control: {e}")

try:
    from robust_voice_control import voice_controller
    voice_available = True
    print("Voice control module loaded successfully")
except ImportError as e:
    print(f"Warning: Could not import voice control: {e}")

app = Flask(__name__)
app.secret_key = 'pixel_secret_key_2024'

# Initialize database
def init_db():
    conn = sqlite3.connect('pixel_app.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Contacts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            subject TEXT NOT NULL,
            message TEXT NOT NULL,
            newsletter BOOLEAN,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create admin user if not exists
    cursor.execute('SELECT * FROM users WHERE username = ?', ('admin',))
    if not cursor.fetchone():
        admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
        cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                      ('admin', 'admin@pixel.com', admin_password))
    
    conn.commit()
    conn.close()

init_db()

# Global variables
gesture_thread = None
voice_thread = None
is_gesture_active = False
is_voice_active = False
active_controller = None

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('welcome'))
    return render_template('home.html')

@app.route('/welcome')
def welcome():
    return render_template('welcome.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/auth/login', methods=['POST'])
def auth_login():
    data = request.get_json()
    username = data.get('username')
    password = hashlib.sha256(data.get('password').encode()).hexdigest()
    
    conn = sqlite3.connect('pixel_app.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, username FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        session['user_id'] = user[0]
        session['username'] = user[1]
        if username == 'admin':
            return jsonify({'status': 'success', 'redirect': '/admin/dashboard'})
        return jsonify({'status': 'success', 'redirect': '/'})
    return jsonify({'status': 'error', 'message': 'Invalid credentials'})

@app.route('/auth/register', methods=['POST'])
def auth_register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = hashlib.sha256(data.get('password').encode()).hexdigest()
    
    conn = sqlite3.connect('pixel_app.db')
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                      (username, email, password))
        conn.commit()
        conn.close()
        return jsonify({'status': 'success', 'message': 'Registration successful'})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'status': 'error', 'message': 'Username or email already exists'})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('username') != 'admin':
        return redirect(url_for('login'))
    return render_template('admin_dashboard.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/developer')
def developer():
    return render_template('developer.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    try:
        data = request.get_json()
        conn = sqlite3.connect('pixel_app.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO contacts (name, email, subject, message, newsletter)
            VALUES (?, ?, ?, ?, ?)
        ''', (data['name'], data['email'], data['subject'], data['message'], data['newsletter']))
        conn.commit()
        conn.close()
        return jsonify({'status': 'success', 'message': 'Contact form submitted successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/admin/contacts')
def admin_contacts():
    if 'user_id' not in session or session.get('username') != 'admin':
        return jsonify({'error': 'Unauthorized'})
    try:
        conn = sqlite3.connect('pixel_app.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM contacts ORDER BY created_at DESC')
        contacts = cursor.fetchall()
        conn.close()
        return jsonify({'contacts': contacts})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/admin/users')
def admin_users():
    if 'user_id' not in session or session.get('username') != 'admin':
        return jsonify({'error': 'Unauthorized'})
    try:
        conn = sqlite3.connect('pixel_app.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, email, created_at FROM users ORDER BY created_at DESC')
        users = cursor.fetchall()
        conn.close()
        return jsonify({'users': users})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/start_gesture', methods=['POST'])
def start_gesture():
    global is_gesture_active, gesture_thread, active_controller
    
    if not is_gesture_active:
        try:
            def run_gesture():
                global is_gesture_active, active_controller
                try:
                    from smooth_gesture_control import SmoothGestureController
                    active_controller = SmoothGestureController()
                    active_controller.start()
                except Exception as e:
                    print(f"Gesture control error: {e}")
                finally:
                    is_gesture_active = False
                    active_controller = None
            
            gesture_thread = threading.Thread(target=run_gesture, daemon=True)
            gesture_thread.start()
            is_gesture_active = True
            return jsonify({'status': 'success', 'message': 'Gesture control started. Camera window should open.'})
        except Exception as e:
            print(f"Start gesture error: {e}")
            return jsonify({'status': 'error', 'message': f'Failed to start: {str(e)}'})
    else:
        return jsonify({'status': 'info', 'message': 'Gesture control already active'})

@app.route('/stop_gesture', methods=['POST'])
def stop_gesture():
    global is_gesture_active, active_controller
    
    print("Stop gesture endpoint called")
    
    # Prevent multiple stop calls
    if not is_gesture_active:
        return jsonify({'status': 'info', 'message': 'Gesture control already stopped'})
    
    try:
        if active_controller:
            print("Stopping active controller")
            active_controller.stop()
            active_controller = None
        
        is_gesture_active = False
        print("Gesture control stopped")
        return jsonify({'status': 'success', 'message': 'Gesture control stopped successfully'})
    except Exception as e:
        print(f"Stop gesture error: {e}")
        is_gesture_active = False
        active_controller = None
        return jsonify({'status': 'success', 'message': 'Gesture control stopped'})

@app.route('/start_voice', methods=['POST'])
def start_voice():
    global voice_thread, is_voice_active
    
    if is_voice_active:
        return jsonify({'status': 'info', 'message': 'Voice control already active'})
    
    try:
        def run_voice():
            global is_voice_active
            try:
                from robust_voice_control import voice_controller
                if voice_controller and not voice_controller.is_listening:
                    voice_controller.start_listening()
            except Exception as e:
                print(f"Voice control thread error: {e}")
            finally:
                is_voice_active = False
        
        voice_thread = threading.Thread(target=run_voice, daemon=True)
        voice_thread.start()
        is_voice_active = True
        return jsonify({'status': 'success', 'message': 'Voice control started successfully'})
    except Exception as e:
        is_voice_active = False
        return jsonify({'status': 'success', 'message': 'Voice control started'})

@app.route('/stop_voice', methods=['POST'])
def stop_voice():
    global is_voice_active
    
    if not is_voice_active:
        return jsonify({'status': 'info', 'message': 'Voice control already stopped'})
    
    try:
        from robust_voice_control import voice_controller
        if voice_controller and voice_controller.is_listening:
            voice_controller.stop_listening()
        is_voice_active = False
        return jsonify({'status': 'success', 'message': 'Voice control stopped'})
    except Exception as e:
        is_voice_active = False
        return jsonify({'status': 'success', 'message': 'Voice control stopped'})

@app.route('/process_voice', methods=['POST'])
def process_voice():
    try:
        from robust_voice_control import process_voice_command
        data = request.get_json()
        command = data.get('command', '')
        
        if command:
            success = process_voice_command(command)
            if success:
                return jsonify({'status': 'success', 'response': 'Command executed successfully'})
            else:
                return jsonify({'status': 'warning', 'response': 'Command not recognized'})
        else:
            return jsonify({'status': 'error', 'message': 'No command provided'})
    except ImportError:
        return jsonify({'status': 'error', 'message': 'Voice control module not available'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/get_commands', methods=['GET'])
def get_commands():
    try:
        commands = [
            "pixel open notepad", "pixel open calculator", "pixel open chrome",
            "pixel close window", "pixel take screenshot", "pixel volume up",
            "pixel volume down", "pixel mute sound", "pixel what time",
            "pixel what date", "pixel search google cats", "pixel smart search",
            "pixel play music", "pixel pause music", "pixel copy text",
            "pixel paste text", "pixel save file", "pixel new tab",
            "pixel close tab", "pixel go back", "pixel refresh page",
            "pixel start gesture", "pixel stop gesture", "pixel tell me a joke",
            "pixel flip a coin", "pixel roll dice", "pixel battery status",
            "pixel create folder", "pixel send email", "pixel set reminder",
            "pixel read clipboard", "pixel clear clipboard", "pixel zoom in",
            "pixel zoom out", "pixel full screen", "pixel find text",
            "pixel print page", "pixel open downloads", "pixel empty trash",
            "pixel system performance", "pixel what can you do"
        ]
        return jsonify({'commands': commands})
    except Exception as e:
        return jsonify({'commands': [], 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)