import os
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np
from PIL import Image
from flask_cors import CORS
import random
import string
from itsdangerous import URLSafeTimedSerializer
from email.mime.text import MIMEText
import smtplib
from flask import request, redirect, url_for, render_template, flash
from werkzeug.utils import secure_filename
import os


# --- Inisialisasi Flask & CORS
app = Flask(__name__)
CORS(app)

# --- Konfigurasi APP
app.config['SECRET_KEY'] = 'myverysecretkey12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3306/deteksi_penyakit_gigi'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Serializer untuk Token
s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# --- Konfigurasi Email
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_app_password'
app.config['MAIL_USE_TLS'] = True

# --- Tambahan CORS header
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
    return response

# --- Model Database
class Pengguna(db.Model):
    __tablename__ = 'pengguna'
    id_pengguna = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('admin', 'user'), default='user')

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

class HasilKlasifikasi(db.Model):
    __tablename__ = 'hasil_klasifikasi'
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100))
    filename = db.Column(db.String(255))
    prediksi = db.Column(db.String(50))
    confidence = db.Column(db.Float)
    waktu = db.Column(db.DateTime, server_default=db.func.now())
    
class Dataset(db.Model):
    __tablename__ = 'dataset'
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(100), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

# --- Dekorator Login
def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'username' not in session:
                flash('Anda perlu login untuk mengakses halaman ini.', 'warning')
                return redirect(url_for('login'))
            if role and session.get('role') != role:
                flash(f'Akses ditolak untuk role: {role}', 'danger')
                return redirect(url_for('dashboard_admin' if session.get('role') == 'admin' else 'dashboard_user'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# --- Load Model AI
MODEL_PATH = 'best_model.h5'
if not os.path.exists(MODEL_PATH):
    print(f"Error: File model '{MODEL_PATH}' tidak ditemukan.")
    exit(1)

try:
    model = tf.keras.models.load_model(MODEL_PATH)
    print("Model berhasil dimuat.")
except Exception as e:
    print(f"ERROR saat memuat model: {e}")
    exit(1)

CLASS_NAMES = ["Gigi Berkarang", "Gigi Berlubang", "Bukan Gigi"]
IMG_HEIGHT = 224
IMG_WIDTH = 224

# --- Kirim Email Reset
def send_reset_email(to_email, token):
    reset_url = url_for('reset_password', token=token, _external=True)
    subject = "Reset Password Akun Anda"
    body = f"Klik link berikut untuk reset password:\n\n{reset_url}\n\nJika Anda tidak meminta, abaikan saja."

    message = MIMEText(body)
    message['Subject'] = subject
    message['From'] = app.config['MAIL_USERNAME']
    message['To'] = to_email

    try:
        with smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT']) as server:
            server.starttls()
            server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            server.send_message(message)
        print(f"Email reset terkirim ke {to_email}")
    except Exception as e:
        print(f"[ERROR Kirim Email]: {e}")

# --- ROUTES
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('dashboard_admin' if session.get('role') == 'admin' else 'dashboard_user'))

    if request.method == 'POST':
        email = request.form['username']
        password = request.form['password']
        user = Pengguna.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['username'] = user.nama
            session['role'] = user.role
            flash('Login berhasil.', 'success')
            return redirect(url_for('dashboard_admin' if user.role == 'admin' else 'dashboard_user'))
        else:
            flash('Email atau password salah.', 'danger')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            nama = request.form['username']
            email = request.form['email']
            password = request.form['password']
            confirm_password = request.form['confirm_password']

            if not nama or not email or not password or not confirm_password:
                flash('Semua kolom wajib diisi.', 'danger')
                return render_template('register.html')

            if password != confirm_password:
                flash('Konfirmasi password tidak cocok.', 'danger')
                return render_template('register.html')

            existing = Pengguna.query.filter_by(email=email).first()
            if existing:
                flash('Email sudah terdaftar.', 'warning')
                return render_template('register.html')

            user = Pengguna(nama=nama, email=email, role='user')
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            flash('Registrasi berhasil. Silakan login.', 'success')
            return redirect(url_for('login'))

        except Exception as e:
            print(f"ERROR REGISTER: {e}")
            flash('Terjadi kesalahan saat registrasi.', 'danger')
            return render_template('register.html')

    return render_template('register.html')


@app.route('/profil')
@login_required()
def profil():
    user = Pengguna.query.filter_by(nama=session.get('username')).first()
    return render_template('profil.html', user=user)

@app.route('/profil/edit', methods=['GET', 'POST'])
@login_required()
def edit_profil():
    nama_lama = session.get('username')
    user = Pengguna.query.filter_by(nama=nama_lama).first()

    if not user:
        flash('User tidak ditemukan.', 'danger')
        return redirect(url_for('profil'))

    if request.method == 'POST':
        new_email = request.form['email']
        new_password = request.form['password']

        if not new_email:
            flash('Email tidak boleh kosong.', 'danger')
            return render_template('edit_profil.html', user=user)

        user.email = new_email

        if new_password:
            user.set_password(new_password)

        db.session.commit()
        flash('Profil berhasil diperbarui.', 'success')
        return redirect(url_for('profil'))

    return render_template('edit_profil.html', user=user)

@app.route('/logout')
@login_required()
def logout():
    session.clear()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('login'))

@app.route('/lupa_akun', methods=['GET', 'POST'])
def lupa_akun():
    if request.method == 'POST':
        email = request.form['email']
        user = Pengguna.query.filter_by(email=email).first()
        if user:
            # Buat password baru secara acak
            new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            user.set_password(new_password)
            db.session.commit()

            flash(f'Password baru Anda: {new_password}', 'success')
        else:
            flash('Email tidak ditemukan.', 'danger')

    return render_template('lupa_akun.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    return render_template('reset_password.html')

@app.route('/predict', methods=['POST'])
@login_required()
def predict():
    if 'file' not in request.files:
        return jsonify({"error": "Tidak ada file yang diupload."}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Tidak ada file yang dipilih."}), 400

    try:
        # --- Siapkan gambar
        img = Image.open(file.stream).convert('RGB')
        img = img.resize((IMG_HEIGHT, IMG_WIDTH))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0) / 255.0

        # --- Prediksi menggunakan model
        predictions = model.predict(img_array)
        scores = tf.nn.softmax(predictions[0])
        predicted_class_index = np.argmax(scores)
        predicted_class_name = CLASS_NAMES[predicted_class_index]
        confidence = float(np.max(scores))

        print(f"[DEBUG Predict] Class: {predicted_class_name}, Confidence: {confidence}")

        # --- Threshold minimum
        MIN_CONFIDENCE = 0.5

        # --- Tolak jika bukan gigi atau confidence rendah
        if predicted_class_name == "Bukan Gigi" or confidence < MIN_CONFIDENCE:
            return jsonify({
                "prediction": "Tidak Dikenali",
                "confidence": confidence,
                "message": "Gambar yang Anda upload bukan gambar gigi yang dapat dikenali. Silakan coba gambar lain."
            })

        # --- Simpan hasil prediksi valid (HANYA Gigi Berlubang / Berkarang)
        hasil = HasilKlasifikasi(
            nama=session.get('username'),
            filename=file.filename,
            prediksi=predicted_class_name,
            confidence=confidence
        )
        db.session.add(hasil)
        db.session.commit()

        # --- Kirim respon JSON ke frontend
        return jsonify({
            "prediction": predicted_class_name,
            "confidence": confidence,
            "all_scores": {label: float(scores[i]) for i, label in enumerate(CLASS_NAMES)}
        })

    except Exception as e:
        print(f"[ERROR Predict]: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/dashboard_user')
@login_required(role='user')
def dashboard_user():
    return render_template('dashboard_user.html')

@app.route('/dashboard_admin')
@login_required(role='admin')
def dashboard_admin():
    from sqlalchemy import func
    data = (
        db.session.query(HasilKlasifikasi.prediksi, func.count(HasilKlasifikasi.id))
        .group_by(HasilKlasifikasi.prediksi)
        .all()
    )
    labels = [row[0] for row in data] or ['Kalkulus', 'Karies']
    counts = [row[1] for row in data] or [0, 0]
    return render_template('dashboard_admin.html', chart_labels=labels, chart_data=counts)

@app.route('/deteksi')
@login_required(role='user')
def deteksi():
    return render_template('deteksi.html')

@app.route('/riwayat')
@login_required(role='user')
def riwayat():
    nama_user = session.get('username')
    data_riwayat = HasilKlasifikasi.query.filter_by(nama=nama_user).order_by(HasilKlasifikasi.waktu.desc()).all()
    return render_template('riwayat.html', data=data_riwayat)

@app.route('/riwayat_admin')
@login_required(role='admin')
def riwayat_admin():
    data = HasilKlasifikasi.query.order_by(HasilKlasifikasi.waktu.desc()).all()
    return render_template('riwayat_admin.html', data=data)

@app.route('/hapus_riwayat/<int:id>')
@login_required(role='admin')
def hapus_riwayat(id):
    data = HasilKlasifikasi.query.get_or_404(id)
    db.session.delete(data)
    db.session.commit()
    flash('Data berhasil dihapus.', 'success')
    return redirect(url_for('riwayat_admin'))

@app.route('/kelola_pengguna')
@login_required(role='admin')
def kelola_pengguna():
    users = Pengguna.query.order_by(Pengguna.nama).all()
    return render_template('kelola_pengguna.html', users=users)

@app.route('/admin_dataset', methods=['GET', 'POST'], endpoint='dataset_admin')
@login_required()
def admin_dataset():
    if request.method == 'POST':
        file = request.files.get('file')
        label = request.form.get('label')

        if file and label:
            filename = secure_filename(file.filename)
            save_path = os.path.join('static/uploads', filename)
            file.save(save_path)

            data = Dataset(label=label, filename=filename)
            db.session.add(data)
            db.session.commit()
            flash('Data berhasil diupload.')

    dataset = Dataset.query.order_by(Dataset.id.desc()).all()
    return render_template('admin_dataset.html', dataset=dataset)

@app.route('/admin/upload_dataset', methods=['POST'])
@login_required()
def upload_dataset():
    if 'image' not in request.files or request.form.get('label') is None:
        flash('Lengkapi data upload!', 'danger')
        return redirect(url_for('dataset_admin'))

    file = request.files['image']
    label = request.form.get('label')

    if file.filename == '':
        flash('File tidak dipilih!', 'danger')
        return redirect(url_for('dataset_admin'))

    # Simpan file ke folder static/uploads/
    filename = secure_filename(file.filename)
    save_path = os.path.join('static/uploads', filename)
    file.save(save_path)

    # Simpan ke database
    new_data = Dataset(label=label, filename=filename)
    db.session.add(new_data)
    db.session.commit()

    flash('Gambar berhasil diupload!', 'success')
    return redirect(url_for('dataset_admin'))

# --- MAIN
if __name__ == '__main__':
    print("DEBUG: Memulai server Flask...")
    app.run(host='0.0.0.0', port=5000, debug=True)