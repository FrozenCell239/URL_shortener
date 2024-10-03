from datetime import timedelta
from os import urandom, getenv

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
    SECRET_KEY : str = getenv('SECRET_KEY')\
        or urandom(32).hex()
    PERMANENT_SESSION_LIFETIME : timedelta = timedelta(minutes = 10)
    PASSWORD_LIMITS : str = getenv('PASSWORD_LIMITS')

    # Database configuration
    SQLALCHEMY_DATABASE_URI : str = getenv('DATABASE_URI')
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
    MAIL_SERVER : str = getenv('MAIL_SERVER')
    MAIL_PORT : int = getenv('MAIL_PORT')
    MAIL_DEFAULT_SENDER : str = getenv('MAIL_DEFAULT_SENDER')
    MAIL_USE_TLS : bool = True if getenv('MAIL_USE_TLS') == 'enabled' else False
    MAIL_USE_SSL : bool = True if getenv('MAIL_USE_SSL') == 'enabled' else False
    MAIL_USERNAME : str =  getenv('MAIL_USERNAME')
    MAIL_PASSWORD : str =  getenv('MAIL_PASSWORD')

    # Running environnement configuration
    WEB_APP_NAME : str = getenv('WEB_APP_NAME')
    DOMAIN_NAME : str = getenv('DOMAIN_NAME') + '/'