from flask import Flask, render_template, request, jsonify, redirect, url_for
import qrcode
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Database setup
DATABASE = 'data/products.db'

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                status TEXT NOT NULL,  -- 'real' or 'fake'
                qr_data TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        db.commit()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_qr():
    name = request.form['name']
    category = request.form['category']
    qr_data = f"{name}|{category}|{datetime.now().timestamp()}"

    db = get_db()
    
    # Check if product exists as fake
    existing = db.execute(
        'SELECT status FROM products WHERE name = ? AND category = ?',
        (name, category)
    ).fetchone()

    if existing and existing['status'] == 'fake':
        return render_template('index.html', 
                           error="This product is marked as fake! Cannot generate QR code.")

    # Generate QR code
    qr = qrcode.make(qr_data)
    qr_path = f"static/qrcodes/{name.replace(' ', '_')}_{category}.png"
    os.makedirs(os.path.dirname(qr_path), exist_ok=True)
    qr.save(qr_path)

    # Store in database as real product
    try:
        db.execute(
            'INSERT INTO products (name, category, status, qr_data) VALUES (?, ?, ?, ?)',
            (name, category, 'real', qr_data)
        )
        db.commit()
    except sqlite3.IntegrityError:
        return render_template('index.html', 
                           error="This product already exists!")

    return render_template('index.html', 
                       qr_image=qr_path, 
                       name=name,
                       success="QR generated successfully!")

@app.route('/scan')
def scan():
    return render_template('scan.html')

@app.route('/verify', methods=['POST'])
def verify():
    data = request.json
    qr_data = data.get('qr_data')
    
    db = get_db()
    product = db.execute(
        'SELECT * FROM products WHERE qr_data = ?', 
        (qr_data,)
    ).fetchone()

    if product:
        return jsonify({
            'status': product['status'],
            'name': product['name'],
            'category': product['category'],
            'created_at': product['created_at']
        })
    
    # If product not found, mark as fake
    try:
        parts = qr_data.split('|')
        name = parts[0] if len(parts) > 0 else 'Unknown'
        category = parts[1] if len(parts) > 1 else 'Unknown'
        
        db.execute(
            'INSERT INTO products (name, category, status, qr_data) VALUES (?, ?, ?, ?)',
            (name, category, 'fake', qr_data)
        )
        db.commit()
        
        return jsonify({
            'status': 'fake',
            'name': name,
            'category': category,
            'created_at': datetime.now().isoformat(),
            'message': 'Product not found - marked as fake'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/products/<status>')
def products(status):
    if status not in ['real', 'fake']:
        return redirect(url_for('home'))
    
    db = get_db()
    products = db.execute(
        'SELECT * FROM products WHERE status = ? ORDER BY created_at DESC',
        (status,)
    ).fetchall()
    
    return render_template('products.html', 
                         products=products, 
                         status=status.capitalize())

if __name__ == '__main__':
    # Ensure directories exist
    os.makedirs('data', exist_ok=True)
    os.makedirs('static/qrcodes', exist_ok=True)
    
    init_db()
    app.run(debug=True)