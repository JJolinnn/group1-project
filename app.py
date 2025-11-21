from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'nfu2025_group1'

# 超活潑全站配色
COLORS = {
    'bg': 'linear-gradient(135deg, #A385E2, #F2A3F2, #7E8BE8, #DCE8F4)',
    'primary': '#A385E2',
    'btn': '#7E8BE8',
    'light': '#DCE8F4'
}

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, name TEXT, password TEXT, is_manager INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS leaves 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, name TEXT, 
                  type TEXT, start_date TEXT, end_date TEXT, reason TEXT, 
                  status TEXT DEFAULT '待審核', apply_time TEXT)''')
    members = [
        ('12156208', '蕭譓贏', '123', 0),
        ('12156231', '陳俊翰', '123', 0),
        ('12156234', '張心宇', '123', 0),
        ('12156252', '蔡瑀涵', '123', 0),
        ('12156254', '傅筠詒', '123', 0),
        ('admin', '第一組主管', 'admin', 1)
    ]
    c.executemany("INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?)", members)
    conn.commit()
    conn.close()

@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()
    if user:
        session['username'] = user[0]
        session['name'] = user[1]
        session['is_manager'] = bool(user[3])
        return redirect('/index')
    flash('帳號或密碼錯誤！')
    return redirect('/')

@app.route('/index')
def index():
    if 'username' not in session:
        return redirect('/')
    return render_template('index.html', name=session['name'], colors=COLORS)

@app.route('/apply')
def apply():
    if 'username' not in session:
        return redirect('/')
    return render_template('apply.html', colors=COLORS)

@app.route('/submit', methods=['POST'])
def submit():
    if 'username' not in session:
        return redirect('/')
    leave_type = request.form['type']
    status = '已核准' if leave_type == '生理假' else '待審核'
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("""INSERT INTO leaves 
                 (username, name, type, start_date, end_date, reason, status, apply_time)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
              (session['username'], session['name'],
               leave_type, request.form['start'], request.form['end'],
               request.form['reason'], status, datetime.now().strftime('%Y-%m-%d %H:%M')))
    conn.commit()
    conn.close()
    flash('申請成功！生理假已自動核准～' if leave_type == '生理假' else '申請已送出，等待主管審核')
    return redirect('/index')

@app.route('/history')
def history():
    if 'username' not in session:
        return redirect('/')
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM leaves WHERE username=? ORDER BY id DESC", (session['username'],))
    leaves = c.fetchall()
    conn.close()
    return render_template('history.html', leaves=leaves, colors=COLORS)

@app.route('/manager')
def manager():
    if not session.get('is_manager'):
        return redirect('/index')
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM leaves WHERE status='待審核' ORDER BY id DESC")
    leaves = c.fetchall()
    conn.close()
    return render_template('manager.html', leaves=leaves, colors=COLORS)

@app.route('/approve/<int:lid>')
def approve(lid):
    if session.get('is_manager'):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("UPDATE leaves SET status='已核准' WHERE id=?", (lid,))
        conn.commit()
        conn.close()
        flash('已核准')
    return redirect('/manager')

@app.route('/reject/<int:lid>')
def reject(lid):
    if session.get('is_manager'):
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("UPDATE leaves SET status='已駁回' WHERE id=?", (lid,))
        conn.commit()
        conn.close()
        flash('已駁回')
    return redirect('/manager')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    init_db()
if __name__ == '__main__':
    app.run()
