import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask import send_from_directory
from werkzeug.utils import secure_filename
import os
from datetime import datetime

from app import app, db
from models import Case, MatchResult
from forms import CaseReportForm, ImageUploadForm
from face_detection import FaceDetector

UPLOAD_FOLDER = os.path.abspath("uploads")

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

main_bp = Blueprint('main', __name__)
face_detector = FaceDetector()
logging.basicConfig(level=logging.INFO) #added logging configuration

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_authority:
        cases = Case.query.all()
    else:
        cases = Case.query.filter_by(reporter_id=current_user.id).all()
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
            # Fix: Store only the filename in the database, not the full path
            image_filename = f'{timestamp}_{filename}'
            # Fix: Use os.path.join for the full path when saving
            full_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)

            # Ensure upload directory exists
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

            logging.info(f"Saving case image to: {full_path}")
            image.save(full_path)

            case = Case(
                child_name=form.child_name.data,
                age=form.age.data,
                location=form.location.data,
                date_missing=form.date_missing.data,
                description=form.description.data,
                image_path=image_filename,  # Store only filename
                reporter_id=current_user.id
            )
            db.session.add(case)
            db.session.commit()
            logging.info(f"Case reported successfully. ID: {case.id}")
            flash('Case reported successfully', 'success')
            return redirect(url_for('main.dashboard'))
        except Exception as e:
            logging.error(f"Error reporting case: {str(e)}", exc_info=True)
            flash(f'Error reporting case: {str(e)}', 'error')
    return render_template('report_case.html', form=form)

@main_bp.route('/case_management')
@login_required
def case_management():
    if not current_user.is_authority:
        flash('Access denied. Authority privileges required.', 'error')
        return redirect(url_for('main.dashboard'))

    active_cases = Case.query.filter_by(status='open').all()
    found_cases = Case.query.filter_by(status='found').all()
    pending_matches = MatchResult.query.filter_by(status='pending').all()
    search_results = request.args.get('search_results', None)

    return render_template('case_management.html',
                         active_cases=active_cases,
                         found_cases=found_cases,
                         pending_matches=pending_matches,
                         search_results=search_results)

@main_bp.route('/search_database', methods=['POST'])
@login_required
def search_database():
    if not current_user.is_authority:
        flash('Access denied. Authority privileges required.', 'error')
        return redirect(url_for('main.dashboard'))

    try:
        image = request.files['search_image']
        min_confidence = float(request.form.get('confidence', 60)) / 100

        logging.info(f"Processing image search with minimum confidence: {min_confidence}")

        if not image:
            flash('No image file provided', 'error')
            return redirect(url_for('main.case_management'))

        filename = secure_filename(image.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        search_filename = f'search_{timestamp}_{filename}'
        search_image_path = os.path.join(app.config['UPLOAD_FOLDER'], search_filename)

        # Ensure the upload directory exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        # Save the uploaded image
        image.save(search_image_path)
        logging.info(f"Saved search image to: {search_image_path}")

        results = []
        cases = Case.query.filter_by(status='open').all()  # Only search among open cases
        logging.info(f"Comparing against {len(cases)} open cases in database")

        for case in cases:
            # Fix: Build full path for case image
            case_image_path = os.path.join(app.config['UPLOAD_FOLDER'], case.image_path)
            if not os.path.exists(case_image_path):
                logging.warning(f"Case image not found: {case_image_path}")
                continue

            logging.info(f"Comparing with case #{case.id} - {case.child_name}")
            confidence = face_detector.compare_faces(search_image_path, case_image_path)
            logging.info(f"Confidence score for case #{case.id}: {confidence}")

            if confidence >= min_confidence:
                # Save the match result in database
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
            logging.info(f"Found {len(results)} matches above confidence threshold")
            return render_template('case_management.html',
                               active_cases=Case.query.filter_by(status='open').all(),
                               found_cases=Case.query.filter_by(status='found').all(),
                               pending_matches=MatchResult.query.filter_by(status='pending').all(),
                               search_results=results)
        else:
            logging.info("No matches found above confidence threshold")
            flash('No matches found above the specified confidence threshold.', 'info')
            return redirect(url_for('main.case_management'))

    except Exception as e:
        logging.error(f"Error processing search: {str(e)}", exc_info=True)
        flash(f'Error processing search: {str(e)}', 'error')
        return redirect(url_for('main.case_management'))

@main_bp.route('/case/<int:case_id>')
@login_required
def case_detail(case_id):
    case = Case.query.get_or_404(case_id)
    if not current_user.is_authority and case.reporter_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('main.dashboard'))
    return render_template('case_detail.html', case=case)

@main_bp.route('/upload_found', methods=['GET', 'POST'])
@login_required
def upload_found():
    form = ImageUploadForm()
    if form.validate_on_submit():
        try:
            image = form.image.data
            filename = secure_filename(image.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            image_path = f'uploads/found_{timestamp}_{filename}'
            full_path = os.path.join(app.config['UPLOAD_FOLDER'], f'found_{timestamp}_{filename}')
            image.save(full_path)

            # Compare with all open cases
            open_cases = Case.query.filter_by(status='open').all()
            for case in open_cases:
                confidence = face_detector.compare_faces(
                    os.path.join(app.config['UPLOAD_FOLDER'], case.image_path),
                    full_path
                )
                if confidence > 0.6:  # Threshold for potential match
                    match_result = MatchResult(
                        case_id=case.id,
                        found_image_path=image_path,
                        confidence_score=confidence
                    )
                    db.session.add(match_result)

            db.session.commit()
            flash('Image uploaded and processed successfully', 'success')
            return redirect(url_for('main.dashboard'))

        except Exception as e:
            flash(f'Error processing image: {str(e)}', 'error')
    return render_template('upload_found.html', form=form)

@main_bp.route('/about')
def about():
    return render_template('about.html')

@main_bp.route('/contact')
def contact():
    return render_template('contact.html')