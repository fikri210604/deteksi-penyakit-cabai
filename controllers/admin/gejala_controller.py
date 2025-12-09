from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from controllers.admin_controller import admin_only
from models import db, Gejala

gejala_bp = Blueprint("gejala_bp", __name__, url_prefix="/admin/gejala")


# ============================================================
# GENERATE KODE OTOMATIS (G1, G2, G3, ...)
# ============================================================
def _generate_increment_code_gejala():
    all_codes = [g.kode for g in Gejala.query.all() if g.kode]
    all_codes = [c for c in all_codes if c.upper().startswith("G")]

    max_num = 0
    for code in all_codes:
        digits = ''.join(ch for ch in code[1:] if ch.isdigit())
        if digits.isdigit():
            max_num = max(max_num, int(digits))

    return f"G{max_num + 1}"


# ============================================================
# LIST GEJALA
# ============================================================
@gejala_bp.route("/")
@login_required
@admin_only
def index():
    gejala = Gejala.query.order_by(Gejala.kode.asc()).all()
    return render_template("admin/gejala/index.html", gejala=gejala)


# ============================================================
# CREATE
# ============================================================
@gejala_bp.route("/create", methods=["GET", "POST"])
@login_required
@admin_only
def create():
    if request.method == "POST":
        nama = request.form.get("nama")
        deskripsi = request.form.get("deskripsi")
        kode = request.form.get("kode")

        if not nama:
            flash("Nama gejala wajib diisi!", "warning")
            return redirect(url_for("gejala_bp.create"))

        # Jika user tidak mengisi kode → sistem generate sendiri
        if not kode:
            kode = _generate_increment_code_gejala()

        new_gjl = Gejala(
            kode=kode,
            nama=nama,
            deskripsi=deskripsi
        )

        db.session.add(new_gjl)
        db.session.commit()

        flash("Gejala berhasil ditambahkan!", "success")
        return redirect(url_for("gejala_bp.index"))

    return render_template("admin/gejala/create.html")


# ============================================================
# EDIT
# ============================================================
@gejala_bp.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
@admin_only
def edit(id):
    gjl = Gejala.query.get_or_404(id)

    if request.method == "POST":
        gjl.nama = request.form.get("nama")
        gjl.deskripsi = request.form.get("deskripsi")

        # Kode gejala **tidak diizinkan diubah**
        # untuk menjaga konsistensi rule di sistem pakar.

        db.session.commit()
        flash("Gejala berhasil diperbarui!", "success")
        return redirect(url_for("gejala_bp.index"))

    return render_template("admin/gejala/edit.html", gejala=gjl)


# ============================================================
# DELETE
# ============================================================
@gejala_bp.route("/delete/<int:id>", methods=["POST"])
@login_required
@admin_only
def delete(id):
    gjl = Gejala.query.get_or_404(id)

    db.session.delete(gjl)
    db.session.commit()

    flash("Gejala berhasil dihapus!", "info")
    return redirect(url_for("gejala_bp.index"))
