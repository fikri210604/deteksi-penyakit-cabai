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


@rule_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_only
def create():
    gejala = Gejala.query.all()
    penyakit = Penyakit.query.all()

    if request.method == 'POST':
        kode_gejala = request.form.get("kode_gejala")
        kode_penyakit = request.form.get("kode_penyakit")
        tipe_fuzzy = request.form.get("tipe_fuzzy")

        r = Rule(kode_gejala=kode_gejala, kode_penyakit=kode_penyakit, tipe_fuzzy=tipe_fuzzy)
        db.session.add(r)
        db.session.commit()

        flash("Rule berhasil ditambahkan!", "success")
        return redirect(url_for('rule_bp.index'))

    return render_template('admin/rule/create.html', gejala=gejala, penyakit=penyakit)


@rule_bp.route('/delete/<int:id>')
@login_required
@admin_only
def delete(id):
    rule = Rule.query.get_or_404(id)
    db.session.delete(rule)
    db.session.commit()

    flash("Rule berhasil dihapus!", "success")
    return redirect(url_for('rule_bp.index'))


# RULE GROUPS (multi-gejala)
@rule_bp.route('/groups')
@login_required
@admin_only
def groups():
    groups = RuleGroup.query.all()
    return render_template('admin/rule/groups_index.html', groups=groups)


@rule_bp.route('/groups/create', methods=['GET', 'POST'])
@login_required
@admin_only
def groups_create():
    gejala = Gejala.query.all()
    penyakit = Penyakit.query.all()

    if request.method == 'POST':
        nama = request.form.get('nama')
        kode_penyakit = request.form.get('kode_penyakit')
        consequent_term = request.form.get('consequent_term')
        bobot = request.form.get('bobot') or '1'
        aktif = True if request.form.get('aktif') == 'on' else False
        z_override_val = request.form.get('z_override')
        keterangan = request.form.get('keterangan')

        if not kode_penyakit or not consequent_term:
            flash('Penyakit dan konsekuen wajib diisi.', 'warning')
            return redirect(url_for('rule_bp.groups_create'))

        # Ambil pasangan kondisi yang valid (k dan t tidak kosong)
        valid_pairs = [(k, t) for k, t in zip(kode_gejala_list, antecedent_term_list) if k and t]
        if len(valid_pairs) == 0:
            flash('Minimal 1 kondisi gejala harus diisi.', 'warning')
            return redirect(url_for('rule_bp.groups_create'))

        group = RuleGroup(
            nama=nama,
            kode_penyakit=kode_penyakit,
            consequent_term=consequent_term,
            bobot=float(bobot),
            aktif=aktif,
            z_override=(float(z_override_val) if z_override_val not in (None, "") else None),
            keterangan=keterangan
        )
        db.session.add(group)
        db.session.flush()

        for k, t in valid_pairs:
            cond = RuleCondition(group_id=group.id, kode_gejala=k, antecedent_term=t)
            db.session.add(cond)

        db.session.commit()
        flash('Rule group berhasil dibuat.', 'success')
        return redirect(url_for('rule_bp.groups'))

    return render_template('admin/rule/groups_create.html', gejala=gejala, penyakit=penyakit)


@rule_bp.route('/groups/delete/<int:id>')
@login_required
@admin_only
def groups_delete(id):
    grp = RuleGroup.query.get_or_404(id)
    db.session.delete(grp)
    db.session.commit()
    flash('Rule group dihapus.', 'success')
    return redirect(url_for('rule_bp.groups'))


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
        grp.consequent_term = request.form.get('consequent_term')
        grp.bobot = float(request.form.get('bobot') or '1')
        grp.aktif = True if request.form.get('aktif') == 'on' else False
        z_override_val = request.form.get('z_override')
        grp.z_override = float(z_override_val) if z_override_val not in (None, "") else None
        grp.keterangan = request.form.get('keterangan')

        # replace conditions
        # hapus lama
        for c in list(grp.kondisi):
            db.session.delete(c)

        # tambah baru
        kode_gejala_list = request.form.getlist('kode_gejala[]')
        antecedent_term_list = request.form.getlist('antecedent_term[]')
        for k, t in zip(kode_gejala_list, antecedent_term_list):
            if not k or not t:
                continue
            db.session.add(RuleCondition(group_id=grp.id, kode_gejala=k, antecedent_term=t))

        db.session.commit()
        flash('Rule group diperbarui.', 'success')
        return redirect(url_for('rule_bp.groups'))

    return render_template('admin/rule/groups_edit.html', group=grp, gejala=gejala, penyakit=penyakit)
