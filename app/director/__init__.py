from flask import Blueprint

director = Blueprint('director', __name__, template_folder='templates')

from . import routes
