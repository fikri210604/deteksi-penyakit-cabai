# controllers/diagnosis_controller.py

from flask import Blueprint, request, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db, Penyakit, Gejala, History
from fuzzy_logic import FuzzyLogic
import json

diagnosis_bp = Blueprint('diagnosis_bp', __name__)


# ======================================================
# KONVERSI SLIDER → X (0–1) + LABEL LINGUISTIK
# ======================================================
def _label_linguistik_from_percent(v: float):
    """Convert persen 0–100 → x (0–1) + label linguistik."""
    x = max(0.0, min(1.0, v / 100.0))

    if v <= 10:
        label = "Tidak Ada"
    elif v <= 35:
        label = "Sedikit"
    elif v <= 60:
        label = "Sedang"
    elif v <= 85:
        label = "Banyak"
    else:
        label = "Sangat Banyak"

    return x, label


# ======================================================
# ROUTE DIAGNOSA
# ======================================================
@diagnosis_bp.route('/diagnose', methods=['POST'])
@login_required
def diagnose():
    try:
        print("FORM MASUK:", request.form)

        # ----------------------------------------------
        # 1. PARSE INPUT DINAMIS nilai[Gx]
        # ----------------------------------------------
        gejala_values = {}      
        gejala_linguistik = {} 

        for key, values in request.form.lists():
            if key.startswith("nilai[") and key.endswith("]"):
                kode = key[6:-1].strip()     

                if not kode:
                    continue

                try:
                    v = float(values[0])      # nilai slider 0–100
                except:
                    continue

                x, label = _label_linguistik_from_percent(v)

                # simpan untuk fuzzy
                gejala_values[kode] = x

                # simpan untuk tampilan & history
                gejala_linguistik[kode] = {
                    "persen": v,
                    "x": x,
                    "label": label
                }

        # ----------------------------------------------
        #  VALIDASI: Minimal 1 input valid
        # ----------------------------------------------
        if not gejala_values:
            flash("Silakan masukkan minimal satu nilai gejala.", "warning")
            return redirect(url_for('user_bp.dashboard'))

        # ----------------------------------------------
        # 2. PROSES FUZZY TSUKAMOTO
        # ----------------------------------------------
        fuzzy = FuzzyLogic()
        result = fuzzy.diagnosa(gejala_values)

        skor_map = result.get("skor_penyakit", {})
        skor_fuzzy = float(result.get("nilai_fuzzy", 0.0))

        kode_terbaik = max(skor_map, key=skor_map.get) if skor_map else None
        penyakit_obj = (
            Penyakit.query.filter_by(kode_penyakit=kode_terbaik).first()
            if kode_terbaik else None
        )

        nama_penyakit = penyakit_obj.nama if penyakit_obj else "Tidak Teridentifikasi"

        # ----------------------------------------------
        # 3. SIMPAN HISTORY
        # ----------------------------------------------
        history = History(
            user_id=current_user.id,
            kode_penyakit=kode_terbaik or "",
            nama_penyakit=nama_penyakit,
            skor_fuzzy=skor_fuzzy,
            gejala_terpilih=json.dumps(gejala_linguistik, ensure_ascii=False),
        )

        db.session.add(history)
        db.session.commit()

        # ----------------------------------------------
        # 4. TAMPILKAN HASIL
        # ----------------------------------------------
        # siapkan mapping kode->nama penyakit untuk label chart
        penyakit_map = {p.kode_penyakit: p.nama for p in Penyakit.query.all()}
        # siapkan mapping kode gejala -> objek Gejala untuk tabel hasil
        symptoms_map = {g.kode: g for g in Gejala.query.all()}

        return render_template(
            "users/result.html",
            result=result,
            info=penyakit_obj,
            gejala_linguistik=gejala_linguistik,
            penyakit_map=penyakit_map,
            symptoms_map=symptoms_map,
        )

    except Exception as e:
        db.session.rollback()
        flash(f"Terjadi kesalahan: {e}", "danger")
        return redirect(url_for('user_bp.dashboard'))
