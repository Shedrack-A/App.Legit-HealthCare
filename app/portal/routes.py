from flask import render_template, redirect, url_for, jsonify, request, flash, session
from app.portal import portal
from flask import abort
from app.models import Patient, PatientAccount
from .forms import PatientSignUpForm, PatientLoginForm, PatientChangePasswordForm
from app import db
from app.utils import log_audit, generate_patient_pdf
from app.decorators import patient_account_login_required

@portal.route('/start')
def start():
    return render_template('portal/start.html', title='Welcome Patient')

@portal.route('/api/patient_search')
def patient_search():
    staff_id = request.args.get('staff_id', '')
    if not staff_id:
        return jsonify({'error': 'Staff ID is required'}), 400

    # Find the most recent patient record for this staff_id
    patient = Patient.query.filter_by(staff_id=staff_id).order_by(Patient.screening_year.desc()).first()

    if patient:
        patient_data = {
            'staff_id': patient.staff_id,
            'first_name': patient.first_name,
            'last_name': patient.last_name,
            'middle_name': patient.middle_name or '',
            'date_of_birth': patient.date_of_birth.strftime('%Y-%m-%d'),
            'email': patient.email_address or '',
            'gender': patient.gender,
            'department': patient.department,
            'phone_number': patient.contact_phone
        }
        return jsonify(patient_data)
    else:
        return jsonify({'error': 'No record found for this Staff ID.'}), 404

@portal.route('/login', methods=['GET', 'POST'])
def login():
    form = PatientLoginForm()
    if form.validate_on_submit():
        account = PatientAccount.query.filter_by(staff_id=form.staff_id.data).first()
        if account and account.verify_password(form.password.data):
            session['patient_account_id'] = account.id
            log_audit('PATIENT_LOGIN', f'Patient logged in with Staff ID: {account.staff_id}')
            flash('You have been successfully logged in.', 'success')
            return redirect(url_for('portal.dashboard'))
        else:
            flash('Invalid Staff ID or password.', 'danger')
    return render_template('portal/login.html', title='Patient Login', form=form)

@portal.route('/signup', methods=['GET', 'POST'])
def signup():
    form = PatientSignUpForm()
    if form.validate_on_submit():
        # Check if account already exists
        existing_account = PatientAccount.query.filter(
            (PatientAccount.staff_id == form.staff_id.data) |
            (PatientAccount.email == form.email.data)
        ).first()

        if existing_account:
            flash('An account with this Staff ID or Email already exists. Please log in.', 'warning')
            return redirect(url_for('portal.login'))

        new_account = PatientAccount(
            staff_id=form.staff_id.data,
            email=form.email.data,
            password=form.password.data
        )
        db.session.add(new_account)
        db.session.commit()

        # Also update the patient's bio-data with any corrections
        patient_record = Patient.query.filter_by(staff_id=form.staff_id.data).order_by(Patient.screening_year.desc()).first()
        if patient_record:
            patient_record.first_name = form.first_name.data
            patient_record.last_name = form.last_name.data
            patient_record.middle_name = form.middle_name.data
            patient_record.gender = form.gender.data
            patient_record.contact_phone = form.phone_number.data
            patient_record.email_address = form.email.data
            db.session.commit()

        log_audit('PATIENT_SIGNUP', f'Patient account created for Staff ID: {new_account.staff_id}')
        flash('Your account has been created successfully! You can now log in.', 'success')
        return redirect(url_for('portal.login'))

    return render_template('portal/signup.html', title='Patient Sign Up', form=form)

@portal.route('/dashboard')
@patient_account_login_required
def dashboard():
    account = PatientAccount.query.get_or_404(session['patient_account_id'])
    # Find all patient bio-data records associated with this account's staff_id
    patient_records = Patient.query.filter_by(staff_id=account.staff_id).order_by(Patient.screening_year.desc()).all()

    # Use the most recent record for display, but pass all for year selection
    latest_patient_record = patient_records[0] if patient_records else None

    return render_template('portal/dashboard.html', title='Patient Dashboard',
                           account=account,
                           latest_patient_record=latest_patient_record,
                           patient_records=patient_records)

@portal.route('/logout')
def logout():
    session.pop('patient_account_id', None)
    flash('You have been logged out from the patient portal.', 'info')
    return redirect(url_for('main.index'))

@portal.route('/settings', methods=['GET', 'POST'])
@patient_account_login_required
def settings():
    account = PatientAccount.query.get_or_404(session['patient_account_id'])
    form = PatientChangePasswordForm()
    if form.validate_on_submit():
        account.password = form.password.data
        db.session.commit()
        log_audit('PATIENT_CHANGE_PASSWORD', f'Patient changed their password. Staff ID: {account.staff_id}')
        flash('Your password has been updated.', 'success')
        return redirect(url_for('portal.dashboard'))
    return render_template('portal/settings.html', title='Account Settings', form=form)

@portal.route('/download_report', methods=['POST'])
@patient_account_login_required
def download_report():
    patient_id = request.form.get('patient_id')
    if not patient_id:
        abort(400, 'Patient ID not provided.')

    # Security Check: Ensure the requested patient record belongs to the logged-in patient account
    account = PatientAccount.query.get_or_404(session['patient_account_id'])
    patient = Patient.query.get_or_404(patient_id)

    if account.staff_id != patient.staff_id:
        log_audit('PATIENT_UNAUTHORIZED_REPORT_ACCESS', f'Patient account {account.id} tried to access report for patient {patient.id}')
        abort(403) # Forbidden

    # Eager load all data for the report
    patient_with_data = Patient.query.options(
        db.joinedload('*')
    ).get(patient_id)

    log_audit('PATIENT_DOWNLOAD_REPORT', f'Patient {account.staff_id} downloaded report for year {patient.screening_year}')
    return generate_patient_pdf(patient_with_data)

@portal.route('/email_report', methods=['POST'])
@patient_account_login_required
def email_report():
    patient_id = request.form.get('patient_id')
    if not patient_id:
        flash('Please select a report to email.', 'danger')
        return redirect(url_for('portal.dashboard'))

    account = PatientAccount.query.get_or_404(session['patient_account_id'])
    patient = Patient.query.get_or_404(patient_id)

    if account.staff_id != patient.staff_id:
        log_audit('PATIENT_UNAUTHORIZED_REPORT_ACCESS', f'Patient account {account.id} tried to email report for patient {patient.id}')
        abort(403)

    if not patient.email_address:
        flash('You do not have a registered email address. Please add one in your settings.', 'danger')
        return redirect(url_for('portal.dashboard'))

    # Generate PDF in memory
    pdf_bytes = generate_patient_pdf_bytes(patient)
    pdf_filename = f'Medical_Report_{patient.screening_year}.pdf'

    # Construct dynamic sender name and subject
    sender_name_prefix = db.session.query(Setting).filter_by(key='MAIL_SENDER_NAME').first()
    sender_name_prefix = sender_name_prefix.value if sender_name_prefix else 'Legit HealthCare'

    sender_name = f"{sender_name_prefix} [{patient.company}-OBAJANA]"
    subject = f"MEDICAL REPORT: {patient.screening_year} Annual Medical Screening for SUNU Health Enrolees at {patient.company} Obajana"

    # Send email
    send_email(
        to=patient.email_address,
        subject=subject,
        template='email/report_notification',
        patient=patient,
        attachments=[(pdf_filename, 'application/pdf', pdf_bytes)],
        sender=(sender_name, current_app.config['MAIL_DEFAULT_SENDER'])
    )

    log_audit('PATIENT_EMAIL_REPORT', f'Patient {account.staff_id} emailed report for year {patient.screening_year}')
    flash(f'Your {patient.screening_year} medical report has been sent to your registered email address.', 'success')
    return redirect(url_for('portal.dashboard'))
