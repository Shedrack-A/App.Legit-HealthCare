from flask import Blueprint

data_view = Blueprint('data_view', __name__)

from . import routes
