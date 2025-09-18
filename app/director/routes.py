from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import login_required
from app import db
from app.director import director
from app.models import Patient, DirectorReview, Spirometry, Audiometry, ECG
from .forms import DirectorReviewForm
from app.decorators import permission_required
from datetime import datetime

@director.route('/', methods=['GET', 'POST'])
@login_required
@permission_required('access_director_page')
def index():
    """
    Search page for the Director to find a patient.
    """
    if request.method == 'POST':
        search_term = request.form.get('search_term', '').strip()
        company = request.form.get('company', 'DCP')
        year = request.form.get('year', '2025')

        if not search_term:
            flash('Please enter a Staff ID to search.', 'warning')
            return redirect(url_for('director.index'))

        patients = Patient.query.filter_by(company=company, screening_year=year)\
                                .filter(Patient.staff_id.ilike(f'%{search_term}%')).all()

        return render_template('director/index.html', title='Search Results', patients=patients, search_term=search_term)

    return render_template('director/index.html', title='Director Review - Search Patient')


from flask import jsonify

@director.route('/api/search')
@login_required
@permission_required('access_director_page')
def api_search():
    search_term = request.args.get('q', '')
    company = request.args.get('company', 'DCP')
    year = request.args.get('year', datetime.now().year, type=int)

    if not search_term:
        return jsonify([])

    patients = Patient.query.filter_by(company=company, screening_year=year)\
                            .filter(Patient.staff_id.ilike(f'%{search_term}%')).limit(10).all()

    return jsonify([{
        'id': p.id,
        'staff_id': p.staff_id,
        'first_name': p.first_name,
        'last_name': p.last_name,
        'department': p.department
    } for p in patients])

@director.route('/review/<int:patient_id>', methods=['GET', 'POST'])
@login_required
@permission_required('access_director_page')
def review(patient_id):
    """
    Main page for the director to review a patient's full details and submit a review.
    """
    patient = Patient.query.options(
        db.joinedload(Patient.consultation),
        db.joinedload(Patient.full_blood_count),
        db.joinedload(Patient.kidney_function_test),
        db.joinedload(Patient.lipid_profile),
        db.joinedload(Patient.liver_function_test),
        db.joinedload(Patient.ecg),
        db.joinedload(Patient.spirometry),
        db.joinedload(Patient.audiometry),
        db.joinedload(Patient.director_review)
    ).get_or_404(patient_id)

    review_record = patient.director_review
    form = DirectorReviewForm(obj=review_record)

    if form.validate_on_submit():
        # 1. Handle the Director's own review comments
        if not review_record:
            review_record = DirectorReview(patient_id=patient.id)
            db.session.add(review_record)
        form.populate_obj(review_record)

        # 2. Handle the editable test results
        # Spirometry
        if 'spirometry_result' in request.form:
            if patient.spirometry:
                patient.spirometry.spirometry_result = request.form.get('spirometry_result')
            else:
                new_spirometry = Spirometry(patient_id=patient.id, spirometry_result=request.form.get('spirometry_result'))
                db.session.add(new_spirometry)

        # Audiometry
        if 'audiometry_result' in request.form:
            if patient.audiometry:
                patient.audiometry.audiometry_result = request.form.get('audiometry_result')
            else:
                new_audiometry = Audiometry(patient_id=patient.id, audiometry_result=request.form.get('audiometry_result'))
                db.session.add(new_audiometry)

        # ECG
        if 'ecg_result' in request.form:
            if patient.ecg:
                patient.ecg.ecg_result = request.form.get('ecg_result')
            else:
                new_ecg = ECG(patient_id=patient.id, ecg_result=request.form.get('ecg_result'))
                db.session.add(new_ecg)

        db.session.commit()
        flash('Patient review and results have been updated successfully!', 'success')
        return redirect(url_for('director.review', patient_id=patient.id))

    # Pre-populate form with existing data for GET request (already done by obj=review_record)
    return render_template('director/review.html', title=f'Reviewing {patient.first_name} {patient.last_name}', patient=patient, form=form)
