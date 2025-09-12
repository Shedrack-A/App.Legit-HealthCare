from flask import Blueprint

patient = Blueprint('patient', __name__)

from . import routes
