import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('complaints.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            status TEXT DEFAULT 'open',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            sentiment TEXT DEFAULT 'unknown',
            category TEXT DEFAULT 'другое'
        )
    ''')
    conn.commit()
    conn.close()

def save_complaint(text, sentiment="unknown", category="другое"):
    conn = sqlite3.connect('complaints.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO complaints (text, sentiment, category)
        VALUES (?, ?, ?)
    ''', (text, sentiment, category))
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id

def get_complaint(complaint_id):
    conn = sqlite3.connect('complaints.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM complaints WHERE id = ?', (complaint_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            "id": result[0],
            "text": result[1],
            "status": result[2],
            "timestamp": result[3],
            "sentiment": result[4],
            "category": result[5]
        }
    return None
