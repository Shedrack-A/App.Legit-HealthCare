from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import current_user, login_required
from app import db
from app.decorators import permission_required
from app.models import TemporaryAccessCode
from datetime import datetime, date

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('landing.html', title='Welcome')

@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', title='Dashboard')

@main.route('/set_filters', methods=['POST'])
def set_filters():
    session['company'] = request.form.get('company', 'DCP', type=str)
    session['year'] = request.form.get('year', date.today().year, type=int)
    # Redirect back to the page the user was on
    return redirect(request.referrer or url_for('main.index'))

@main.route('/sensitive_data')
@login_required
@permission_required('view_sensitive_data')
def sensitive_data():
    return "This is sensitive data."

@main.route('/activate_code', methods=['POST'])
def activate_code():
    code_str = request.form.get('temp_code')
    next_url = request.form.get('next_url') or url_for('main.index')

    if not code_str:
        flash('No code provided.', 'danger')
        return redirect(next_url)

    code = TemporaryAccessCode.query.filter_by(code=code_str).first()

    if not code:
        flash('Invalid temporary access code.', 'danger')
        return redirect(next_url)

    if not code.is_active or code.expiry_time < datetime.utcnow() or (code.is_single_use and code.times_used > 0):
        flash('This code is expired or has already been used.', 'danger')
        return redirect(next_url)

    if code.user_id != current_user.id:
        flash('This code is not assigned to you.', 'danger')
        return redirect(next_url)

    # All checks passed, activate the permission in the session
    if 'temp_permissions' not in session:
        session['temp_permissions'] = {}

    session['temp_permissions'][code.permission.name] = code.expiry_time.isoformat()

    code.times_used += 1
    if code.is_single_use:
        code.is_active = False

    db.session.commit()

    flash(f"Permission '{code.permission.name}' has been temporarily granted.", 'success')
    return redirect(next_url)
