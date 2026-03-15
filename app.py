from flask import Flask, render_template, request, redirect, session, url_for
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import PyPDF2

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def init_db():
    with sqlite3.connect('users.db') as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL
        )""")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        with sqlite3.connect('users.db') as conn:
            conn.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, password))
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        with sqlite3.connect('users.db') as conn:
            cursor = conn.execute("SELECT * FROM users WHERE email=?", (email,))
            user = cursor.fetchone()
            if user and check_password_hash(user[3], password):
                session['user_id'] = user[0]
                session['username'] = user[1]
                return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/upload', methods=['POST'])
def upload():
    if 'pdf' not in request.files:
        return 'No file part'
    file = request.files['pdf']
    if file.filename == '':
        return 'No selected file'
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ''.join([page.extract_text() or '' for page in reader.pages])
        return render_template('result.html', text=text)
    return 'Upload failed'

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
