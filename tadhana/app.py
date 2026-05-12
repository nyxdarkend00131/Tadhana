from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_bcrypt import Bcrypt
import psycopg2
import psycopg2.extras

app = Flask(__name__, static_folder='static')
CORS(app)
bcrypt = Bcrypt(app)

# ── Database connection ───────────────────────────────
def get_db():
    return psycopg2.connect(
        host='localhost',
        database='tadhana_db',
        user='postgres',
        password='6767',
        port=5432
    )

# ── Serve HTML pages ──────────────────────────────────
@app.route('/')
def index():
    return send_from_directory('static', 'login.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

# ── REGISTER ──────────────────────────────────────────
@app.route('/api/register', methods=['POST'])
def register():
    data     = request.get_json()
    name     = data.get('name', '').strip()
    email    = data.get('email', '').strip()
    password = data.get('password', '')
    dob      = data.get('date_of_birth') or None

    if not name or not email or not password:
        return jsonify({'error': 'Name, email, and password are required.'}), 400
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters.'}), 400

    hashed = bcrypt.generate_password_hash(password).decode('utf-8')

    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute(
            'INSERT INTO users (name, email, password, date_of_birth) VALUES (%s, %s, %s, %s)',
            (name, email, hashed, dob)
        )
        conn.commit()
        cur.close(); conn.close()
        return jsonify({'success': True, 'message': 'Account created successfully!'})
    except psycopg2.errors.UniqueViolation:
        return jsonify({'error': 'An account with that email already exists.'}), 400
    except Exception as e:
        print(e)
        return jsonify({'error': 'Something went wrong.'}), 500

# ── LOGIN ─────────────────────────────────────────────
@app.route('/api/login', methods=['POST'])
def login():
    data     = request.get_json()
    email    = data.get('email', '').strip()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'All fields are required.'}), 400

    try:
        conn = get_db()
        cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cur.fetchone()

        if not user:
            return jsonify({'error': 'No account found with that email.'}), 401
        if not bcrypt.check_password_hash(user['password'], password):
            return jsonify({'error': 'Incorrect password.'}), 401

        cur.execute('UPDATE users SET last_login = NOW() WHERE user_id = %s', (user['user_id'],))
        conn.commit()
        cur.close(); conn.close()

        return jsonify({
            'success': True,
            'user_id': user['user_id'],
            'name':    user['name'],
            'email':   user['email']
        })
    except Exception as e:
        print(e)
        return jsonify({'error': 'Something went wrong.'}), 500

# ── GET ALL READINGS ──────────────────────────────────
@app.route('/api/readings/<int:user_id>', methods=['GET'])
def get_readings(user_id):
    try:
        conn = get_db()
        cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute('SELECT * FROM readings WHERE user_id = %s ORDER BY reading_date DESC', (user_id,))
        readings = cur.fetchall()
        cur.close(); conn.close()
        result = []
        for r in readings:
            row = dict(r)
            if row.get('reading_date'):
                row['reading_date'] = row['reading_date'].isoformat()
            result.append(row)
        return jsonify(result)
    except Exception as e:
        print(e)
        return jsonify({'error': 'Failed to fetch readings.'}), 500

# ── GET SINGLE READING ────────────────────────────────
@app.route('/api/reading/<int:reading_id>', methods=['GET'])
def get_reading(reading_id):
    try:
        conn = get_db()
        cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute('SELECT * FROM readings WHERE reading_id = %s', (reading_id,))
        reading = cur.fetchone()
        cur.close(); conn.close()
        if not reading:
            return jsonify({'error': 'Reading not found.'}), 404
        row = dict(reading)
        if row.get('reading_date'):
            row['reading_date'] = row['reading_date'].isoformat()
        return jsonify(row)
    except Exception as e:
        print(e)
        return jsonify({'error': 'Failed to fetch reading.'}), 500

# ── CREATE READING ────────────────────────────────────
@app.route('/api/readings', methods=['POST'])
def create_reading():
    data        = request.get_json()
    user_id     = data.get('user_id')
    question    = data.get('question', '').strip()
    spread_type = data.get('spread_type', '')
    tags        = data.get('tags', '')
    notes       = data.get('notes', '')

    if not user_id or not question or not spread_type:
        return jsonify({'error': 'Missing required fields.'}), 400

    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute(
            'INSERT INTO readings (user_id, question, spread_type, tags, notes) VALUES (%s, %s, %s, %s, %s) RETURNING reading_id',
            (user_id, question, spread_type, tags, notes)
        )
        reading_id = cur.fetchone()[0]
        conn.commit()
        cur.close(); conn.close()
        return jsonify({'success': True, 'reading_id': reading_id})
    except Exception as e:
        print(e)
        return jsonify({'error': 'Failed to save reading.'}), 500

# ── UPDATE READING ────────────────────────────────────
@app.route('/api/readings/<int:reading_id>', methods=['PUT'])
def update_reading(reading_id):
    data        = request.get_json()
    question    = data.get('question', '').strip()
    spread_type = data.get('spread_type', '')
    tags        = data.get('tags', '')
    notes       = data.get('notes', '')

    if not question or not spread_type:
        return jsonify({'error': 'Question and spread type are required.'}), 400

    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute(
            'UPDATE readings SET question = %s, spread_type = %s, tags = %s, notes = %s WHERE reading_id = %s',
            (question, spread_type, tags, notes, reading_id)
        )
        conn.commit()
        cur.close(); conn.close()
        return jsonify({'success': True})
    except Exception as e:
        print(e)
        return jsonify({'error': 'Failed to update reading.'}), 500

# ── DELETE READING ────────────────────────────────────
@app.route('/api/readings/<int:reading_id>', methods=['DELETE'])
def delete_reading(reading_id):
    try:
        conn = get_db()
        cur  = conn.cursor()
        cur.execute('DELETE FROM readings WHERE reading_id = %s', (reading_id,))
        conn.commit()
        cur.close(); conn.close()
        return jsonify({'success': True})
    except Exception as e:
        print(e)
        return jsonify({'error': 'Failed to delete reading.'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=3000)
