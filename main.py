from flask import Flask, render_template
from flask_login import LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from models import db, User, History, Gejala, Penyakit, RuleGroup
from controllers.auth_controller import auth_bp
from controllers.user_controller import user_bp
from controllers.diagnose_controller import diagnosis_bp
from controllers.admin_controller import admin_bp
from controllers.admin.gejala_controller import gejala_bp
from controllers.admin.penyakit_controller import penyakit_bp
from controllers.admin.rule_controller import rule_bp

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth_bp.login"    


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(diagnosis_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(gejala_bp)
app.register_blueprint(penyakit_bp)
app.register_blueprint(rule_bp)


@app.route("/")
def index():
    return render_template("index.html")


@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(403)
def forbidden_error(error):
    return render_template("errors/403.html"), 403


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template("errors/500.html"), 500


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
