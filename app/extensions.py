# SQLAlchemy for database
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

# Bcrypt for passwords hashing
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()

# Limiter for bruteforce attacks preventing
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
limiter = Limiter(
    get_remote_address,

    # Memcached options
    storage_uri = 'memcached://localhost:11211',
    storage_options = {}

    # Redis options
    #storage_uri = 'redis://localhost:6379',
    #storage_options = {'socket_connect_timeout': 30},
    #strategy = 'fixed-window' #// or 'moving-window'
)

# Flask-WTF for CSRF tokens
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect()

# Flask-Mail for mailing
from flask_mail import Mail
mailer = Mail()