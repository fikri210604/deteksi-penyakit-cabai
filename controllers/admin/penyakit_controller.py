from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from controllers.admin_controller import admin_only
from models import db, Penyakit

penyakit_bp = Blueprint('penyakit_bp', __name__, url_prefix="/admin/penyakit")


# ==========================================================
# INDEX
# ==========================================================
@penyakit_bp.route('/')
@login_required
@admin_only
def index():
    data = Penyakit.query.order_by(Penyakit.kode_penyakit).all()
    return render_template('admin/penyakit/index.html', penyakit=data)


# ==========================================================
# GENERATE KODE PENYAKIT OTOMATIS (P1, P2, dst)
# ==========================================================
def _generate_increment_code_penyakit():
    all_codes = [p.kode_penyakit for p in Penyakit.query.all() if p.kode_penyakit]
    all_codes = [c for c in all_codes if c.upper().startswith("P")]

    max_num = 0
    for code in all_codes:
        digits = ''.join(ch for ch in code[1:] if ch.isdigit())
        if digits.isdigit():
            max_num = max(max_num, int(digits))

    return f"P{max_num + 1}"


# ==========================================================
# CREATE
# ==========================================================
@penyakit_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_only
def create():
    if request.method == "POST":
        kode = request.form.get("kode")
        nama = request.form.get("nama")
        deskripsi = request.form.get("deskripsi")
        solusi = request.form.get("solusi")

        if not nama:
            flash("Nama penyakit wajib diisi!", "warning")
            return redirect(url_for('penyakit_bp.create'))

        # Auto-generate kode jika kosong
        if not kode:
            kode = _generate_increment_code_penyakit()

        # Pastikan kode unik
        existing = Penyakit.query.filter_by(kode_penyakit=kode).first()
        if existing:
            flash("Kode penyakit sudah digunakan!", "danger")
            return redirect(url_for('penyakit_bp.create'))

        new_p = Penyakit(
            kode_penyakit=kode,
            nama=nama,
            deskripsi=deskripsi,
            solusi=solusi
        )

        db.session.add(new_p)
        db.session.commit()

        flash("Penyakit berhasil ditambahkan!", "success")
        return redirect(url_for('penyakit_bp.index'))

    return render_template('admin/penyakit/create.html')


# ==========================================================
# EDIT
# ==========================================================
@penyakit_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_only
def edit(id):
    penyakit = Penyakit.query.get_or_404(id)

    if request.method == "POST":
        kode = request.form.get('kode')
        nama = request.form.get('nama')
        deskripsi = request.form.get('deskripsi')
        solusi = request.form.get('solusi')

        if not nama:
            flash("Nama penyakit wajib diisi!", "warning")
            return redirect(url_for('penyakit_bp.edit', id=id))

        # Cek kode tidak dipakai penyakit lain
        if kode != penyakit.kode_penyakit:
            exists = Penyakit.query.filter_by(kode_penyakit=kode).first()
            if exists:
                flash("Kode penyakit sudah digunakan penyakit lain!", "danger")
                return redirect(url_for('penyakit_bp.edit', id=id))

        penyakit.kode_penyakit = kode
        penyakit.nama = nama
        penyakit.deskripsi = deskripsi
        penyakit.solusi = solusi

        db.session.commit()

        flash("Penyakit berhasil diperbarui!", "success")
        return redirect(url_for('penyakit_bp.index'))

    return render_template('admin/penyakit/edit.html', p=penyakit)


# ==========================================================
# DELETE
# ==========================================================
@penyakit_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
@admin_only
def delete(id):
    penyakit = Penyakit.query.get_or_404(id)
    
    db.session.delete(penyakit)
    db.session.commit()

    flash("Penyakit berhasil dihapus!", "success")
    return redirect(url_for('penyakit_bp.index'))
