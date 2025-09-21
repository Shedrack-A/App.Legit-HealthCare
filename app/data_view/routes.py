from flask import render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_required
from sqlalchemy import or_
from app.data_view import data_view
from app.models import Patient
from app import db
from app.patient.forms import PatientRegistrationForm
from datetime import date
from app.utils import log_audit

@data_view.route('/all')
@login_required
def view_all_patients():
    page = request.args.get('page', 1, type=int)
    patients = Patient.query.order_by(Patient.date_registered.desc()).paginate(
        page=page, per_page=20)
    return render_template('data_view/view_all.html', title='All Patients', patients=patients)

@data_view.route('/delete/<int:patient_id>', methods=['POST'])
@login_required
def delete_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    # Note: This is a hard delete. It will also delete associated consultation and test results
    # due to the cascade effect of the database relationships if configured, or it will fail
    # if not. For now, we assume this is the desired behavior.
    # A soft delete (marking as inactive) might be a better approach in a real-world scenario.
    log_audit('DELETE_PATIENT', f'Patient deleted: {patient.staff_id} (ID: {patient.id})')
    db.session.delete(patient)
    db.session.commit()
    flash(f'Patient {patient.first_name} {patient.last_name} has been deleted.', 'success')
    return redirect(url_for('data_view.view_all_patients'))

def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, today.day))

@data_view.route('/edit/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def edit_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    form = PatientRegistrationForm(obj=patient)

    # We need to prevent validation on fields that should be unique, but are already set for this user
    if form.validate_on_submit():
        patient.staff_id = form.staff_id.data
        patient.patient_id = form.patient_id.data
        patient.first_name = form.first_name.data
        patient.middle_name = form.middle_name.data
        patient.last_name = form.last_name.data
        patient.department = form.department.data
        patient.gender = form.gender.data
        patient.date_of_birth = form.date_of_birth.data
        patient.age = calculate_age(form.date_of_birth.data)
        patient.contact_phone = form.contact_phone.data
        patient.email_address = form.email_address.data
        patient.race = form.race.data
        patient.nationality = form.nationality.data
        db.session.commit()
        log_audit('EDIT_PATIENT', f'Patient edited: {patient.staff_id} (ID: {patient.id})')
        flash('Patient information has been updated.', 'success')
        return redirect(url_for('data_view.view_all_patients'))

    return render_template('data_view/edit_patient.html', title='Edit Patient', form=form)

@data_view.route('/yearly')
@login_required
def view_yearly_records():
    company = session.get('company', 'DCP')
    year = session.get('year', date.today().year)
    return render_template('data_view/view_yearly.html', title=f'{year} Records ({company})')

@data_view.route('/api/yearly_search')
@login_required
def api_search_yearly_records():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '')
    company = session.get('company', 'DCP')
    year = session.get('year', date.today().year)

    query = Patient.query.filter_by(company=company, screening_year=year)

    if search_query:
        query = query.filter(
            or_(
                Patient.staff_id.ilike(f'%{search_query}%'),
                Patient.first_name.ilike(f'%{search_query}%'),
                Patient.last_name.ilike(f'%{search_query}%')
            )
        )

    patients = query.order_by(Patient.date_registered.desc()).paginate(page=page, per_page=20)

    return jsonify({
        'patients': [{
            'id': p.id,
            'patient_id': p.patient_id,
            'staff_id': p.staff_id,
            'first_name': p.first_name,
            'last_name': p.last_name,
            'company': p.company,
            'screening_year': p.screening_year
        } for p in patients.items],
        'has_next': patients.has_next,
        'has_prev': patients.has_prev,
        'next_num': patients.next_num,
        'prev_num': patients.prev_num,
        'page': patients.page,
        'pages': patients.pages
    })
