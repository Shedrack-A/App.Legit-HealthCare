from flask import Blueprint, render_template, session, request, redirect, url_for
from flask_login import current_user
from datetime import date

main = Blueprint('main', __name__)

@main.before_app_request
def before_request():
    if 'company' not in session:
        session['company'] = 'DCP'
    if 'year' not in session:
        session['year'] = date.today().year

@main.route('/')
@main.route('/index')
def index():
    if current_user.is_authenticated:
        return render_template('dashboard.html', title='Dashboard')
    return render_template('landing.html', title='Welcome')

@main.route('/set_filters', methods=['POST'])
def set_filters():
    session['company'] = request.form.get('company', 'DCP', type=str)
    session['year'] = request.form.get('year', date.today().year, type=int)
    # Redirect back to the page the user was on
    return redirect(request.referrer or url_for('main.index'))
