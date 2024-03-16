from os import urandom, environ
from datetime import timedelta

class Config :
    """
    Contains the app's configuration.\n
    You must not create an instance of this class because of its purpose.
    """

    def __init__(self) -> None :
        """
        You must NOT create an instance of this class since it contains app's configuration.
        """

        raise Exception(
            "You must NOT create an instance of Config class since it contains app's configuration."
        )

    # Security configuration
    SECRET_KEY : str = environ.get('SECRET_KEY')\
        or urandom(32).hex()
    PERMANENT_SESSION_LIFETIME : timedelta = timedelta(minutes = 10)
    PASSWORD_LIMITS : str = environ.get('PASSWORD_LIMITS')

    # Database configuration
    SQLALCHEMY_DATABASE_URI : str = environ.get('DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS : bool = False

    # Link shortening feature configuration
    DEFAULT_LINK_LENGTH : int = 6
    MIN_LINK_LENGTH : int = 5
    MAX_LINK_LENGTH : int = 10

    # File upload feature configuration
    UPLOAD_FOLDER : str = 'app/static/uploads'
    MAX_CONTENT_LENGTH : int = 16 * 1024 * 1024
    MAX_UPLOAD_SIZE : str = "16 Mo"
    UPLOAD_EXTENSIONS : list[str] = [
        # Allowed document file formats
        'xml', 'json', 'csv', 'toml', 'yaml',
        'txt', 'md', 'pdf', 'rtf', 'epub',
        'odt', 'odp', 'ods', 'odg',
        'doc', 'ppt', 'xls',
        'docx', 'pptx', 'xlsx', 'pub',
    
        # Allowed image file formats
        'png', 'jpg', 'jpeg', 'webp', 'gif',
    
        # Allowed music file formats
        'mp3', 'ogg', 'wav',
    
        # Allowed video file formats
        'mp4', 'avi',
    
        # Allowed compressed file formats
        'zip', 'rar', 'tar', 'gz', '7z'
    ]

    # Mail service configuration
    MAIL_SERVER : str = environ.get('MAIL_SERVER')
    MAIL_PORT : int = environ.get('MAIL_PORT')
    MAIL_DEFAULT_SENDER : str = environ.get('MAIL_DEFAULT_SENDER')
    MAIL_USE_TLS : bool = environ.get('MAIL_USE_TLS')
    MAIL_USE_SSL : bool = environ.get('MAIL_USE_SSL')
    MAIL_USERNAME : str =  environ.get('MAIL_USERNAME')
    MAIL_PASSWORD : str =  environ.get('MAIL_PASSWORD')

    # Running environnement configuration
    WEB_APP_NAME : str = environ.get('WEB_APP_NAME')
    DOMAIN_NAME : str = environ.get('DOMAIN_NAME') + "/"