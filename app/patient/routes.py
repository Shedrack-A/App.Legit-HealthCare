from flask import render_template, redirect, url_for, flash, jsonify, session, request
from flask_login import login_required
from app import db
from app.patient import patient
from app.models import Patient
from app.patient.forms import PatientRegistrationForm
from app.utils import log_audit
from datetime import date, datetime, time
from sqlalchemy import func

def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, today.day))

@patient.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    form = PatientRegistrationForm()
    if form.validate_on_submit():
        age = calculate_age(form.date_of_birth.data)
        new_patient = Patient(
            staff_id=form.staff_id.data,
            patient_id=form.patient_id.data,
            first_name=form.first_name.data,
            middle_name=form.middle_name.data,
            last_name=form.last_name.data,
            department=form.department.data,
            gender=form.gender.data,
            date_of_birth=form.date_of_birth.data,
            age=age,
            contact_phone=form.contact_phone.data,
            email_address=form.email_address.data,
            race=form.race.data,
            nationality=form.nationality.data,
            company=session.get('company', 'DCP'),
            screening_year=session.get('year', date.today().year)
        )
        db.session.add(new_patient)
        db.session.commit()
        log_audit('CREATE_PATIENT', f'Patient created: {new_patient.staff_id} ({new_patient.first_name} {new_patient.last_name})')
        flash(f'Patient {form.first_name.data} {form.last_name.data} has been registered successfully!', 'success')
        return redirect(url_for('patient.register'))

    # --- Statistics Calculation ---
    year = session.get('year', date.today().year)
    company = session.get('company', 'DCP')

    today_start = datetime.combine(date.today(), time.min)
    today_end = datetime.combine(date.today(), time.max)

    stats = {
        'total': Patient.query.filter_by(screening_year=year, company=company).count(),
        'today': Patient.query.filter(
            Patient.screening_year == year,
            Patient.company == company,
            Patient.date_registered.between(today_start, today_end)
        ).count(),
        'male': Patient.query.filter_by(screening_year=year, company=company, gender='Male').count(),
        'female': Patient.query.filter_by(screening_year=year, company=company, gender='Female').count(),
        'over_40': Patient.query.filter(
            Patient.screening_year == year,
            Patient.company == company,
            Patient.age >= 40
        ).count(),
        'under_40': Patient.query.filter(
            Patient.screening_year == year,
            Patient.company == company,
            Patient.age < 40
        ).count()
    }

    return render_template('patient/register.html', title='Register Patient', form=form, stats=stats)

@patient.route('/api/search')
@login_required
def search_patient():
    staff_id = request.args.get('staff_id', '', type=str)
    if not staff_id:
        return jsonify({'error': 'Staff ID is required'}), 400

    year = session.get('year', date.today().year)
    company = session.get('company', 'DCP')

    patient = Patient.query.filter_by(staff_id=staff_id, screening_year=year, company=company).first()

    if patient:
        patient_data = {
            'staff_id': patient.staff_id,
            'patient_id': patient.patient_id,
            'first_name': patient.first_name,
            'middle_name': patient.middle_name,
            'last_name': patient.last_name,
            'department': patient.department,
            'gender': patient.gender,
            'date_of_birth': patient.date_of_birth.strftime('%Y-%m-%d'),
            'contact_phone': patient.contact_phone,
            'email_address': patient.email_address,
            'race': patient.race,
            'nationality': patient.nationality,
        }
        return jsonify(patient_data)
    else:
        return jsonify({'error': 'Patient not found'}), 404
