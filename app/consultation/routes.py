from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import login_required
from app import db
from app.consultation import consultation
from app.models import Patient, Consultation
from .forms import ConsultationForm

from flask import session

@consultation.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        search_term = request.form.get('search_term', '').strip()
        company = session.get('company', 'DCP')
        year = session.get('year', 2025)

        if not search_term:
            flash('Please enter a Staff ID to search.', 'warning')
            return redirect(url_for('consultation.index'))

        patients = Patient.query.filter_by(company=company, screening_year=year)\
                                .filter(Patient.staff_id.ilike(f'%{search_term}%')).all()
        return render_template('consultation/index.html', title='Search Results', patients=patients, search_term=search_term)

    return render_template('consultation/index.html', title='Consultation - Search')

@consultation.route('/form/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def consultation_form(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    # Check if a consultation already exists for this patient
    consultation_record = Consultation.query.filter_by(patient_id=patient.id).first()

    form = ConsultationForm(obj=consultation_record) # Pre-populate form if record exists

    if form.validate_on_submit():
        if consultation_record:
            # Update existing record
            form.populate_obj(consultation_record)
            flash('Consultation record updated successfully!', 'success')
        else:
            # Create new record
            consultation_record = Consultation(patient_id=patient.id)
            form.populate_obj(consultation_record)
            db.session.add(consultation_record)
            flash('Consultation record saved successfully!', 'success')

        db.session.commit()
        return redirect(url_for('consultation.index'))

    return render_template('consultation/form.html', title='Consultation', form=form, patient=patient)
