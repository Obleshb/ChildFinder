from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, IntegerField, DateField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models import User
from wtforms.validators import DataRequired, Optional

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    is_authority = BooleanField('Register as Authority')


    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class CaseReportForm(FlaskForm):
    child_name = StringField('Child Name', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    date_missing = DateField('Date Missing', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    image = FileField('Upload Image', validators=[DataRequired()])

    # ✅ NEW: Parent Details (Only shown if Authority is filing)
    parent_name = StringField('Parent Name', validators=[Optional()])
    parent_contact = StringField('Parent Contact', validators=[Optional()])

class ImageUploadForm(FlaskForm):
    image = FileField('Upload Image', validators=[DataRequired()])
    location = StringField('Location Found', validators=[DataRequired()])
