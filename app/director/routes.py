from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import login_required
from app import db
from app.director import director
from app.models import Patient, DirectorReview
from .forms import DirectorReviewForm
from app.decorators import permission_required

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
        if review_record:
            form.populate_obj(review_record)
            flash('Director review updated successfully!', 'success')
        else:
            review_record = DirectorReview(patient_id=patient.id)
            form.populate_obj(review_record)
            db.session.add(review_record)
            flash('Director review saved successfully!', 'success')

        db.session.commit()
        return redirect(url_for('director.index'))

    return render_template('director/review.html', title=f'Reviewing {patient.first_name} {patient.last_name}', patient=patient, form=form)
