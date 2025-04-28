from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime
import pytz

app = Flask(__name__)
# Configure CORS to allow requests from the frontend
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type"]
    }
})

# Set Indian timezone
ist = pytz.timezone('Asia/Kolkata')

# Database setup
def init_db():
    conn = sqlite3.connect('enquiries.db')
    c = conn.cursor()
    
    # Create the table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS enquiries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            reason TEXT NOT NULL,
            created_at TEXT NOT NULL,
            solved BOOLEAN DEFAULT 0
        )
    ''')
    
    # Check if solved column exists
    c.execute("PRAGMA table_info(enquiries)")
    columns = [column[1] for column in c.fetchall()]
    
    # Add solved column if it doesn't exist
    if 'solved' not in columns:
        c.execute('ALTER TABLE enquiries ADD COLUMN solved BOOLEAN DEFAULT 0')
    
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
            'created_at': row[5],
            'solved': bool(row[6]) if len(row) > 6 else False
        } for row in enquiries]), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/enquiries/<int:enquiry_id>', methods=['PUT'])
def update_enquiry(enquiry_id):
    try:
        data = request.json
        solved = data.get('solved')
        
        if solved is None:
            return jsonify({'error': 'solved status is required'}), 400

        conn = sqlite3.connect('enquiries.db')
        c = conn.cursor()
        
        # First check if the enquiry exists
        c.execute('SELECT id FROM enquiries WHERE id = ?', (enquiry_id,))
        if not c.fetchone():
            return jsonify({'error': 'Enquiry not found'}), 404

        # Update the enquiry
        c.execute('UPDATE enquiries SET solved = ? WHERE id = ?', (solved, enquiry_id))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Enquiry updated successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/enquiries/<int:enquiry_id>', methods=['DELETE'])
def delete_enquiry(enquiry_id):
    try:
        conn = sqlite3.connect('enquiries.db')
        c = conn.cursor()
        c.execute('DELETE FROM enquiries WHERE id = ?', (enquiry_id,))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Enquiry deleted successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 