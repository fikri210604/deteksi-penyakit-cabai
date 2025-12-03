# controllers/user_controller.py
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Gejala, History, Penyakit
from fuzzy_logic import FuzzyLogic
import json

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


@user_bp.route('/history/<int:history_id>')
@login_required
def history_detail(history_id: int):
    if current_user.role == 'admin':
        return redirect(url_for('admin_bp.dashboard'))

    h = History.query.filter_by(id=history_id, user_id=current_user.id).first()
    if not h:
        flash('Riwayat tidak ditemukan atau bukan milik Anda.', 'warning')
        return redirect(url_for('user_bp.history'))

    try:
        selected_pairs = json.loads(h.gejala_terpilih or '{}')
    except Exception:
        selected_pairs = {}

    term_to_x = {
        'tidak_ada': 0.05,
        'sedikit': 0.25,
        'sedang': 0.5,
        'banyak': 0.8,
        'sangat_banyak': 0.95,
    }

    inputs = {}
    for k, t in (selected_pairs or {}).items():
        t = (t or '').strip()
        if t in term_to_x:
            inputs[(k or '').strip()] = term_to_x[t]

    result = {'penyakit': h.nama_penyakit, 'nilai_fuzzy': float(h.skor_fuzzy or 0.0), 'skor_penyakit': {}}
    if inputs:
        try:
            fuzzy = FuzzyLogic()
            result = fuzzy.diagnosa(inputs)
        except Exception:
            # fallback ke data tersimpan jika terjadi error saat rekalkulasi
            pass

    penyakit_info = Penyakit.query.filter_by(nama=result.get('penyakit', '')).first()

    return render_template('users/result.html', result=result, info=penyakit_info)
