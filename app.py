from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime
import pytz

app = Flask(__name__)
CORS(app)

# Set Indian timezone
ist = pytz.timezone('Asia/Kolkata')

# Database setup
def init_db():
    conn = sqlite3.connect('enquiries.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS enquiries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            reason TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

def get_ist_time():
    # Get current UTC time and convert to IST
    utc_now = datetime.now(pytz.UTC)
    ist_now = utc_now.astimezone(ist)
    return ist_now.strftime('%Y-%m-%d %H:%M:%S')

@app.route('/api/enquiry', methods=['POST'])
def submit_enquiry():
    try:
        data = request.json
        name = data.get('name')
        phone = data.get('phone')
        email = data.get('email')
        reason = data.get('reason')

        if not all([name, phone, email, reason]):
            return jsonify({'error': 'All fields are required'}), 400

        # Get current time in IST
        ist_time = get_ist_time()

        conn = sqlite3.connect('enquiries.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO enquiries (name, phone, email, reason, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, phone, email, reason, ist_time))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Enquiry submitted successfully'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/enquiries', methods=['GET'])
def get_enquiries():
    try:
        conn = sqlite3.connect('enquiries.db')
        c = conn.cursor()
        c.execute('SELECT * FROM enquiries ORDER BY created_at DESC')
        enquiries = c.fetchall()
        conn.close()

        return jsonify([{
            'id': row[0],
            'name': row[1],
            'phone': row[2],
            'email': row[3],
            'reason': row[4],
            'created_at': row[5]
        } for row in enquiries]), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 