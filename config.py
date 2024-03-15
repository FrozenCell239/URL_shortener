from os import urandom, environ
from datetime import timedelta

DOMAIN_NAME = environ.get('DOMAIN_NAME')

class AppInfos :
    """
    Contains somes informations about the app that the app often needs to work properly and might be modified fastly later when needed if so.\n
    All theses informations are returned by some static methods as they musn't be modified somewhere else in the programs.\n
    So you must not create an instance of this class.
    """

    def __init__(self) -> None :
        """
        You must NOT create an instance of this class since it only contains static methods that return some app informations.
        """

        raise Exception(
            "You must NOT create an instance of AppInfos class since it only contains static methods that return some app informations."
        )

    @staticmethod
    def link_lengths(key : str) -> int :
        """
        Expected parameter : 'min' or 'max' or 'default'.\n
        Returns either the "min", "max", or "default" link length.
        """

        if key == 'default' : return 6
        elif key == 'min' : return 5
        elif key == 'max' : return 10
        else : raise ValueError("Invalid key.")

    @staticmethod
    def web_app_name() -> str : return "Easy Link"

    @staticmethod
    def domain_name() -> str : return f'http://{DOMAIN_NAME}/'

    @staticmethod
    def allowed_extensions() -> list[str] :
        """
        Returns the list of all file formats allowed for upload.
        """

        return [
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
    
    @staticmethod
    def upload_folder() -> str : return 'app/static/uploads'

    @staticmethod
    def max_upload_size(requested_type : type = int) -> (int | str) :
        """
        Returns the maximum size for uploaded files.\n
        It can be returned either... :
            - As a string with the unit symbol.
            - As an integer which represent the maximum size allowed in bytes.\n
        Pass the str type as an argument if you need the string return.\n
        You can pass the int type as an argument if you need the integer return, but you actually don't need to since it's the default returned type.
        """

        if requested_type == int : return 16 * 1024 * 1024
        elif requested_type == str : return '16 Mo'
        else : raise TypeError("Invalid requested type.")

    @staticmethod
    def password_limits() -> str : return '200/day;100/hour;20/minute'

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

    # Security config
    SECRET_KEY = environ.get('SECRET_KEY')\
        or urandom(32).hex()
    PERMANENT_SESSION_LIFETIME = timedelta(minutes = 10)

    # Database config
    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # File upload feature config
    UPLOAD_FOLDER = AppInfos.upload_folder()
    UPLOAD_EXTENSIONS = AppInfos.allowed_extensions()
    MAX_CONTENT_LENGTH = AppInfos.max_upload_size()

    # Mail service config
    MAIL_SERVER = environ.get('MAIL_SERVER')
    MAIL_PORT = environ.get('MAIL_PORT')
    MAIL_DEFAULT_SENDER = environ.get('MAIL_DEFAULT_SENDER')
    MAIL_USE_TLS = environ.get('MAIL_USE_TLS')
    MAIL_USE_SSL = environ.get('MAIL_USE_SSL')
    MAIL_USERNAME =  environ.get('MAIL_USERNAME')
    MAIL_PASSWORD =  environ.get('MAIL_PASSWORD')