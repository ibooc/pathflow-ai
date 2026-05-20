from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    target_role = db.Column(db.String(100), default='')
    skills = db.Column(db.Text, default='')
    python_level = db.Column(db.Integer, default=0)
    web_level = db.Column(db.Integer, default=0)
    data_level = db.Column(db.Integer, default=0)
    ml_level = db.Column(db.Integer, default=0)
    sql_level = db.Column(db.Integer, default=0)
    roadmaps_count = db.Column(db.Integer, default=0)
    scans_count = db.Column(db.Integer, default=0)
    interviews_count = db.Column(db.Integer, default=0)
    projects_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)