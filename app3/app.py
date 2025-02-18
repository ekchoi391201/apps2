from flask import Flask, request, render_template, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import socket

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL 설정
app.config['MYSQL_HOST'] = 'db-svc'
app.config['MYSQL_USER'] = 'frodo'
app.config['MYSQL_PASSWORD'] = 'frodo5020!!'
app.config['MYSQL_DB'] = 'frodo'

mysql = MySQL(app)

# Flask-Login 설정
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    if user:
        return User(id=user[0], username=user[1], password=user[2])
    return None

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)  # 기본 방법 사용
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        mysql.connection.commit()
        cursor.close()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        if user and check_password_hash(user[2], password):
            login_user(User(id=user[0], username=user[1], password=user[2]))
            return redirect(url_for('dashboard'))
        flash('Invalid credentials. Please try again.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    client_ip = request.remote_addr
    server_name = socket.gethostname()
    server_ip = socket.gethostbyname(server_name)
    return render_template('dashboard.html', client_ip=client_ip, server_name=server_name, server_ip=server_ip)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

