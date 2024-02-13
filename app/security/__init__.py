from flask import Blueprint

security_bp = Blueprint('security', __name__)

from app.security import routes