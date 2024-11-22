from flask import Flask, render_template, send_from_directory, request, redirect, url_for, session, flash
import sqlite3
import os
from datetime import datetime
from functools import wraps
from pathlib import Path

app = Flask(__name__, template_folder='.')
app.secret_key = os.environ.get('SECRET_KEY')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')

# Use Render's persistent disk mount path
DATA_DIR = Path('/opt/render/project/data')
DB_PATH = str(DATA_DIR / 'confessions.db')

def init_db():
    # Create data directory if it doesn't exist
    os.makedirs(DATA_DIR, exist_ok=True)
    
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        
        # Create tables only if they don't exist (no dropping)
        c.execute('''CREATE TABLE IF NOT EXISTS staging_confessions
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     text TEXT NOT NULL,
                     color TEXT DEFAULT 'white',
                     timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS live_confessions
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     text TEXT NOT NULL,
                     color TEXT DEFAULT 'white',
                     timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()

# Initialize database on startup
init_db()

def require_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        try:
            c.execute('''
                SELECT text, color, timestamp 
                FROM live_confessions 
                ORDER BY timestamp DESC 
                LIMIT 20
            ''')
        except sqlite3.OperationalError:
            # If color column doesn't exist, reinitialize the database
            init_db()
            c.execute('''
                SELECT text, color, timestamp 
                FROM live_confessions 
                ORDER BY timestamp DESC 
                LIMIT 20
            ''')
        
        confessions = c.fetchall()
        
        formatted_confessions = []
        for conf in confessions:
            conf_time = datetime.strptime(conf[2], '%Y-%m-%d %H:%M:%S')
            formatted_confessions.append({
                'text': conf[0],
                'color': conf[1] if len(conf) > 1 else 'white',  # Default to white if no color
                'time': conf_time.strftime('%I:%M %p').lstrip('0')
            })
    
    return render_template('site/index.html', confessions=formatted_confessions)

@app.route('/confess')
def confess():
    return render_template('site/confess.html')

@app.route('/what')
def what():
    return render_template('site/what.html')

@app.route('/submit_confession', methods=['POST'])
def submit_confession():
    if request.method == 'POST':
        confession_text = request.form.get('confessionText')
        color = request.form.get('color', 'white')  # Get color from form
        if confession_text:
            try:
                with sqlite3.connect(DB_PATH) as conn:
                    c = conn.cursor()
                    c.execute('INSERT INTO staging_confessions (text, color) VALUES (?, ?)', 
                            (confession_text, color))
                    conn.commit()
                return '', 200
            except Exception as e:
                print(f"Database error: {str(e)}")
                return str(e), 500
    return '', 400

@app.route('/admin')
@require_admin
def admin():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('SELECT id, text, timestamp FROM staging_confessions ORDER BY timestamp DESC LIMIT 1')
        confession = c.fetchone()
    return render_template('site/admin.html', confession=confession)

@app.route('/admin/approve/<int:confession_id>', methods=['POST'])
@require_admin
def approve_confession(confession_id):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        # Get the confession text and color
        c.execute('SELECT text, color FROM staging_confessions WHERE id = ?', (confession_id,))
        confession = c.fetchone()
        if confession:
            # Move to live database with color
            c.execute('INSERT INTO live_confessions (text, color) VALUES (?, ?)', 
                     (confession[0], confession[1]))
            # Delete from staging
            c.execute('DELETE FROM staging_confessions WHERE id = ?', (confession_id,))
            conn.commit()
    return redirect(url_for('admin'))

@app.route('/admin/reject/<int:confession_id>', methods=['POST'])
@require_admin
def reject_confession(confession_id):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('DELETE FROM staging_confessions WHERE id = ?', (confession_id,))
        conn.commit()
    return redirect(url_for('admin'))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['is_admin'] = True
            return redirect(url_for('admin'))
        flash('Invalid password')
    return render_template('site/admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('admin_login'))

@app.route('/<path:filename>')
def serve_static(filename):
    print(f"Serving static file: {filename}")
    try:
        return send_from_directory('site', filename)
    except Exception as e:
        print(f"Error serving {filename}: {str(e)}")
        return f"Error: {str(e)}", 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)