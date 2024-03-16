from app.extensions import db
from random import choice
from config import Config
from sqlalchemy.sql import func
from validators import url

class Link(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    link_type = db.Column(db.String(4), nullable = False)
    short = db.Column(db.String(100), nullable = False)
    original = db.Column(db.String(255), nullable = False)
    clicks = db.Column(db.Integer, nullable = False)
    state = db.Column(db.Boolean, nullable = False)
    last_visit_at = db.Column(
        db.DateTime(timezone = True),
        nullable = False,
        server_default = func.current_timestamp()
    )
    created_at = db.Column(
        db.DateTime(timezone = True),
        nullable = False,
        server_default = func.current_timestamp()
    )

    def __init__(
        self,
        owner_id : int,
        link_type : str,
        original : str,
        short_length : int = Config.DEFAULT_LINK_LENGTH
    ) -> None :
        if short_length < Config.MIN_LINK_LENGTH :
            raise ValueError(
                f'Too short length. Minimum is {Config.MIN_LINK_LENGTH}.'
            )
        if short_length > Config.MAX_LINK_LENGTH :
            raise ValueError(
                f'Too long length. Maximum is {Config.MAX_LINK_LENGTH}.'
            )
        if original is None :
            raise ValueError('Original cannot be empty.')
        if link_type != 'file' and link_type != 'link' :
            raise ValueError('Link type must be "link" or "file".')
        self.owner_id = owner_id
        self.link_type = link_type
        self.clicks = 0
        self.state = True
        self.short = self.__shorten(short_length)
        if original.startswith("www.") : original = "https://" + original
        self.original = original

    def __repr__(self) -> str : return f'<Link "{self.short}">'

    # Short link creation
    def __shorten(self, length : int) -> str :
        characters = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        short = ''
        for _ in range(length):
            short += choice(characters)
        return short

    # Creation date getter
    def getCreatedAt(self) -> dict[str, str] :
        return {
            'date' : str(self.created_at)[:10],
            'time' : str(self.created_at)[10:-13],
            'timezone' : str(self.created_at)[-6:]
        }

    # Last visit date getter
    def getLastVisitAt(self) -> dict[str, str] :
        return {
            'date' : str(self.last_visit_at)[:10],
            'time' : str(self.last_visit_at)[10:-13],
            'timezone' : str(self.last_visit_at)[-6:]
        }

    # File format checker
    @staticmethod
    def isFileFormatAllowed(filename : str) -> bool :
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in Config.UPLOAD_EXTENSIONS

    # Original link's validity checker
    @staticmethod
    def checkOriginal(original : str) -> bool :
        return True if url(original) else False