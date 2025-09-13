from flask import render_template, request, redirect, url_for, flash, session
from app.portal import portal
from app.models import Patient
from .forms import PatientLoginForm
from app.decorators import patient_login_required

@portal.route('/login', methods=['GET', 'POST'])
def login():
    form = PatientLoginForm()
    if form.validate_on_submit():
        patient = Patient.query.filter_by(
            patient_id=form.patient_id.data,
            date_of_birth=form.date_of_birth.data
        ).first()

        if patient:
            session['patient_id'] = patient.id
            flash('You have been successfully logged in.', 'success')
            return redirect(url_for('portal.dashboard'))
        else:
            flash('Invalid Patient ID or Date of Birth.', 'danger')

    return render_template('portal/login.html', title='Patient Login', form=form)

@portal.route('/dashboard')
@patient_login_required
def dashboard():
    patient = Patient.query.get_or_404(session['patient_id'])
    return render_template('portal/dashboard.html', title='Patient Dashboard', patient=patient)

@portal.route('/logout')
def logout():
    session.pop('patient_id', None)
    flash('You have been logged out from the patient portal.', 'info')
    return redirect(url_for('main.index'))
