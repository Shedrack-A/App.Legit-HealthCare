from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_required
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

from sqlalchemy import or_

@data_view.route('/yearly')
@login_required
def view_yearly_records():
    page = request.args.get('page', 1, type=int)
    company = session.get('company', 'DCP')
    year = session.get('year', date.today().year)
    query = request.args.get('q', '')

    patients_query = Patient.query.filter_by(company=company, screening_year=year)

    if query:
        patients_query = patients_query.filter(
            or_(
                Patient.staff_id.ilike(f'%{query}%'),
                Patient.patient_id.ilike(f'%{query}%'),
                Patient.first_name.ilike(f'%{query}%'),
                Patient.last_name.ilike(f'%{query}%')
            )
        )

    patients = patients_query.order_by(Patient.date_registered.desc()).paginate(page=page, per_page=20)

    return render_template('data_view/view_yearly.html', title=f'{year} Records ({company})', patients=patients)
