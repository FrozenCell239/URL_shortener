from flask import Flask
from config import Config
from app.extensions import db, bcrypt, limiter

def create_app(config_class = Config):
    # App initialisation
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Flask extensions initialisation
    db.init_app(app)
    bcrypt.init_app(app)
    limiter.init_app(app)

    # Blueprints
    from app.main import main_bp
    app.register_blueprint(main_bp)
    from app.user import user_bp
    app.register_blueprint(user_bp, url_prefix='/u')
    from app.error import error_bp
    app.register_blueprint(error_bp, url_prefix='/error')

    return app