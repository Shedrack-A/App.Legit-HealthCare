from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.reports import reports
from app.models import Patient
from app.decorators import permission_required
from app.utils import generate_patient_pdf, generate_patient_pdf_bytes, send_email

@reports.route('/', methods=['GET', 'POST'])
@login_required
@permission_required('generate_patient_report')
def index():
    """
    Search page to find a patient to generate a report for.
    """
    if request.method == 'POST':
        search_term = request.form.get('search_term', '').strip()
        company = request.form.get('company', 'DCP')
        year = request.form.get('year', '2025')

        if not search_term:
            flash('Please enter a Staff ID to search.', 'warning')
            return redirect(url_for('reports.index'))

        patients = Patient.query.filter_by(company=company, screening_year=year)\
                                .filter(Patient.staff_id.ilike(f'%{search_term}%')).all()

        return render_template('reports/index.html', title='Search Results', patients=patients, search_term=search_term)

    return render_template('reports/index.html', title='Generate Patient Report')


@reports.route('/download/<int:patient_id>')
@login_required
@permission_required('generate_patient_report')
def download_report(patient_id):
    """
    Generates and downloads a PDF report for a single patient.
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

    return generate_patient_pdf(patient)

@reports.route('/email/<int:patient_id>')
@login_required
@permission_required('generate_patient_report') # Re-using the same permission
def email_report(patient_id):
    """
    Generates a PDF report and emails it to the patient.
    """
    patient = Patient.query.get_or_404(patient_id)

    if not patient.email_address:
        flash('This patient does not have an email address on file.', 'warning')
        return redirect(url_for('reports.index'))

    # Generate PDF in memory
    pdf_bytes = generate_patient_pdf_bytes(patient)

    # Prepare attachment
    filename = f'report_{patient.staff_id}_{patient.screening_year}.pdf'
    attachments = [(filename, 'application/pdf', pdf_bytes)]

    # Send email
    send_email(
        to=patient.email_address,
        subject=f'Your {patient.screening_year} Medical Report from Legit HealthCare Services',
        template='email/report_notification',
        attachments=attachments,
        patient=patient
    )

    flash(f'Report has been successfully emailed to {patient.email_address}.', 'success')
    return redirect(url_for('reports.index'))
