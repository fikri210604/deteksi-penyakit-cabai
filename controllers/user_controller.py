# controllers/user_controller.py
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from models import Gejala, History

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('admin_bp.dashboard'))
    gejala_list = Gejala.query.all()
    return render_template('users/dashboard.html', symptoms=gejala_list)


@user_bp.route('/history')
@login_required
def history():
    if current_user.role == 'admin':
        return redirect(url_for('admin_bp.dashboard'))
    user_history = (
        History.query.filter_by(user_id=current_user.id)
        .order_by(History.timestamp.desc())
        .all()
    )
    return render_template('users/history.html', histories=user_history)
