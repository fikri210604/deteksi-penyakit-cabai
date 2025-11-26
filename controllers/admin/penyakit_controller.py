from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from controllers.admin_controller import admin_only
from models import db, Penyakit

penyakit_bp = Blueprint('penyakit_bp', __name__, url_prefix="/admin/penyakit")


@penyakit_bp.route('/')
@login_required
@admin_only
def index():
    data = Penyakit.query.all()
    return render_template('admin/penyakit/index.html', penyakit=data)


def _generate_increment_code_penyakit():
    all_codes = [p.kode_penyakit for p in Penyakit.query.all() if p.kode_penyakit]
    all_codes = [c for c in all_codes if c.upper().startswith('P')]
    max_num = 0
    for code in all_codes:
        digits = ''.join(ch for ch in code[1:] if ch.isdigit())
        if digits.isdigit():
            max_num = max(max_num, int(digits))
    return f"P{max_num + 1}"


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

        if not kode:
            kode = _generate_increment_code_penyakit()

        p = Penyakit(kode_penyakit=kode, nama=nama, deskripsi=deskripsi, solusi=solusi)
        db.session.add(p)
        db.session.commit()

        flash("Penyakit berhasil ditambahkan!", "success")
        return redirect(url_for('penyakit_bp.index'))

    return render_template('admin/penyakit/create.html')


@penyakit_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_only
def edit(id):
    penyakit = Penyakit.query.get_or_404(id)

    if request.method == "POST":
        penyakit.kode_penyakit = request.form.get('kode')
        penyakit.nama = request.form.get('nama')
        penyakit.deskripsi = request.form.get('deskripsi')
        penyakit.solusi = request.form.get('solusi')

        db.session.commit()
        flash("Penyakit berhasil diperbarui!", "success")
        return redirect(url_for('penyakit_bp.index'))

    return render_template('admin/penyakit/edit.html', p=penyakit)


@penyakit_bp.route('/delete/<int:id>')
@login_required
@admin_only
def delete(id):
    penyakit = Penyakit.query.get_or_404(id)
    db.session.delete(penyakit)
    db.session.commit()
    
    flash("Penyakit berhasil dihapus!", "success")
    return redirect(url_for('penyakit_bp.index'))
