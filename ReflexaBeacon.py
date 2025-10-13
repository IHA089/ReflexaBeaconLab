from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager, set_access_cookies, unset_jwt_cookies
from flask_cors import CORS
import sqlite3, logging
from werkzeug.security import generate_password_hash, check_password_hash
import os, urllib3, html, requests
import smtplib, ssl, uuid
from email.mime.text import MIMEText

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

lab_type = "XSS"
lab_name = "ReflexaBeaconLab"
web_app_name = "ReflexaBeacon"

ReflexaBeacon = Flask(__name__)
ReflexaBeacon.secret_key = "vulnerable_lab_by_IHA089"

ReflexaBeacon.config["JWT_SECRET_KEY"] = "Hacking_is_our_vision_and_mission"  
ReflexaBeacon.config["JWT_TOKEN_LOCATION"] = ["cookies"]
ReflexaBeacon.config["JWT_COOKIE_SECURE"] = True  
ReflexaBeacon.config["JWT_COOKIE_CSRF_PROTECT"] = True  

jwt = JWTManager(ReflexaBeacon)

print(web_app_name)

CORS(ReflexaBeacon, supports_credentials=True)

def init_db():
    db_path = os.path.join(os.getcwd(), "Labs", lab_type, lab_name, 'database.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            profile_pic TEXT,
            social_links TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')

    cursor.execute('''
        CREATE TABLE ai_services (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            icon_url TEXT,
            price_in_tokens INTEGER NOT NULL
        );
    ''')

    cursor.execute('''
        CREATE TABLE user_ais (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            ai_service_id INTEGER NOT NULL,
            tokens_purchased INTEGER NOT NULL DEFAULT 0,
            purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (ai_service_id) REFERENCES ai_services (id)
        );
    ''')

    sample_ais = [
        ('GPT-4', 'A powerful large language model for creative and technical tasks.', 'images/gpt4.png', 100),
        ('DALL-E 3', 'Generates stunning images from text descriptions.', 'images/dalle3.png', 150),
        ('GitHub Copilot', 'An AI pair programmer that helps write code faster.', 'images/copilot.png', 75),
        ('Midjourney', 'Creates beautiful and complex images from prompts.', 'images/midjourney.png', 120),
        ('AI Video Editor', 'Automatically edits videos with AI assistance.', 'images/video_editor.png', 200),
        ('Music Composer AI', 'Generates original music compositions.', 'images/music_ai.png', 180),
        ('Voice Synthesizer', 'Converts text into natural-sounding speech.', 'images/voice_synth.png', 90),
        ('Code Debugger AI', 'Finds and suggests fixes for bugs in your code.', 'images/debugger.png', 110),
        ('Financial Analyst AI', 'Analyzes market data and provides insights.', 'images/finance_ai.png', 250)
    ]

    cursor.executemany("INSERT OR IGNORE INTO ai_services (name, description, icon_url, price_in_tokens) VALUES (?, ?, ?, ?)", sample_ais)
    conn.commit()
    conn.close()


def check_database():
    db_path = os.path.join(os.getcwd(), "Labs", lab_type, lab_name, 'database.db')
    if not os.path.isfile(db_path):
        init_db()

check_database()

def get_db_connection():
    db_path = os.path.join(os.getcwd(), "Labs", lab_type, lab_name, 'database.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def create_mail_account():
    mail_db_path = os.path.join(os.getcwd(), "IHA089_Mail", "mail_users.db")
    username = "Reflexa Beacon"
    email="ReflexaBeacon@iha089.org"
    password="a6a4eee26ea3f3330f7c5716b16921e6"
    usr_uuid = str(uuid.uuid4())
    conn = sqlite3.connect(mail_db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE email = ?", (email,))
    conn.commit()
    cursor.execute("INSERT INTO users (username, email, password, uuid) VALUES (?, ?, ?, ?)", (username, email, password, usr_uuid))
    conn.commit()
    conn.close()

create_mail_account()

def mail_sender(to_email, subject, body):
    try:
        sender = "ReflexaBeacon@iha089.org"
        password = "IHA089@Labs"  
        recipient = to_email

        msg = MIMEText(body, "plain")
        msg["From"] = sender
        msg["To"] = recipient
        msg["Subject"] = subject

        with smtplib.SMTP_SSL("127.0.0.1", 465) as server:
            server.sendmail(sender, [recipient], msg.as_string())
        return True
    except Exception as e:
        print(e)
        return False
        
@ReflexaBeacon.route('/')
def home():
    return render_template('index.html')

@ReflexaBeacon.route('/ai')
def ai_page():
    conn = get_db_connection()
    ai_services = conn.execute('SELECT * FROM ai_services').fetchall()
    conn.close()
    return render_template('ai.html', ais=ai_services)

@ReflexaBeacon.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({"msg": "Missing JSON in request"}), 400

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"msg": "Missing email or password"}), 400

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            access_token = create_access_token(identity=str(user['id']))
            response = jsonify({"msg": "Login successful"})
            set_access_cookies(response, access_token)
            return response
        else:
            return jsonify({"msg": "Invalid email or password"}), 401
    
    return render_template('login.html')

@ReflexaBeacon.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        password_hash = generate_password_hash(password)

        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                         (username, email, password_hash))
            conn.commit()
            safe_user_name = html.escape(username)
            subject = f"Your Registration Is Confirmed – Welcome to {web_app_name}"
            support_email="iha089-labs@iha089.org"
            login_url = "https://iha089-labs.in/login"
            bdcontent = f"""
<p>Hello {safe_user_name},</p>

<p>Thank you for registering with <strong>{web_app_name}</strong>. Your account has been successfully created.</p>

<p>You can now log in and start exploring all the features we offer:<br>
👉 <a href="https://{web_app_name.lower()}.iha089-labs.in" target="_blank" rel="noopener">Login Link</a>
</p>

<p>If you have any questions or need assistance, feel free to contact our support team at 
<a href="mailto:{support_email}">{support_email}</a>.
</p>

<p>Welcome aboard,<br>
The <strong>IHA089</strong> Team</p>
""" 
            if(mail_sender(email, subject, bdcontent)):
                error_message="code sent"
            else:  
                return jsonify({"error": "Mail server is not responding"}), 500
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            conn.close()
            return render_template('register.html', error='Username or email already exists.')

    return render_template('register.html')

@ReflexaBeacon.route('/logout', methods=['POST'])
def logout():
    response = jsonify({"msg": "Logout successful"})
    unset_jwt_cookies(response)
    return response

@ReflexaBeacon.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    user_id = get_jwt_identity()
    conn = get_db_connection()

    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    
    user_ais_query = """
        SELECT ai_services.name, ai_services.description, ai_services.icon_url, user_ais.tokens_purchased
        FROM ai_services
        JOIN user_ais ON ai_services.id = user_ais.ai_service_id
        WHERE user_ais.user_id = ?
    """
    user_ais = conn.execute(user_ais_query, (user_id,)).fetchall()

    total_tokens = conn.execute('SELECT SUM(tokens_purchased) FROM user_ais WHERE user_id = ?', (user_id,)).fetchone()[0] or 0
    conn.close()

    return render_template('dashboard.html', user=user, user_ais=user_ais, total_tokens=total_tokens)

@ReflexaBeacon.route('/buy_ai/<int:ai_id>', methods=['POST'])
@jwt_required()
def buy_ai(ai_id):
    user_id = get_jwt_identity()
    conn = get_db_connection()
    
    try:
        ai_service = conn.execute('SELECT price_in_tokens FROM ai_services WHERE id = ?', (ai_id,)).fetchone()
        if not ai_service:
            return jsonify({'success': False, 'message': 'AI not found.'})
        
        price = ai_service['price_in_tokens']

        user_ai_entry = conn.execute('SELECT * FROM user_ais WHERE user_id = ? AND ai_service_id = ?', (user_id, ai_id)).fetchone()
        
        if user_ai_entry:
            conn.execute('UPDATE user_ais SET tokens_purchased = tokens_purchased + ? WHERE user_id = ? AND ai_service_id = ?', (price, user_id, ai_id))
        else:
            conn.execute('INSERT INTO user_ais (user_id, ai_service_id, tokens_purchased) VALUES (?, ?, ?)', (user_id, ai_id, price))
            
        conn.commit()

        total_tokens = conn.execute('SELECT SUM(tokens_purchased) FROM user_ais WHERE user_id = ?', (user_id,)).fetchone()[0] or 0
        
        return jsonify({'success': True, 'message': f'You have successfully added {price} tokens for this AI.', 'total_tokens': total_tokens})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        conn.close()

@ReflexaBeacon.after_request
def add_cache_control_headers(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

