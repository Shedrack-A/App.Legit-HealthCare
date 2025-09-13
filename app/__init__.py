from flask import Flask, render_template, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from config import config
from datetime import date

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login' # Redirect to login page if user is not authenticated
bcrypt = Bcrypt()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)

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

    # Set default session filters for company and year
    @app.before_request
    def before_request_hook():
        if 'company' not in session:
            session['company'] = 'DCP'
        if 'year' not in session:
            session['year'] = date.today().year

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

    return app
