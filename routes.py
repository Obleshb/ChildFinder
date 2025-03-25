import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from datetime import datetime

from app import app, db
from models import Case, MatchResult, ReunitedCase, User
from forms import CaseReportForm, ImageUploadForm
from face_detection import FaceDetector

UPLOAD_FOLDER = os.path.abspath("uploads")

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

main_bp = Blueprint('main', __name__)
face_detector = FaceDetector()
logging.basicConfig(level=logging.INFO)

@main_bp.route('/case_management')
@login_required
def case_management():
    if not current_user.is_authority:
        flash('Access denied. Authority privileges required.', 'error')
        return redirect(url_for('main.dashboard'))

    active_cases = Case.query.filter_by(status='open').all()
    found_cases = Case.query.filter_by(status='found').all()
    pending_matches = MatchResult.query.filter_by(status='pending').all()
    reunited_cases = ReunitedCase.query.all()

    return render_template('case_management.html',
                           active_cases=active_cases,
                           found_cases=found_cases,
                           pending_matches=pending_matches,
                           reunited_cases=reunited_cases)

@main_bp.route('/review_match/<int:match_id>')
@login_required
def review_match(match_id):
    match = MatchResult.query.get_or_404(match_id)
    case = Case.query.get_or_404(match.case_id)
    return render_template('review_page.html', match=match, case=case)

@main_bp.route('/handle_match_decision/<int:match_id>', methods=['POST'])
@login_required
def handle_match_decision(match_id):
    match = MatchResult.query.get_or_404(match_id)
    case = Case.query.get_or_404(match.case_id)

    decision = request.form.get('decision')

    if decision == "confirm":
        match.status = 'confirmed'
        case.status = 'found'
        db.session.commit()

        reunited_case = ReunitedCase(
            case_id=case.id,
            child_name=case.child_name,
            age=case.age,
            location=case.location,
            date_missing=case.date_missing,
            date_reunited=datetime.utcnow(),
            description=case.description,
            image_path=case.image_path
        )
        db.session.add(reunited_case)
        db.session.commit()

        flash("Match confirmed! Child added to reunited cases.", "success")
    else:
        match.status = 'rejected'
        db.session.commit()
        flash("Match rejected.", "danger")

    return redirect(url_for('main.case_management'))

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    cases = Case.query.all() if current_user.is_authority else Case.query.filter_by(reporter_id=current_user.id).all()
    return render_template('dashboard.html', cases=cases)

@main_bp.route('/report_case', methods=['GET', 'POST'])
@login_required
def report_case():
    form = CaseReportForm()
    if form.validate_on_submit():
        try:
            image = form.image.data
            filename = secure_filename(image.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            image_filename = f'{timestamp}_{filename}'
            full_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)

            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            image.save(full_path)

            # ✅ Check if a case with the same name and missing date exists
            existing_case = Case.query.filter_by(child_name=form.child_name.data, date_missing=form.date_missing.data).first()

            # ✅ Check if uploaded image matches any existing case
            cases = Case.query.all()
            for case in cases:
                case_image_path = os.path.join(app.config['UPLOAD_FOLDER'], case.image_path)
                if os.path.exists(case_image_path):
                    similarity = face_detector.compare_faces(full_path, case_image_path)
                    if similarity > 0.8:  # 80% similarity threshold
                        existing_case = case  # Set the existing case for later use
                        break

            if existing_case:
                # ✅ If an authority is reporting, show "Show Details" button
                if current_user.is_authority:
                    return render_template('report_case.html', form=form, existing_case=existing_case)

                else:
                    # ✅ If a normal user is reporting, show reporter name & email
                    reporter = User.query.get(existing_case.reporter_id)
                    flash(f"⚠️ This case has already been reported by {reporter.username} (Email: {reporter.email}).", "danger")
                    return redirect(url_for('main.report_case'))

            # ✅ If no duplicate is found, proceed with saving the new case
            parent_name = form.parent_name.data if current_user.is_authority else None
            parent_contact = form.parent_contact.data if current_user.is_authority else None

            new_case = Case(
                child_name=form.child_name.data,
                age=form.age.data,
                location=form.location.data,
                date_missing=form.date_missing.data,
                description=form.description.data,
                image_path=image_filename,
                reporter_id=current_user.id,
                parent_name=parent_name,
                parent_contact=parent_contact
            )
            db.session.add(new_case)
            db.session.commit()
            flash('✅ Case reported successfully!', 'success')
            return redirect(url_for('main.dashboard'))

        except Exception as e:
            logging.error(f"Error reporting case: {str(e)}", exc_info=True)
            flash(f'Error reporting case: {str(e)}', 'danger')

    return render_template('report_case.html', form=form, existing_case=None)


@main_bp.route('/case/<int:case_id>')
@login_required
def case_detail(case_id):
    case = Case.query.get_or_404(case_id)
    reporter = User.query.get(case.reporter_id)
    matches = MatchResult.query.filter_by(case_id=case.id).all()

    if not current_user.is_authority and case.reporter_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))

    return render_template('case_detail.html', case=case, reporter=reporter, matches=matches)

@main_bp.route('/search_database', methods=['POST'])
@login_required
def search_database():
    if not current_user.is_authority:
        flash('Access denied. Authority privileges required.', 'error')
        return redirect(url_for('main.dashboard'))

    try:
        image = request.files['search_image']
        min_confidence = float(request.form.get('confidence', 60)) / 100

        if not image:
            flash('No image file provided', 'error')
            return redirect(url_for('main.case_management'))

        filename = secure_filename(image.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        search_filename = f'search_{timestamp}_{filename}'
        search_image_path = os.path.join(app.config['UPLOAD_FOLDER'], search_filename)

        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        image.save(search_image_path)

        results = []
        cases = Case.query.filter_by(status='open').all()

        for case in cases:
            case_image_path = os.path.join(app.config['UPLOAD_FOLDER'], case.image_path)
            if not os.path.exists(case_image_path):
                continue

            confidence = face_detector.compare_faces(search_image_path, case_image_path)
            if confidence >= min_confidence:
                match_result = MatchResult(
                    case_id=case.id,
                    found_image_path=search_filename,
                    confidence_score=confidence,
                    status='pending'
                )
                db.session.add(match_result)
                results.append({'case': case, 'confidence': confidence, 'match': match_result})

        if results:
            db.session.commit()
            return render_template('case_management.html',
                                   active_cases=Case.query.filter_by(status='open').all(),
                                   found_cases=Case.query.filter_by(status='found').all(),
                                   pending_matches=MatchResult.query.filter_by(status='pending').all(),
                                   search_results=results)
        else:
            flash('No matches found above the specified confidence threshold.', 'info')
            return redirect(url_for('main.case_management'))

    except Exception as e:
        logging.error(f"Error processing search: {str(e)}", exc_info=True)
        flash(f'Error processing search: {str(e)}', 'error')
        return redirect(url_for('main.case_management'))

@main_bp.route('/about')
def about():
    return render_template('about.html')

@main_bp.route('/contact')
def contact():
    return render_template('contact.html')
