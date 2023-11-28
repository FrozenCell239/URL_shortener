from app.extensions import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(42))
    password = db.Column(db.String(255))
    mail = db.Column(db.String(42))

    def __init__(self, username : str, mail : str):
        self.username = username
        self.mail = mail

    def __repr__(self) -> str:
        return f'<User "{self.username}">'

    def setPassword(self, password):
        self.password = password