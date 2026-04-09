import sqlite3
import json
from config import DATABASE_PATH

def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            balance INTEGER DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS codes (
            code TEXT PRIMARY KEY,
            value INTEGER,
            active INTEGER DEFAULT 0,
            used_by TEXT DEFAULT '[]'
        )
    ''')
    
    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect(DATABASE_PATH)

def get_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def create_user(user_id, balance=1000):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (user_id, balance) VALUES (?, ?)', (user_id, balance))
    conn.commit()
    conn.close()

def get_or_create_user(user_id):
    user = get_user(user_id)
    if user is None:
        create_user(user_id, 1000)  # Give 1000 coins initially
        return 1000
    return user[0]

def update_balance(user_id, amount):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
    if cursor.fetchone() is None:
        cursor.execute('INSERT INTO users (user_id, balance) VALUES (?, ?)', (user_id, amount))
    else:
        cursor.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (amount, user_id))
    conn.commit()
    conn.close()

def set_balance(user_id, amount):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET balance = ? WHERE user_id = ?', (amount, user_id))
    conn.commit()
    conn.close()

def get_code(code):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT code, value, active, used_by FROM codes WHERE code = ?', (code,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {
            'code': result[0],
            'value': result[1],
            'active': bool(result[2]),
            'used_by': json.loads(result[3])
        }
    return None

def create_code(code, value):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO codes (code, value, active, used_by) VALUES (?, ?, 0, ?)',
                   (code, value, json.dumps([])))
    conn.commit()
    conn.close()

def update_code(code, value=None, active=None):
    conn = get_connection()
    cursor = conn.cursor()
    if value is not None:
        cursor.execute('UPDATE codes SET value = ? WHERE code = ?', (value, code))
    if active is not None:
        cursor.execute('UPDATE codes SET active = ? WHERE code = ?', (1 if active else 0, code))
    conn.commit()
    conn.close()

def use_code(code, user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT used_by FROM codes WHERE code = ?', (code,))
    result = cursor.fetchone()
    used_by = json.loads(result[0])
    used_by.append(user_id)
    cursor.execute('UPDATE codes SET used_by = ? WHERE code = ?', (json.dumps(used_by), code))
    conn.commit()
    conn.close()