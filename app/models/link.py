from app.extensions import db
import random

class Link(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    original = db.Column(db.String(255))
    short = db.Column(db.String(100))
    clicks = db.Column(db.Integer)
    state = db.Column(db.Boolean)
    attached_file_name = db.Column(db.String(255))
    
    def __init__(
        self, owner_id : int,
        shortened_length : int = 6,
        original : str = None,
        attached_file_name : str = None
    ):
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
            short += random.choice(characters)
        return short