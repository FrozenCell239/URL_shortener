from app.extensions import db, bcrypt
from sqlalchemy.sql import func
from re import search

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(42), nullable = False, unique = True)
    password = db.Column(db.String(255), nullable = False)
    mail = db.Column(db.String(42), nullable = False)
    created_at = db.Column(
        db.DateTime(timezone = True),
        nullable = False,
        server_default = func.current_timestamp()
    )

    def __init__(self, username : str, mail : str) -> None :
        self.setUsername(username)
        self.setMail(mail)

    def __repr__(self) -> str :
        return f'<User "{self.username}">'

    # ID getter
    def getID(self) -> int : return self.id

    # Username getter/setter
    def getUsername(self) -> str : return self.username
    def setUsername(self, new_username : str) -> None :
        if new_username == '' : raise ValueError('Username cannot be empty.')
        self.username = new_username

    # Password checker/setter
    def checkPassword(self, password_to_check : str) -> bool :
        return bcrypt.check_password_hash(self.password, password_to_check)
    def setPassword(self, new_password) -> None :
        if new_password == '' : raise ValueError('Password cannot be empty.')
        self.password = bcrypt.generate_password_hash(new_password).decode('utf-8')

    # Mail getter/setter
    def getMail(self) -> str : return self.mail
    def setMail(self, new_mail : str) -> None :
        if new_mail == '' : raise ValueError('Mail cannot be empty.')
        self.mail = new_mail

    # Creation date getter
    def getCreatedAt(self) -> dict[str, str] :
        return {
            'date' : str(self.created_at)[:10],
            'time' : str(self.created_at)[10:-13],
            'timezone' : str(self.created_at)[-6:]
        }

    # Password strength checker
    @staticmethod
    def checkPasswordStrength(password : str) -> dict[str, bool] :
        """
        Verify the strength of password.\n
        Returns a dictionnary indicating the wrong criteria(s).\n
        A password is considered strong if it has... :
            - 8 characters or more.
            - 1 digit or more.
            - 1 symbol or more.
            - 1 uppercase letter or more.
            - 1 lowercase letter or more.
        """

        # Calculating the length
        length_error = len(password) < 8

        # Searching for digits
        digit_error = search(r"\d", password) is None

        # Searching for uppercase
        uppercase_error = search(r"[A-Z]", password) is None

        # Searching for lowercase
        lowercase_error = search(r"[a-z]", password) is None

        # Searching for symbols
        symbol_error = search(r"\W", password) is None

        # Overall result
        password_ok = not (length_error or digit_error or uppercase_error or lowercase_error or symbol_error)

        return {
            'password_ok' : password_ok,
            'length_error' : length_error,
            'digit_error' : digit_error,
            'uppercase_error' : uppercase_error,
            'lowercase_error' : lowercase_error,
            'symbol_error' : symbol_error,
        }