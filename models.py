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

from app import db
from datetime import datetime

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

    # ✅ Link case to reporter
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    reporter = db.relationship('User', backref=db.backref('cases', lazy=True))

    # ✅ NEW: Parent Details (Only for cases filed by Authority)
    parent_name = db.Column(db.String(100), nullable=True)
    parent_contact = db.Column(db.String(20), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ReunitedCase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('missing_case.id'), nullable=False)  # ✅ Correct table reference
    child_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(255), nullable=False)
    date_missing = db.Column(db.Date, nullable=False)
    date_reunited = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    description = db.Column(db.Text, nullable=True)
    image_path = db.Column(db.String(255), nullable=True)

    case = db.relationship('Case', backref=db.backref('reunited_cases', lazy=True))  # ✅ Ensure correct relationship


class MatchResult(db.Model):
    __tablename__ = 'match_result'
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('missing_case.id'))
    found_image_path = db.Column(db.String(255))
    confidence_score = db.Column(db.Float)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


