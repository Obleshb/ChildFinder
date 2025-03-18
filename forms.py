from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, IntegerField, DateField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models import User

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

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

class CaseReportForm(FlaskForm):
    child_name = StringField('Child Name', validators=[DataRequired(), Length(max=100)])
    age = IntegerField('Age', validators=[DataRequired()])
    location = StringField('Last Known Location', validators=[DataRequired(), Length(max=200)])
    date_missing = DateField('Date Missing', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    image = FileField('Child Photo', validators=[DataRequired()])

class ImageUploadForm(FlaskForm):
    image = FileField('Upload Image', validators=[DataRequired()])
    location = StringField('Location Found', validators=[DataRequired()])
