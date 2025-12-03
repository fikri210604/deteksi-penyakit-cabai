# controllers/diagnosis_controller.py

from flask import Blueprint, request, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db, Gejala, Penyakit, History
from fuzzy_logic import FuzzyLogic  
import json

diagnosis_bp = Blueprint('diagnosis_bp', __name__)


@diagnosis_bp.route('/diagnose', methods=['POST'])
@login_required
def diagnose():
    try:
        kode_list = request.form.getlist('kode_gejala[]')
        term_list = request.form.getlist('term[]')

        term_to_x = {
            'sedikit': 0.25,
            'sedang': 0.50,
            'banyak': 0.80,
        }

        inputs = {}
        selected_pairs = {}

        for k, t in zip(kode_list, term_list):
            k = (k or "").strip()
            t = (t or "").strip()

            if not k or not t:
                continue

            if t not in term_to_x:
                continue 

            inputs[k] = term_to_x[t]
            selected_pairs[k] = t

        if not inputs:
            flash("Silakan pilih minimal satu gejala dan keterangannya.", "warning")
            return redirect(url_for('user_bp.dashboard'))

        # ============================
        # 2. Proses Fuzzy Logic Sugeno
        # ============================
        fuzzy = FuzzyLogic()
        result = fuzzy.diagnosa(inputs)

        skor_fuzzy = float(result.get("nilai_fuzzy", 0.0))
        skor_map = result.get("skor_penyakit", {}) or {}

        # Tentukan kode penyakit terbaik
        kode_terbaik = max(skor_map, key=skor_map.get) if skor_map else None
        nama_penyakit = result.get("penyakit", "Tidak diketahui")

        # ============================
        # 3. Simpan riwayat diagnosa
        # ============================
        history = History(
            user_id=current_user.id,
            gejala_terpilih=json.dumps(selected_pairs, ensure_ascii=False),
            kode_penyakit=kode_terbaik or "",
            nama_penyakit=nama_penyakit,
            skor_fuzzy=skor_fuzzy,
        )

        db.session.add(history)
        db.session.commit()

        # ============================
        # 4. Ambil info penyakit
        # ============================
        penyakit_info = Penyakit.query.filter_by(kode_penyakit=kode_terbaik).first()

        return render_template(
            "users/result.html",
            result=result,
            info=penyakit_info
        )

    except Exception as e:
        db.session.rollback()
        flash(f"Terjadi kesalahan: {e}", "danger")
        return redirect(url_for('user_bp.dashboard'))
