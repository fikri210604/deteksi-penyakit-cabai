# controllers/admin_controller.py

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import User, Gejala, Penyakit, RuleGroup, History
from functools import wraps
from flask import redirect, url_for, flash


admin_bp = Blueprint("admin_bp", __name__, url_prefix="/admin")


#   MIDDLEWARE ADMIN ONLY
def admin_only(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            flash("Akses ditolak. Halaman ini hanya untuk Admin.", "warning")
            return redirect(url_for("auth_bp.login"))
        return f(*args, **kwargs)
    return wrapper


#   DASHBOARD ADMIN
@admin_bp.route("/")
@login_required
@admin_only
def dashboard():
    total_user = User.query.count()
    total_gejala = Gejala.query.count()
    total_penyakit = Penyakit.query.count()
    total_rule = RuleGroup.query.count()
    total_history = History.query.count()

    riwayat_terbaru = (
        History.query.order_by(History.timestamp.desc()).limit(10).all()
    )

    return render_template(
        "admin/dashboard.html",
        total_user=total_user,
        total_gejala=total_gejala,
        total_penyakit=total_penyakit,
        total_rule=total_rule,
        total_history=total_history,
        histories=riwayat_terbaru
    )


#   DATA USER (LIST SAJA)
@admin_bp.route("/users")
@login_required
@admin_only
def users():
    users = User.query.all()
    return render_template("admin/users/index.html", users=users)
