from flask import Blueprint, Flask, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from models import db, User

# Seragamkan nama blueprint agar konsisten dengan main.py
auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_bp.dashboard'))
        return redirect(url_for('user_bp.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash("Username dan Password wajib diisi!", "warning")
            return render_template('auth/login.html')

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash(f"Selamat datang, {user.username}!", "success")

            if user.role == 'admin':
                return redirect(url_for('admin_bp.dashboard'))
            return redirect(url_for('user_bp.dashboard'))
        else:
            flash("Login gagal. Username atau Password salah.", "danger")

    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin_bp.dashboard'))
        return redirect(url_for('user_bp.dashboard'))

    if request.method == 'POST':
        try:
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')

            if not username or not email or not password:
                flash("Semua kolom wajib diisi!", "warning")
                return render_template('auth/register.html')

            hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')

            new_user = User(username=username, email=email, password=hashed_pw, role='user')
            db.session.add(new_user)
            db.session.commit()

            flash("Registrasi berhasil. Silakan login.", "success")
            return redirect(url_for('auth_bp.login'))

        except IntegrityError:
            db.session.rollback()
            flash("Username atau Email sudah digunakan.", "warning")

        except Exception as e:
            db.session.rollback()
            flash(f"Terjadi kesalahan: {e}", "danger")

    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Anda telah logout.", "info")
    return redirect(url_for('auth_bp.login'))
