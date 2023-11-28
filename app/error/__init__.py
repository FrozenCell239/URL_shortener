from flask import Blueprint

error_bp = Blueprint('error', __name__)

from app.error import routes