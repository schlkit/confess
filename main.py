from flask import Flask, render_template, send_from_directory, request, redirect, url_for, session, flash
import sqlite3
import os
from datetime import datetime
from functools import wraps

app = Flask(__name__, template_folder='.')
app.secret_key = os.environ.get('SECRET_KEY')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')

# Update database path to use Render's persistent storage
DB_PATH = '/opt/render/project/data/confessions.db'

# Database initialization
def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        # Staging table for unapproved confessions
        c.execute('''CREATE TABLE IF NOT EXISTS staging_confessions
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     text TEXT NOT NULL,
                     timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        
        # Live table for approved confessions
        c.execute('''CREATE TABLE IF NOT EXISTS live_confessions
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     text TEXT NOT NULL,
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
        c.execute('''
            SELECT text, timestamp 
            FROM live_confessions 
            ORDER BY timestamp DESC 
            LIMIT 20
        ''')
        confessions = c.fetchall()
        
        formatted_confessions = []
        for conf in confessions:
            conf_time = datetime.strptime(conf[1], '%Y-%m-%d %H:%M:%S')
            time_diff = datetime.now() - conf_time
            hours = time_diff.total_seconds() / 3600
            
            if hours < 1:
                time_str = f"{int(time_diff.total_seconds() / 60)} minutes ago"
            elif hours < 24:
                time_str = f"{int(hours)} hours ago"
            else:
                days = int(hours / 24)
                time_str = f"{days} days ago"
            
            formatted_confessions.append({
                'text': conf[0],
                'time': time_str
            })
            
    return render_template('site/index.html', confessions=formatted_confessions)

@app.route('/confess')
def confess():
    return render_template('site/confess.html')

@app.route('/submit_confession', methods=['POST'])
def submit_confession():
    if request.method == 'POST':
        confession_text = request.form.get('confessionText')
        if confession_text:
            try:
                with sqlite3.connect(DB_PATH) as conn:
                    c = conn.cursor()
                    c.execute('INSERT INTO staging_confessions (text) VALUES (?)', (confession_text,))
                    conn.commit()
                return '', 200  # Success response for AJAX
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
        # Get the confession text
        c.execute('SELECT text FROM staging_confessions WHERE id = ?', (confession_id,))
        confession = c.fetchone()
        if confession:
            # Move to live database
            c.execute('INSERT INTO live_confessions (text) VALUES (?)', (confession[0],))
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