from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from controllers.admin_controller import admin_only
from models import db, Gejala, Penyakit, RuleGroup, RuleCondition

rule_bp = Blueprint('rule_bp', __name__, url_prefix="/admin/rule")

@rule_bp.route('/')
@login_required
@admin_only
def index():
    return redirect(url_for('rule_bp.groups'))


# ================================
# GROUP LIST
# ================================
@rule_bp.route('/groups')
@login_required
@admin_only
def groups():
    groups = RuleGroup.query.all()
    return render_template('admin/rule/groups_index.html', groups=groups)


# ================================
# GROUP CREATE
# ================================
@rule_bp.route('/groups/create', methods=['GET', 'POST'])
@login_required
@admin_only
def groups_create():
    gejala = Gejala.query.all()
    penyakit = Penyakit.query.all()

    if request.method == 'POST':
        nama = request.form.get('nama')
        kode_penyakit = request.form.get('kode_penyakit')

        # list kondisi
        kode_gejala_list = request.form.getlist("kode_gejala[]")
        antecedent_term_list = request.form.getlist("antecedent_term[]")

        valid_pairs = [(k, t) for k, t in zip(kode_gejala_list, antecedent_term_list) if k and t]

        if not kode_penyakit:
            flash("Penyakit wajib dipilih.", "warning")
            return redirect(url_for('rule_bp.groups_create'))

        if not valid_pairs:
            flash("Minimal 1 kondisi gejala harus diisi.", "warning")
            return redirect(url_for('rule_bp.groups_create'))

        group = RuleGroup(
            nama=nama,
            kode_penyakit=kode_penyakit,
        )
        db.session.add(group)
        db.session.flush()  

        for k, t in valid_pairs:
            db.session.add(RuleCondition(group_id=group.id, kode_gejala=k, antecedent_term=t))

        db.session.commit()
        flash("Rule group berhasil dibuat!", "success")
        return redirect(url_for('rule_bp.groups'))

    return render_template('admin/rule/groups_create.html', gejala=gejala, penyakit=penyakit)


# ================================
# GROUP DELETE
# ================================
@rule_bp.route('/groups/delete/<int:id>')
@login_required
@admin_only
def groups_delete(id):
    grp = RuleGroup.query.get_or_404(id)
    db.session.delete(grp)
    db.session.commit()
    flash("Rule group berhasil dihapus!", "success")
    return redirect(url_for('rule_bp.groups'))


# ================================
# GROUP EDIT
# ================================
@rule_bp.route('/groups/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_only
def groups_edit(id):
    grp = RuleGroup.query.get_or_404(id)
    gejala = Gejala.query.all()
    penyakit = Penyakit.query.all()

    if request.method == 'POST':
        grp.nama = request.form.get('nama')
        grp.kode_penyakit = request.form.get('kode_penyakit')

        # hapus semua kondisi lama
        for c in grp.kondisi:
            db.session.delete(c)

        kode_gejala_list = request.form.getlist("kode_gejala[]")
        antecedent_term_list = request.form.getlist("antecedent_term[]")

        for k, t in zip(kode_gejala_list, antecedent_term_list):
            if k and t:
                db.session.add(RuleCondition(group_id=grp.id, kode_gejala=k, antecedent_term=t))

        db.session.commit()
        flash("Rule group berhasil diperbarui!", "success")
        return redirect(url_for('rule_bp.groups'))

    return render_template('admin/rule/groups_edit.html', group=grp, gejala=gejala, penyakit=penyakit)
