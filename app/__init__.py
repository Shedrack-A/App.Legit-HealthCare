from flask import Flask, render_template, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_socketio import SocketIO
from config import config
from datetime import date

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login' # Redirect to login page if user is not authenticated
bcrypt = Bcrypt()
mail = Mail()
socketio = SocketIO()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    socketio.init_app(app)

    # Register blueprints
    # I will create and register blueprints for different parts of the app
    # (e.g., auth, main, api)

    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from app.patient import patient as patient_blueprint
    app.register_blueprint(patient_blueprint, url_prefix='/patient')

    from app.consultation import consultation as consultation_blueprint
    app.register_blueprint(consultation_blueprint, url_prefix='/consultation')

    from app.results import results as results_blueprint
    app.register_blueprint(results_blueprint, url_prefix='/results')

    from app.data_view import data_view as data_view_blueprint
    app.register_blueprint(data_view_blueprint, url_prefix='/view')

    from app.admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')

    from app.portal import portal as portal_blueprint
    app.register_blueprint(portal_blueprint, url_prefix='/portal')

    from app.director import director as director_blueprint
    app.register_blueprint(director_blueprint, url_prefix='/director')

    from app.reports import reports as reports_blueprint
    app.register_blueprint(reports_blueprint, url_prefix='/reports')

    from app.account import account as account_blueprint
    app.register_blueprint(account_blueprint, url_prefix='/account')

    from app.messaging import messaging as messaging_blueprint
    app.register_blueprint(messaging_blueprint, url_prefix='/messaging')

    # Set default session filters for company and year
    @app.before_request
    def before_request_hook():
        if 'company' not in session:
            session['company'] = 'DCP'
        if 'year' not in session:
            session['year'] = date.today().year

    # Load email settings from DB, overriding environment variables if they exist in the DB.
    with app.app_context():
        from .models import Setting
        from sqlalchemy.exc import OperationalError
        try:
            # Set static Gmail config
            app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
            app.config['MAIL_PORT'] = 587
            app.config['MAIL_USE_TLS'] = True

            # Load dynamic settings from DB
            settings = {s.key: s.value for s in Setting.query.all()}
            app.config['MAIL_USERNAME'] = settings.get('MAIL_USERNAME')
            app.config['MAIL_PASSWORD'] = settings.get('MAIL_PASSWORD')
            app.config['MAIL_SENDER_NAME'] = settings.get('MAIL_SENDER_NAME')
            app.config['MAIL_DEFAULT_SENDER'] = settings.get('MAIL_USERNAME') # Sender email is the username

        except OperationalError:
            # This can happen if the db is not yet initialized.
            # It's safe to ignore in that case.
            pass

    # Error Handlers
    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return render_template('errors/500.html'), 500

    @app.context_processor
    def inject_branding():
        from .models import Setting
        try:
            settings = {s.key: s.value for s in Setting.query.all()}
            return dict(
                light_logo_url=settings.get('light_logo_url'),
                dark_logo_url=settings.get('dark_logo_url'),
                favicon_url=settings.get('favicon_url'),
                hospital_name=settings.get('hospital_name', 'Legit HealthCare'),
                organization_name=settings.get('organization_name', 'LHC')
            )
        except Exception:
            # Return defaults if DB is not ready
            return dict(
                hospital_name='Legit HealthCare',
                organization_name='LHC'
            )

    return app
