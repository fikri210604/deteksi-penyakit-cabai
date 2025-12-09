from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(255))
    role = db.Column(db.String(10), default="user")
    histories = db.relationship("History", back_populates="user", lazy=True)


class Gejala(db.Model):
    __tablename__ = "gejala"
    id = db.Column(db.Integer, primary_key=True)
    kode = db.Column(db.String(10), unique=True)
    nama = db.Column(db.String(100))
    deskripsi = db.Column(db.Text)


class Penyakit(db.Model):
    __tablename__ = "penyakit"
    id = db.Column(db.Integer, primary_key=True)
    kode_penyakit = db.Column(db.String(10), unique=True)
    nama = db.Column(db.String(100))
    deskripsi = db.Column(db.Text)
    solusi = db.Column(db.Text)

class RuleGroup(db.Model):
    __tablename__ = "rule_groups"
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100))
    kode_penyakit = db.Column(db.String(10),db.ForeignKey("penyakit.kode_penyakit"),nullable=False)
    aktif = db.Column(db.Boolean, default=True)
    kondisi = db.relationship("RuleCondition",backref="group",cascade="all, delete-orphan",lazy=True)


class RuleCondition(db.Model):
    __tablename__ = "rule_conditions"
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("rule_groups.id"), nullable=False)
    kode_gejala = db.Column(db.String(10), nullable=False)
    antecedent_term = db.Column(db.String(10), nullable=False)  # S/D/B/T


class History(db.Model):
    __tablename__ = "history"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey("users.id"),nullable=False,)
    kode_penyakit = db.Column(db.String(10), nullable=True)
    nama_penyakit = db.Column(db.String(50), nullable=True)
    skor_fuzzy = db.Column(db.Float, nullable=False)
    gejala_terpilih = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship("User", back_populates="histories")

