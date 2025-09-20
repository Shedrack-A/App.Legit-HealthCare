from flask import render_template, request, redirect, url_for, flash, abort, jsonify, session
from flask_login import login_required
from app import db
from app.consultation import consultation
from app.models import Patient, Consultation
from .forms import ConsultationForm

@consultation.route('/')
@login_required
def index():
    return render_template('consultation/index.html', title='Search Patient')

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

@consultation.route('/api/search_patient')
@login_required
def api_search_patient():
    search_term = request.args.get('q', '')
    company = session.get('company', 'DCP')
    year = session.get('year', 2024)

    if not search_term:
        return jsonify([])

    patients = Patient.query.filter(
        Patient.staff_id.ilike(f'%{search_term}%'),
        Patient.company == company,
        Patient.screening_year == year
    ).limit(10).all()

    return jsonify([{
        'id': p.id,
        'staff_id': p.staff_id,
        'first_name': p.first_name,
        'last_name': p.last_name,
        'department': p.department
    } for p in patients])
