from flask import Blueprint

consultation = Blueprint('consultation', __name__)

from . import routes
