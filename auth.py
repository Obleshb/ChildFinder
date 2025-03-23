from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from flask import current_app
from app import login_manager
from models import User
from models import db  # ✅ CORRECT
from forms import LoginForm, RegistrationForm
import logging

auth_bp = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                next_page = request.args.get('next')
                logging.info(f"User {user.email} logged in successfully")
                return redirect(next_page or url_for('main.dashboard'))
            flash('Invalid email or password', 'error')
            logging.warning(f"Failed login attempt for email: {form.email.data}")
        except Exception as e:
            logging.error(f"Login error: {str(e)}")
            flash('An error occurred during login. Please try again.', 'error')
    return render_template('login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            logging.info(f"Attempting to register new user with email: {form.email.data}")
            user = User(
                username=form.username.data,
                email=form.email.data,
                is_authority=form.is_authority.data
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            logging.info(f"Successfully registered user: {user.email}, Authority: {user.is_authority}")
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Registration error: {str(e)}")
            flash('Registration failed. Please try again.', 'error')
    return render_template('register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    if current_user.is_authenticated:
        logging.info(f"User {current_user.email} logged out")
    logout_user()
    return redirect(url_for('main.index'))