from flask import Blueprint

registration_bp = Blueprint('registration', __name__)

from app.registration import routes