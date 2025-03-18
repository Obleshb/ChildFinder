from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    is_authority = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Case(db.Model):
    __tablename__ = 'missing_case'
    id = db.Column(db.Integer, primary_key=True)
    child_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    date_missing = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text)
    image_path = db.Column(db.String(255))
    status = db.Column(db.String(20), default='open')
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    matches = db.relationship('MatchResult', backref='case', lazy=True)

class MatchResult(db.Model):
    __tablename__ = 'match_result'
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('missing_case.id'))
    found_image_path = db.Column(db.String(255))
    confidence_score = db.Column(db.Float)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)