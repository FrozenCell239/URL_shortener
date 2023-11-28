import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')\
        or os.urandom(32).hex()
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=10)