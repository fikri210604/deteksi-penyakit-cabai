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

    def norm_term_to_x(term: str):
        if not isinstance(term, str):
            return None
        key = term.strip().lower().replace(' ', '_')
        return term_to_x.get(key)

    inputs = {}
    display_gejala = {}

    for k, t in (selected_pairs or {}).items():
        kode = (k or '').strip()
        x_val = None
        label_text = None

        if isinstance(t, dict):
            # format baru: {'persen': v, 'x': x, 'label': label}
            if 'x' in t:
                try:
                    x_val = float(t.get('x'))
                except Exception:
                    x_val = None
            elif 'persen' in t:
                try:
                    x_val = float(t.get('persen')) / 100.0
                except Exception:
                    x_val = None
            if 'label' in t and isinstance(t.get('label'), str):
                label_text = t.get('label')
            # fallback: jika belum ada label, derive dari x
            if label_text is None and isinstance(x_val, (float, int)):
                # ringkas: aproksimasi label dari batas di dashboard
                v = x_val * 100.0
                label_text = (
                    'Tidak Ada' if v <= 10 else
                    'Sedikit' if v <= 35 else
                    'Sedang' if v <= 60 else
                    'Banyak' if v <= 85 else
                    'Sangat Banyak'
                )
            # jika tidak ada x, coba konversi dari label
            if x_val is None and label_text:
                x_val = norm_term_to_x(label_text)
        else:
            # format lama: t adalah string term seperti 'sedikit'/'banyak'
            if isinstance(t, str):
                x_val = norm_term_to_x(t)
                label_text = t

        if isinstance(x_val, (float, int)):
            # clamp 0..1
            x_val = max(0.0, min(1.0, float(x_val)))
            inputs[kode] = x_val
            display_gejala[kode] = {
                'x': x_val,
                'label': label_text or ''
            }

    result = {'penyakit': h.nama_penyakit, 'nilai_fuzzy': float(h.skor_fuzzy or 0.0), 'skor_penyakit': {}}
    if inputs:
        try:
            fuzzy = FuzzyLogic()
            result = fuzzy.diagnosa(inputs)
        except Exception:
            # fallback ke data tersimpan jika terjadi error saat rekalkulasi
            pass

    penyakit_info = Penyakit.query.filter_by(nama=result.get('penyakit', '')).first()

    # map tambahan untuk template result
    penyakit_map = {p.kode_penyakit: p.nama for p in Penyakit.query.all()}
    symptoms_map = {g.kode: g for g in Gejala.query.all()}

    return render_template(
        'users/result.html',
        result=result,
        info=penyakit_info,
        gejala_linguistik=display_gejala,
        penyakit_map=penyakit_map,
        symptoms_map=symptoms_map,
    )
