from flask import Flask, request, render_template, session, redirect, url_for, flash
from gmssl.sm4 import CryptSM4, SM4_ENCRYPT, SM4_DECRYPT
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from PIL import Image
import numpy as np
import base64
import io
import sqlite3
import secrets
import time
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime
import os
import json
import telepot
bot=telepot.Bot('8233017599:AAFai95Z_5Fm3qeUJbiMji8lQsX03vcKxR4')
# ---------------------- SM4 HELPER FUNCTIONS ----------------------

def pad(data, block_size=16):
    padding = block_size - len(data) % block_size
    return data + bytes([padding] * padding)

def unpad(data):
    padding = data[-1]
    return data[:-padding]

def sm4_encrypt(data, key):
    crypt_sm4 = CryptSM4()
    crypt_sm4.set_key(key, SM4_ENCRYPT)
    return crypt_sm4.crypt_ecb(pad(data))

def sm4_decrypt(data, key):
    crypt_sm4 = CryptSM4()
    crypt_sm4.set_key(key, SM4_DECRYPT)
    return unpad(crypt_sm4.crypt_ecb(data))

# ---------------------- AES-GCM HELPER FUNCTIONS ----------------------

def aes_gcm_encrypt(data, key):
    aesgcm = AESGCM(key)
    nonce = secrets.token_bytes(12)  # 96-bit nonce
    encrypted_data = aesgcm.encrypt(nonce, data, None)
    return nonce + encrypted_data

def aes_gcm_decrypt(encrypted_data, key):
    aesgcm = AESGCM(key)
    nonce = encrypted_data[:12]
    ciphertext = encrypted_data[12:]
    return aesgcm.decrypt(nonce, ciphertext, None)

# ---------------------- IMAGE ANALYSIS FUNCTIONS ----------------------

def calculate_psnr(original_path, stego_path):
    """Calculate PSNR between original and stego image"""
    try:
        original = np.array(Image.open(original_path).convert('RGB'))
        stego = np.array(Image.open(stego_path).convert('RGB'))
        
        mse = np.mean((original - stego) ** 2)
        if mse == 0:
            return float('inf')
        max_pixel = 255.0
        psnr = 20 * math.log10(max_pixel / math.sqrt(mse))
        return psnr
    except Exception as e:
        print(f"PSNR calculation error: {e}")
        return 0

def calculate_mse(original_path, stego_path):
    """Calculate Mean Squared Error"""
    try:
        original = np.array(Image.open(original_path).convert('RGB'))
        stego = np.array(Image.open(stego_path).convert('RGB'))
        return np.mean((original - stego) ** 2)
    except:
        return 0

def analyze_image_pixels(image_path):
    """Analyze pixel distribution and return histogram data"""
    try:
        img = Image.open(image_path).convert('RGB')
        img_array = np.array(img)
        
        # Calculate pixel statistics
        red_pixels = img_array[:,:,0].flatten()
        green_pixels = img_array[:,:,1].flatten()
        blue_pixels = img_array[:,:,2].flatten()
        
        stats = {
            'red': {
                'mean': float(np.mean(red_pixels)),
                'std': float(np.std(red_pixels)),
                'min': int(np.min(red_pixels)),
                'max': int(np.max(red_pixels))
            },
            'green': {
                'mean': float(np.mean(green_pixels)),
                'std': float(np.std(green_pixels)),
                'min': int(np.min(green_pixels)),
                'max': int(np.max(green_pixels))
            },
            'blue': {
                'mean': float(np.mean(blue_pixels)),
                'std': float(np.std(blue_pixels)),
                'min': int(np.min(blue_pixels)),
                'max': int(np.max(blue_pixels))
            }
        }
        
        return stats
    except Exception as e:
        print(f"Pixel analysis error: {e}")
        return None

# ---------------------- GRAPH GENERATION ----------------------

def generate_performance_graph(times, labels, graph_type):
    """Generate performance time graphs"""
    plt.figure(figsize=(10, 6))
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
    
    bars = plt.bar(labels, times, color=colors[:len(times)])
    plt.ylabel('Time (seconds)', fontsize=12)
    plt.title(f'{graph_type} Performance', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.4f}s',
                ha='center', va='bottom')
    
    plt.tight_layout()
    graph_path = f'static/graphs/{graph_type.lower()}_{secrets.token_hex(8)}.png'
    os.makedirs('static/graphs', exist_ok=True)
    plt.savefig(graph_path)
    plt.close()
    return graph_path

def generate_psnr_graph(psnr_values, labels):
    """Generate PSNR comparison graph"""
    plt.figure(figsize=(10, 6))
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    
    bars = plt.bar(labels, psnr_values, color=colors[:len(psnr_values)])
    plt.ylabel('PSNR (dB)', fontsize=12)
    plt.title('Image Quality (PSNR) Comparison', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f} dB',
                ha='center', va='bottom')
    
    plt.tight_layout()
    graph_path = f'static/graphs/psnr_{secrets.token_hex(8)}.png'
    plt.savefig(graph_path)
    plt.close()
    return graph_path

def generate_pixel_histogram(original_path, stego_path, operation_type):
    """Generate pixel distribution histograms for original and stego images"""
    try:
        # Load images
        original_img = Image.open(original_path).convert('RGB')
        stego_img = Image.open(stego_path).convert('RGB')
        
        # Convert to numpy arrays
        original_array = np.array(original_img)
        stego_array = np.array(stego_img)
        
        # Flatten pixel values for each channel
        original_flat = original_array.reshape(-1, 3)
        stego_flat = stego_array.reshape(-1, 3)
        
        # Create subplots
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        fig.suptitle(f'Pixel Distribution Analysis - {operation_type}', fontsize=16, fontweight='bold')
        
        colors = ['red', 'green', 'blue']
        channels = ['Red Channel', 'Green Channel', 'Blue Channel']
        
        for i in range(3):
            # Original image histogram
            axes[0, i].hist(original_flat[:, i], bins=50, color=colors[i], alpha=0.7, label='Original')
            axes[0, i].set_title(f'Original - {channels[i]}')
            axes[0, i].set_xlabel('Pixel Value')
            axes[0, i].set_ylabel('Frequency')
            axes[0, i].grid(True, alpha=0.3)
            
            # Stego image histogram
            axes[1, i].hist(stego_flat[:, i], bins=50, color=colors[i], alpha=0.7, label='Stego')
            axes[1, i].set_title(f'Stego - {channels[i]}')
            axes[1, i].set_xlabel('Pixel Value')
            axes[1, i].set_ylabel('Frequency')
            axes[1, i].grid(True, alpha=0.3)
        
        plt.tight_layout()
        histogram_path = f'static/graphs/histogram_{operation_type}_{secrets.token_hex(8)}.png'
        plt.savefig(histogram_path)
        plt.close()
        
        return histogram_path
    except Exception as e:
        print(f"Histogram generation error: {e}")
        return None

def generate_comparison_metrics(original_path, stego_path):
    """Generate comprehensive comparison metrics and graphs"""
    metrics = {}
    
    # Calculate PSNR and MSE
    metrics['psnr'] = calculate_psnr(original_path, stego_path)
    metrics['mse'] = calculate_mse(original_path, stego_path)
    
    # Analyze pixel statistics
    original_stats = analyze_image_pixels(original_path)
    stego_stats = analyze_image_pixels(stego_path)
    
    if original_stats and stego_stats:
        metrics['pixel_stats'] = {
            'original': original_stats,
            'stego': stego_stats
        }
    
    # Generate histogram
    metrics['histogram_path'] = generate_pixel_histogram(original_path, stego_path, "Encryption")
    
    return metrics

# ---------------------- TEXT STEGANOGRAPHY ----------------------

def embed_data_in_image(image_path, data):
    start_time = time.time()
    img = Image.open(image_path).convert('RGB')
    img_data = np.array(img)
    flat_img = img_data.flatten()

    data_length = len(data)
    metadata = data_length.to_bytes(4, 'big')
    combined_data = metadata + data

    if len(combined_data) * 8 > len(flat_img):
        raise ValueError("Data too large for this image.")

    for i, byte in enumerate(combined_data):
        for bit in range(8):
            flat_img[i*8 + bit] = (flat_img[i*8 + bit] & 0xFE) | ((byte >> (7 - bit)) & 1)

    new_img = Image.fromarray(flat_img.reshape(img_data.shape), 'RGB')
    output_path = 'static/output.png'
    new_img.save(output_path)
    
    encryption_time = time.time() - start_time
    psnr_value = calculate_psnr(image_path, output_path)
    
    # Generate comparison metrics
    metrics = generate_comparison_metrics(image_path, output_path)
    
    return output_path, encryption_time, psnr_value, metrics

def extract_data_from_image(image_path):
    start_time = time.time()
    img = Image.open(image_path)
    img_data = np.array(img).flatten()

    metadata_bits = [img_data[i] & 0x01 for i in range(32)]
    metadata_bytes = bytearray()
    for i in range(0, 32, 8):
        byte = 0
        for bit in metadata_bits[i:i+8]:
            byte = (byte << 1) | bit
        metadata_bytes.append(byte)
    data_length = int.from_bytes(metadata_bytes, 'big')

    data_bits = [img_data[i+32] & 0x01 for i in range(data_length*8)]
    data_bytes = bytearray()
    for i in range(0, len(data_bits), 8):
        byte = 0
        for bit in data_bits[i:i+8]:
            byte = (byte << 1) | bit
        data_bytes.append(byte)

    decryption_time = time.time() - start_time
    return bytes(data_bytes), decryption_time

# ---------------------- IMAGE-IN-IMAGE STEGANOGRAPHY ----------------------

def embed_image_in_image(carrier_image_path, hidden_image_path, output_image_path, key, algorithm='SM4'):
    start_time = time.time()
    carrier_img = Image.open(carrier_image_path).convert('RGB')
    hidden_img = Image.open(hidden_image_path).convert('RGB')

    hidden_bytes_io = io.BytesIO()
    hidden_img.save(hidden_bytes_io, format='PNG')
    hidden_data = hidden_bytes_io.getvalue()

    if algorithm == 'AES-GCM':
        encrypted_data = aes_gcm_encrypt(hidden_data, key)
    else:
        encrypted_data = sm4_encrypt(hidden_data, key)

    carrier_flat = np.array(carrier_img).flatten()

    data_length = len(encrypted_data)
    metadata = data_length.to_bytes(4, 'big')
    combined_data = metadata + encrypted_data

    if len(combined_data) * 8 > len(carrier_flat):
        raise ValueError("Hidden image too large.")

    for i, byte in enumerate(combined_data):
        for bit in range(8):
            carrier_flat[i*8 + bit] = (carrier_flat[i*8 + bit] & 0xFE) | ((byte >> (7 - bit)) & 1)

    new_img = Image.fromarray(carrier_flat.reshape(np.array(carrier_img).shape), 'RGB')
    new_img.save(output_image_path)
    
    encryption_time = time.time() - start_time
    psnr_value = calculate_psnr(carrier_image_path, output_image_path)
    
    # Generate comparison metrics
    metrics = generate_comparison_metrics(carrier_image_path, output_image_path)
    
    return encryption_time, psnr_value, metrics

def extract_image_from_image(encrypted_image_path, key, algorithm='SM4'):
    start_time = time.time()
    img = Image.open(encrypted_image_path)
    flat_img = np.array(img).flatten()

    metadata_bits = [flat_img[i] & 0x01 for i in range(32)]
    metadata_bytes = bytearray()
    for i in range(0, 32, 8):
        byte = 0
        for bit in metadata_bits[i:i+8]:
            byte = (byte << 1) | bit
        metadata_bytes.append(byte)
    data_length = int.from_bytes(metadata_bytes, 'big')

    encrypted_bits = [flat_img[i+32] & 0x01 for i in range(data_length*8)]
    encrypted_bytes = bytearray()
    for i in range(0, len(encrypted_bits), 8):
        byte = 0
        for bit in encrypted_bits[i:i+8]:
            byte = (byte << 1) | bit
        encrypted_bytes.append(byte)

    if algorithm == 'AES-GCM':
        decrypted_data = aes_gcm_decrypt(bytes(encrypted_bytes), key)
    else:
        decrypted_data = sm4_decrypt(bytes(encrypted_bytes), key)
    
    decryption_time = time.time() - start_time
    
    # Save extracted image
    hidden_img = Image.open(io.BytesIO(decrypted_data))
    extracted_path = "static/extracted_hidden_image.png"
    hidden_img.save(extracted_path)
    
    return extracted_path, decryption_time

# ---------------------- FLASK APP ----------------------

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# ---------------------- DATABASE ----------------------

def init_db():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    
    # Admin table
    cur.execute("""CREATE TABLE IF NOT EXISTS admin (
        Id INTEGER PRIMARY KEY AUTOINCREMENT, 
        name TEXT, 
        password TEXT, 
        mobile TEXT, 
        email TEXT
    )""")
    
    # User table
    cur.execute("""CREATE TABLE IF NOT EXISTS user (
        Id INTEGER PRIMARY KEY AUTOINCREMENT, 
        name TEXT, 
        password TEXT, 
        mobile TEXT, 
        email TEXT
    )""")
    
    # Failed attempts table
    cur.execute("""CREATE TABLE IF NOT EXISTS failed_attempts (
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_type TEXT,
        email TEXT,
        attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        ip_address TEXT
    )""")
    
    # Access history table
    cur.execute("""CREATE TABLE IF NOT EXISTS access_history (
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_type TEXT,
        user_email TEXT,
        user_name TEXT,
        operation_type TEXT,
        data_type TEXT,
        algorithm TEXT,
        success BOOLEAN,
        processing_time REAL,
        psnr_value REAL,
        access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        ip_address TEXT
    )""")
    
    conn.commit()
    conn.close()

init_db()

# ---------------------- LOGGING FUNCTIONS ----------------------

def log_failed_attempt(user_type, email, ip_address):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("INSERT INTO failed_attempts (user_type, email, ip_address) VALUES (?, ?, ?)",
                (user_type, email, ip_address))
    conn.commit()
    conn.close()

def log_access_history(user_type, user_email, user_name, operation_type, data_type, algorithm, success, processing_time, psnr_value, ip_address):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("""INSERT INTO access_history 
                (user_type, user_email, user_name, operation_type, data_type, algorithm, success, processing_time, psnr_value, ip_address) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (user_type, user_email, user_name, operation_type, data_type, algorithm, success, processing_time, psnr_value, ip_address))
    conn.commit()
    conn.close()

def get_failed_attempts():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM failed_attempts ORDER BY attempt_time DESC")
    attempts = cur.fetchall()
    conn.close()
    return attempts

def get_access_history(limit=50):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM access_history ORDER BY access_time DESC LIMIT ?", (limit,))
    history = cur.fetchall()
    conn.close()
    return history

def get_user_access_stats():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    
    # Get total operations by user
    cur.execute("""
        SELECT user_name, user_email, user_type, 
               COUNT(*) as total_operations,
               SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_operations,
               AVG(processing_time) as avg_processing_time,
               MAX(access_time) as last_access
        FROM access_history 
        GROUP BY user_email 
        ORDER BY last_access DESC
    """)
    stats = cur.fetchall()
    
    conn.close()
    return stats

# ---------------------- AUTHENTICATION ROUTES ----------------------

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        email = request.form['email']
        password = request.form['password']
        cur.execute("SELECT * FROM admin WHERE email=? AND password=?", (email, password))
        result = cur.fetchone()
        conn.close()
        
        if result:
            session['admin'] = email
            session['admin_name'] = result[1]
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            log_failed_attempt('admin', email, request.remote_addr)
            flash('Invalid credentials. Please try again.', 'error')
            return render_template('admin_login.html')
    return render_template('admin_login.html')

@app.route('/admin_register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        name = request.form['name']
        password = request.form['password']
        mobile = request.form['mobile']
        email = request.form['email']
        
        # Check if email already exists
        cur.execute("SELECT * FROM admin WHERE email=?", (email,))
        if cur.fetchone():
            flash('Email already registered!', 'error')
            return render_template('admin_register.html')
            
        cur.execute("INSERT INTO admin (name, password, mobile, email) VALUES (?, ?, ?, ?)", 
                   (name, password, mobile, email))
        conn.commit()
        conn.close()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('admin_login'))
    return render_template('admin_register.html')

@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        email = request.form['email']
        password = request.form['password']
        cur.execute("SELECT * FROM user WHERE email=? AND password=?", (email, password))
        result = cur.fetchone()
        conn.close()
        
        if result:
            session['user'] = email
            session['user_name'] = result[1]
            flash('Login successful!', 'success')
            return redirect(url_for('user_dashboard'))
        else:
            log_failed_attempt('user', email, request.remote_addr)
            flash('Invalid credentials. Please try again.', 'error')
            return render_template('user_login.html')
    return render_template('user_login.html')

@app.route('/user_register', methods=['GET', 'POST'])
def user_register():
    if request.method == 'POST':
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        name = request.form['name']
        password = request.form['password']
        mobile = request.form['mobile']
        email = request.form['email']
        
        # Check if email already exists
        cur.execute("SELECT * FROM user WHERE email=?", (email,))
        if cur.fetchone():
            flash('Email already registered!', 'error')
            return render_template('user_register.html')
            
        cur.execute("INSERT INTO user (name, password, mobile, email) VALUES (?, ?, ?, ?)", 
                   (name, password, mobile, email))
        conn.commit()
        conn.close()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('user_login'))
    return render_template('user_register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

# ---------------------- MAIN ROUTES ----------------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/text_steganography")
def text_steganography():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    return render_template("text_steganography.html")

@app.route("/image_steganography")
def image_steganography():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    return render_template("image_steganography.html")

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    
    failed_attempts = get_failed_attempts()
    access_history = get_access_history(20)
    user_stats = get_user_access_stats()
    
    return render_template('admin_dashboard.html', 
                         failed_attempts=failed_attempts,
                         access_history=access_history,
                         user_stats=user_stats)

@app.route('/user_dashboard')
def user_dashboard():
    if 'user' not in session:
        return redirect(url_for('user_login'))
    
    # Get user-specific access history
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM access_history 
        WHERE user_email = ? 
        ORDER BY access_time DESC 
        LIMIT 20
    """, (session['user'],))
    user_history = cur.fetchall()
    conn.close()
    
    return render_template('user_dashboard.html', user_history=user_history)

@app.route('/access_history')
def access_history():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    
    access_history = get_access_history(100)
    return render_template('access_history.html', access_history=access_history)

@app.route('/user_access_stats')
def user_access_stats():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    
    user_stats = get_user_access_stats()
    return render_template('user_access_stats.html', user_stats=user_stats)

# ---------------------- ENCRYPT/DECRYPT TEXT ----------------------

@app.route("/encrypt_text", methods=["POST"])
def encrypt_text():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
        
    try:
        patient_data = request.form["patient_data"].encode()
        image_file = request.files["image"]
        algorithm = request.form.get("algorithm", "SM4")
        
        # Save uploaded image
        image_path = f'static/uploads/{secrets.token_hex(8)}.png'
        os.makedirs('static/uploads', exist_ok=True)
        image_file.save(image_path)
        
        # Generate key
        if algorithm == "AES-GCM":
            key = secrets.token_bytes(32)  # 256-bit key for AES
        else:
            key = secrets.token_bytes(16)  # 128-bit key for SM4
        
        # Encrypt data
        start_encrypt = time.time()
        if algorithm == "AES-GCM":
            encrypted_data = aes_gcm_encrypt(patient_data, key)
        else:
            encrypted_data = sm4_encrypt(patient_data, key)
        encryption_time = time.time() - start_encrypt
        
        # Embed in image
        output_path, embed_time, psnr_value, metrics = embed_data_in_image(image_path, encrypted_data)
        
        # Save key
        key_b64 = base64.b64encode(key).decode()
        with open("encryption_key.txt", "w") as key_file:
            key_file.write(key_b64)
            print(key_b64)
            bot.sendMessage('6198625751',str('Encryption key for text : {}'.format(key_b64)))
        
        # Log access history
        log_access_history(
            user_type='admin',
            user_email=session['admin'],
            user_name=session['admin_name'],
            operation_type='encrypt',
            data_type='text',
            algorithm=algorithm,
            success=True,
            processing_time=encryption_time + embed_time,
            psnr_value=psnr_value,
            ip_address=request.remote_addr
        )
        
        # Generate performance graphs
        times = [encryption_time, embed_time]
        labels = ['Encryption', 'Embedding']
        time_graph = generate_performance_graph(times, labels, 'Encryption')
        psnr_graph = generate_psnr_graph([psnr_value], ['Stego Image'])
        
        total_time = encryption_time + embed_time
        
        return render_template("text_steganography.html", 
                             download_url='/static/output.png',
                             key=key_b64,
                             encryption_time=f"{encryption_time:.4f}",
                             embedding_time=f"{embed_time:.4f}",
                             total_time=f"{total_time:.4f}",
                             psnr_value=f"{psnr_value:.2f}",
                             time_graph=time_graph,
                             psnr_graph=psnr_graph,
                             histogram_path=metrics.get('histogram_path'),
                             pixel_stats=metrics.get('pixel_stats'),
                             algorithm=algorithm)
                             
    except Exception as e:
        flash(f'Error during encryption: {str(e)}', 'error')
        return redirect(url_for('text_steganography'))

@app.route("/decrypt_text", methods=["POST"])
def decrypt_text():
    if 'admin' not in session and 'user' not in session:
        return redirect(url_for('index'))
        
    try:
        image_file = request.files["image"]
        key_input = request.form['key']
        
        # Save uploaded image
        image_path = f'static/uploads/{secrets.token_hex(8)}.png'
        os.makedirs('static/uploads', exist_ok=True)
        image_file.save(image_path)
        
        # Verify key
        with open("encryption_key.txt", "r") as key_file:
            stored_key = key_file.read().strip()
        
        if stored_key != key_input:
            user_type = 'admin' if 'admin' in session else 'user'
            log_failed_attempt(user_type, session.get('admin') or session.get('user'), request.remote_addr)
            
            # Log failed attempt
            log_access_history(
                user_type=user_type,
                user_email=session.get('admin') or session.get('user'),
                user_name=session.get('admin_name') or session.get('user_name'),
                operation_type='decrypt',
                data_type='text',
                algorithm='unknown',
                success=False,
                processing_time=0,
                psnr_value=0,
                ip_address=request.remote_addr
            )
            
            flash('Invalid encryption key!', 'error')
            return redirect(url_for('text_steganography' if 'admin' in session else 'user_dashboard'))
        
        try:
            key = base64.b64decode(key_input)
            extracted_data, extract_time = extract_data_from_image(image_path)
            
            # Try both algorithms for decryption
            start_decrypt = time.time()
            try:
                decrypted_data = aes_gcm_decrypt(extracted_data, key)
                algorithm = 'AES-GCM'
            except:
                decrypted_data = sm4_decrypt(extracted_data, key)
                algorithm = 'SM4'
            decryption_time = time.time() - start_decrypt
            
            total_time = extract_time + decryption_time
            patient_info = decrypted_data.decode()
            
            # Log successful access
            user_type = 'admin' if 'admin' in session else 'user'
            log_access_history(
                user_type=user_type,
                user_email=session.get('admin') or session.get('user'),
                user_name=session.get('admin_name') or session.get('user_name'),
                operation_type='decrypt',
                data_type='text',
                algorithm=algorithm,
                success=True,
                processing_time=total_time,
                psnr_value=0,  # PSNR not applicable for decryption
                ip_address=request.remote_addr
            )
            
            # Generate performance graph
            times = [extract_time, decryption_time]
            labels = ['Extraction', 'Decryption']
            time_graph = generate_performance_graph(times, labels, 'Decryption')
            
            if 'admin' in session:
                return render_template("text_steganography.html", 
                                     decrypted_text=patient_info,
                                     extraction_time=f"{extract_time:.4f}",
                                     decryption_time=f"{decryption_time:.4f}",
                                     total_time=f"{total_time:.4f}",
                                     time_graph=time_graph,
                                     algorithm=algorithm)
            else:
                return render_template("user_dashboard.html", 
                                     decrypted_text=patient_info,
                                     extraction_time=f"{extract_time:.4f}",
                                     decryption_time=f"{decryption_time:.4f}",
                                     total_time=f"{total_time:.4f}",
                                     time_graph=time_graph,
                                     algorithm=algorithm)
                                     
        except Exception as e:
            user_type = 'admin' if 'admin' in session else 'user'
            log_access_history(
                user_type=user_type,
                user_email=session.get('admin') or session.get('user'),
                user_name=session.get('admin_name') or session.get('user_name'),
                operation_type='decrypt',
                data_type='text',
                algorithm='unknown',
                success=False,
                processing_time=0,
                psnr_value=0,
                ip_address=request.remote_addr
            )
            flash('Failed to decrypt data. Invalid key or corrupted data.', 'error')
            
    except Exception as e:
        flash(f'Error during decryption: {str(e)}', 'error')
    
    return redirect(url_for('text_steganography' if 'admin' in session else 'user_dashboard'))

# ---------------------- IMAGE ENCRYPTION/DECRYPTION ----------------------

@app.route("/encrypt_image", methods=["POST"])
def encrypt_image():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
        
    try:
        carrier_image = request.files["carrier_image"]
        hidden_image = request.files["hidden_image"]
        algorithm = request.form.get("algorithm", "SM4")
        
        # Save uploaded images
        carrier_path = f'static/uploads/{secrets.token_hex(8)}.png'
        hidden_path = f'static/uploads/{secrets.token_hex(8)}.png'
        output_path = "static/output_carrier.png"
        
        carrier_image.save(carrier_path)
        hidden_image.save(hidden_path)
        
        # Generate key
        if algorithm == "AES-GCM":
            key = secrets.token_bytes(32)
        else:
            key = secrets.token_bytes(16)
            
        key_b64 = base64.b64encode(key).decode()
        with open("encryption_key_image.txt", "w") as key_file:
            key_file.write(key_b64)
            print(key_b64)
            bot.sendMessage('6198625751',str('Encryption key for image : {}'.format(key_b64)))
        
        # Encrypt and embed
        encryption_time, psnr_value, metrics = embed_image_in_image(
            carrier_path, hidden_path, output_path, key, algorithm
        )
        
        # Log access history
        log_access_history(
            user_type='admin',
            user_email=session['admin'],
            user_name=session['admin_name'],
            operation_type='encrypt',
            data_type='image',
            algorithm=algorithm,
            success=True,
            processing_time=encryption_time,
            psnr_value=psnr_value,
            ip_address=request.remote_addr
        )
        
        # Generate graphs
        time_graph = generate_performance_graph([encryption_time], ['Image Encryption'], 'Encryption')
        psnr_graph = generate_psnr_graph([psnr_value], ['Stego Image'])
        
        return render_template("image_steganography.html", 
                             download_url='/static/output_carrier.png',
                             key=key_b64,
                             encryption_time=f"{encryption_time:.4f}",
                             psnr_value=f"{psnr_value:.2f}",
                             time_graph=time_graph,
                             psnr_graph=psnr_graph,
                             histogram_path=metrics.get('histogram_path'),
                             pixel_stats=metrics.get('pixel_stats'),
                             algorithm=algorithm)
                             
    except Exception as e:
        flash(f'Error during image encryption: {str(e)}', 'error')
        return redirect(url_for('image_steganography'))

@app.route("/decrypt_image", methods=["POST"])
def decrypt_image():
    if 'admin' not in session and 'user' not in session:
        return redirect(url_for('index'))
        
    try:
        encrypted_image = request.files["image"]
        key_input = request.form['key']
        algorithm = request.form.get("algorithm", "SM4")
        
        # Save uploaded image
        image_path = f'static/uploads/{secrets.token_hex(8)}.png'
        encrypted_image.save(image_path)
        
        # Verify key
        with open("encryption_key_image.txt", "r") as key_file:
            stored_key = key_file.read().strip()
        
        if stored_key != key_input:
            user_type = 'admin' if 'admin' in session else 'user'
            log_failed_attempt(user_type, session.get('admin') or session.get('user'), request.remote_addr)
            
            # Log failed attempt
            log_access_history(
                user_type=user_type,
                user_email=session.get('admin') or session.get('user'),
                user_name=session.get('admin_name') or session.get('user_name'),
                operation_type='decrypt',
                data_type='image',
                algorithm=algorithm,
                success=False,
                processing_time=0,
                psnr_value=0,
                ip_address=request.remote_addr
            )
            
            flash('Invalid encryption key!', 'error')
            return redirect(url_for('image_steganography' if 'admin' in session else 'user_dashboard'))
        
        try:
            key = base64.b64decode(key_input)
            extracted_path, decryption_time = extract_image_from_image(image_path, key, algorithm)
            
            # Log successful access
            user_type = 'admin' if 'admin' in session else 'user'
            log_access_history(
                user_type=user_type,
                user_email=session.get('admin') or session.get('user'),
                user_name=session.get('admin_name') or session.get('user_name'),
                operation_type='decrypt',
                data_type='image',
                algorithm=algorithm,
                success=True,
                processing_time=decryption_time,
                psnr_value=0,  # PSNR not applicable for decryption
                ip_address=request.remote_addr
            )
            
            # Generate performance graph
            time_graph = generate_performance_graph([decryption_time], ['Image Decryption'], 'Decryption')
            
            if 'admin' in session:
                return render_template("image_steganography.html", 
                                     decrypted_image='/static/extracted_hidden_image.png',
                                     decryption_time=f"{decryption_time:.4f}",
                                     time_graph=time_graph,
                                     algorithm=algorithm)
            else:
                return render_template("user_dashboard.html", 
                                     decrypted_image='/static/extracted_hidden_image.png',
                                     decryption_time=f"{decryption_time:.4f}",
                                     time_graph=time_graph,
                                     algorithm=algorithm)
                                     
        except Exception as e:
            user_type = 'admin' if 'admin' in session else 'user'
            log_access_history(
                user_type=user_type,
                user_email=session.get('admin') or session.get('user'),
                user_name=session.get('admin_name') or session.get('user_name'),
                operation_type='decrypt',
                data_type='image',
                algorithm=algorithm,
                success=False,
                processing_time=0,
                psnr_value=0,
                ip_address=request.remote_addr
            )
            flash('Failed to decrypt image. Invalid key or corrupted data.', 'error')
            
    except Exception as e:
        flash(f'Error during image decryption: {str(e)}', 'error')
    
    return redirect(url_for('image_steganography' if 'admin' in session else 'user_dashboard'))

if __name__ == "__main__":
    os.makedirs('static/uploads', exist_ok=True)
    os.makedirs('static/graphs', exist_ok=True)
    app.run(debug=True, use_reloader=False)