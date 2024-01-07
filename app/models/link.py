from app.extensions import db
from random import choice
from config import AppInfos
from sqlalchemy.sql import func
from validators import url

class AbstractShortcut():
    id = db.Column(db.Integer, primary_key = True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    short = db.Column(db.String(100), nullable = False)
    clicks = db.Column(db.Integer, nullable = False)
    state = db.Column(db.Boolean, nullable = False)
    created_at = db.Column(
        db.DateTime(timezone = True),
        nullable = False,
        server_default = func.current_timestamp()
    )

    def __init__(
        self,
        owner_id : int,
        short_length : int = AppInfos.link_lengths('default')
    ) -> None :
        if short_length < AppInfos.link_lengths('min') :
            raise ValueError(
                f'Too short length. Minimum is {AppInfos.link_lengths('min')}.'
            )
        if short_length > AppInfos.link_lengths('max') :
            raise ValueError(
                f'Too long length. Maximum is {AppInfos.link_lengths('max')}.'
            )
        self.owner_id = owner_id
        self.short = self.__shorten(short_length)
        self.clicks = 0
        self.state = True

    # Short link creation
    def __shorten(self, length : int) -> str :
        characters = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        short = ''
        for _ in range(length):
            short += choice(characters)
        return short
    
    # ID getter
    def getID(self) -> int : return self.id

    # Owner ID getter
    def getOwnerID(self) -> int : return self.owner_id
    
    # Short getter
    def getShort(self) -> str : return self.short

    # Clicks getter/incrementer
    def getClicks(self) -> int : return self.clicks
    def incrementClicks(self) -> None : self.clicks += 1

    # State getter/toggler
    def getState(self) -> bool : return self.state
    def toggleState(self) -> None : self.state = not self.state

    # Creation date getter
    def getCreatedAt(self) -> dict[str, str] :
        return {
            'date' : str(self.created_at)[:10],
            'time' : str(self.created_at)[10:-13],
            'timezone' : str(self.created_at)[-6:]
        }

class Link(db.Model, AbstractShortcut):
    original = db.Column(db.String(255), nullable = False)

    def __init__(
        self,
        owner_id : int,
        original : str,
        short_length : int = AppInfos.link_lengths('default')
    ) -> None :
        AbstractShortcut.__init__(self, owner_id, short_length)
        self.setOriginal(original)

    def __repr__(self) -> str : return f'<Link "{self.short}">'

    # Original link getter/setter
    def getOriginal(self) -> str : return self.original
    def setOriginal(self, new_original : str) -> None :
        # Adding "https://" to links starting with "www." in order to avoid a redirect bug
        if new_original.startswith("www.") : new_original = "https://" + new_original
        self.original = new_original
        
    # Original link's validity checker
    @staticmethod
    def checkOriginal(original : str) -> bool :
        return True if url(original) else False

class File(db.Model, AbstractShortcut):
    attached_file_name = db.Column(db.String(255), nullable = False)

    def __init__(
        self,
        owner_id : int,
        attached_file_name : str,
        short_length : int = AppInfos.link_lengths('default'),
    ) -> None :
        AbstractShortcut.__init__(self, owner_id, short_length)
        self.attached_file_name = attached_file_name

    def __repr__(self) -> str : return f'<File "{self.short}">'

    # Attached file name getter
    def getAttachedFileName(self) -> str : return self.attached_file_name

    # File format checker
    @staticmethod
    def isFileFormatAllowed(filename : str) -> bool :
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in AppInfos.allowed_extensions()