from app.extensions import db
from random import choice
from config import AppInfos

class Link(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    original = db.Column(db.String(255), nullable = True)
    short = db.Column(db.String(100), nullable = False)
    clicks = db.Column(db.Integer, nullable = False)
    state = db.Column(db.Boolean, nullable = False)
    attached_file_name = db.Column(db.String(255), nullable = True)
    
    def __init__(
        self, owner_id : int,
        shortened_length : int = AppInfos.link_lengths('default'),
        original : str = None,
        attached_file_name : str = None
    ):
        if shortened_length < AppInfos.link_lengths('min') :
            raise ValueError(
                f'Too short length. Minimum is {AppInfos.link_lengths('min')}.'
            )
        if shortened_length > AppInfos.link_lengths('max') :
            raise ValueError(
                f'Too long length. Maximum is {AppInfos.link_lengths('max')}.'
            )
        self.owner_id = owner_id
        self.short = self.shorten(shortened_length)
        self.original = original
        self.attached_file_name = attached_file_name
        self.clicks = 0
        self.state = True
        

    def __repr__(self) -> str :
        return f'<Link "{self.short}">'
    
    def shorten(self, length) -> str :
        characters = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        short = ""
        for _ in range(length):
            short += choice(characters)
        return short