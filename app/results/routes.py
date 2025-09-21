from flask import render_template, request, redirect, url_for, flash, abort, jsonify, session
from flask_login import login_required
from app import db
from app.results import results
from app.models import Patient, FullBloodCount, KidneyFunctionTest, LipidProfile, LiverFunctionTest, ECG, Spirometry, Audiometry
from .forms import FullBloodCountForm, KidneyFunctionTestForm, LipidProfileForm, LiverFunctionTestForm, ECGForm, SpirometryForm, AudiometryForm

@results.route('/')
@login_required
def index():
    # This page will list all available tests to enter results for.
    tests = [
        {'name': 'Full Blood Count', 'endpoint': 'results.full_blood_count'},
        {'name': 'Kidney Function Test', 'endpoint': 'results.kidney_function_test'},
        {'name': 'Lipid Profile', 'endpoint': 'results.lipid_profile'},
        {'name': 'Liver Function Test', 'endpoint': 'results.liver_function_test'},
        {'name': 'ECG', 'endpoint': 'results.ecg'},
        {'name': 'Spirometry', 'endpoint': 'results.spirometry'},
        {'name': 'Audiometry', 'endpoint': 'results.audiometry'},
    ]
    return render_template('results/index.html', title='Select Test', tests=tests)

@results.route('/full_blood_count', methods=['GET'])
@login_required
def full_blood_count():
    return render_template('results/full_blood_count_search.html', title='Search Patient')

@results.route('/full_blood_count/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def full_blood_count_form(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    fbc_record = FullBloodCount.query.filter_by(patient_id=patient.id).first()

    form = FullBloodCountForm(obj=fbc_record)

    if form.validate_on_submit():
        if fbc_record:
            form.populate_obj(fbc_record)
            flash('Full Blood Count results updated successfully!', 'success')
        else:
            fbc_record = FullBloodCount(patient_id=patient.id)
            form.populate_obj(fbc_record)
            db.session.add(fbc_record)
            flash('Full Blood Count results saved successfully!', 'success')

        db.session.commit()
        return redirect(url_for('results.full_blood_count'))

    return render_template('results/full_blood_count_form.html', title='Full Blood Count', form=form, patient=patient)

@results.route('/kidney_function_test', methods=['GET'])
@login_required
def kidney_function_test():
    return render_template('results/kidney_function_test_search.html', title='Search Patient')

@results.route('/kidney_function_test/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def kidney_function_test_form(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    kft_record = KidneyFunctionTest.query.filter_by(patient_id=patient.id).first()

    form = KidneyFunctionTestForm(obj=kft_record)

    if form.validate_on_submit():
        hco3 = form.k.data + form.na.data - form.cl.data - 16
        if kft_record:
            form.populate_obj(kft_record)
            kft_record.hco3 = hco3
            flash('Kidney Function Test results updated successfully!', 'success')
        else:
            kft_record = KidneyFunctionTest(patient_id=patient.id, hco3=hco3)
            form.populate_obj(kft_record)
            db.session.add(kft_record)
            flash('Kidney Function Test results saved successfully!', 'success')

        db.session.commit()
        return redirect(url_for('results.kidney_function_test'))

    return render_template('results/kidney_function_test_form.html', title='Kidney Function Test', form=form, patient=patient)

@results.route('/lipid_profile', methods=['GET'])
@login_required
def lipid_profile():
    return render_template('results/lipid_profile_search.html', title='Search Patient')

@results.route('/lipid_profile/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def lipid_profile_form(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    lp_record = LipidProfile.query.filter_by(patient_id=patient.id).first()

    form = LipidProfileForm(obj=lp_record)

    if form.validate_on_submit():
        tcho = form.tcho.data
        tg = form.tg.data
        hdl = tcho * 0.35
        ldl = tcho + (tg / 5) + hdl # Using user's specified formula

        if lp_record:
            form.populate_obj(lp_record)
            lp_record.hdl = hdl
            lp_record.ldl = ldl
            flash('Lipid Profile results updated successfully!', 'success')
        else:
            lp_record = LipidProfile(patient_id=patient.id, hdl=hdl, ldl=ldl)
            form.populate_obj(lp_record)
            db.session.add(lp_record)
            flash('Lipid Profile results saved successfully!', 'success')

        db.session.commit()
        return redirect(url_for('results.lipid_profile'))

    return render_template('results/lipid_profile_form.html', title='Lipid Profile', form=form, patient=patient)

@results.route('/liver_function_test', methods=['GET'])
@login_required
def liver_function_test():
    return render_template('results/liver_function_test_search.html', title='Search Patient')

@results.route('/liver_function_test/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def liver_function_test_form(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    lft_record = LiverFunctionTest.query.filter_by(patient_id=patient.id).first()

    form = LiverFunctionTestForm(obj=lft_record)

    if form.validate_on_submit():
        if lft_record:
            form.populate_obj(lft_record)
            flash('Liver Function Test results updated successfully!', 'success')
        else:
            lft_record = LiverFunctionTest(patient_id=patient.id)
            form.populate_obj(lft_record)
            db.session.add(lft_record)
            flash('Liver Function Test results saved successfully!', 'success')

        db.session.commit()
        return redirect(url_for('results.liver_function_test'))

    return render_template('results/liver_function_test_form.html', title='Liver Function Test', form=form, patient=patient)

# --- ECG Routes ---
@results.route('/ecg', methods=['GET'])
@login_required
def ecg():
    return render_template('results/ecg_search.html', title='Search Patient')

@results.route('/ecg/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def ecg_form(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    ecg_record = ECG.query.filter_by(patient_id=patient.id).first()
    form = ECGForm(obj=ecg_record)
    if form.validate_on_submit():
        if ecg_record:
            form.populate_obj(ecg_record)
            flash('ECG results updated successfully!', 'success')
        else:
            ecg_record = ECG(patient_id=patient.id)
            form.populate_obj(ecg_record)
            db.session.add(ecg_record)
            flash('ECG results saved successfully!', 'success')
        db.session.commit()
        return redirect(url_for('results.ecg'))
    return render_template('results/ecg_form.html', title='ECG', form=form, patient=patient)

# --- Spirometry Routes ---
@results.route('/spirometry', methods=['GET'])
@login_required
def spirometry():
    return render_template('results/spirometry_search.html', title='Search Patient')

@results.route('/spirometry/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def spirometry_form(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    sp_record = Spirometry.query.filter_by(patient_id=patient.id).first()
    form = SpirometryForm(obj=sp_record)
    if form.validate_on_submit():
        if sp_record:
            form.populate_obj(sp_record)
            flash('Spirometry results updated successfully!', 'success')
        else:
            sp_record = Spirometry(patient_id=patient.id)
            form.populate_obj(sp_record)
            db.session.add(sp_record)
            flash('Spirometry results saved successfully!', 'success')
        db.session.commit()
        return redirect(url_for('results.spirometry'))
    return render_template('results/spirometry_form.html', title='Spirometry', form=form, patient=patient)

# --- Audiometry Routes ---
@results.route('/audiometry', methods=['GET'])
@login_required
def audiometry():
    return render_template('results/audiometry_search.html', title='Search Patient')

@results.route('/audiometry/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def audiometry_form(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    au_record = Audiometry.query.filter_by(patient_id=patient.id).first()
    form = AudiometryForm(obj=au_record)
    if form.validate_on_submit():
        if au_record:
            form.populate_obj(au_record)
            flash('Audiometry results updated successfully!', 'success')
        else:
            au_record = Audiometry(patient_id=patient.id)
            form.populate_obj(au_record)
            db.session.add(au_record)
            flash('Audiometry results saved successfully!', 'success')
        db.session.commit()
        return redirect(url_for('results.audiometry'))
    return render_template('results/audiometry_form.html', title='Audiometry', form=form, patient=patient)

# --- API Routes ---
@results.route('/api/search_patient')
@login_required
def api_search_patient():
    search_term = request.args.get('q', '')
    company = session.get('company', 'DCP')
    year = session.get('year', datetime.now().year)

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
