from app.extensions import mailer
from config import Config
from datetime import datetime, timedelta, timezone
from flask import flash, redirect, url_for, render_template, session
from flask_mail import Message
from functools import wraps
from jwt import encode, decode

# Decorators
def login_required(route):
    """
    When applied to a route as a decorator, redirects the user to login page if they're not logged in.
    """

    @wraps(route)
    def decorated_route(*args, **kwargs):
        if not 'username' in session :
            flash("Vous devez être connecté pour accéder à cette page/fonctionnalité.", 'danger')
            return redirect(url_for('security.login'))

        return route(*args, **kwargs)

    return decorated_route

def logout_required(route):
    """
    When applied to a route as a decorator, redirects the user to index page if they're already logged in.
    """

    @wraps(route)
    def decorated_route(*args, **kwargs):
        if 'username' in session : return redirect(url_for('main.index'))
        return route(*args, **kwargs)

    return decorated_route

# Microservices
def sendMail(
    to : str,    
    subject : str,
    template_path : str,
    infos : dict[str, str]
) -> None :
    """
    Performs basic mail sending tasks.
    """

    mailer.send(
        Message(
            subject = subject,
            recipients = [to],
            html = render_template(
                template_path,
                domain_name = Config.DOMAIN_NAME,
                infos = infos
            )
        )
    )

class JWT :
    """
    This class is used to perform any tasks related to JSON Web Tokens (JWT).
    """

    payload : dict[str, str] = {}

    @staticmethod
    def generate(payload : dict = {}, validity_time : float = 3) -> str :
        """
        Generates a JSON Web Token, no matter the purpose.\n
        Default validity time is set to 3 hours, but can be overridden it if needed.
        """

        if validity_time <= 0 :
            raise ValueError("Validity time must be strictly greater than zero.")
        if payload == {} :
            raise ValueError("Payload must not be empty.")
        now = datetime.now(tz = timezone.utc)
        payload['iat'] = now
        payload['exp'] = now + timedelta(hours = validity_time)
        return encode(payload, Config.SECRET_KEY, algorithm='HS256')

    def __init__(
        self,
        token : str = None
    ) -> None :
        """
        Gets a passed token in order to automatically performs some tasks on it.\n
        These includes token's expiration and validity/integrity checking and decoding.
        """

        if not token : raise ValueError("Token can't be empty or null.")
        self.payload = decode(token, Config.SECRET_KEY, algorithms=["HS256"])

    def getPayload(self) -> dict[str, str] :
        """
        Returns the content (payload) of the JSON Web Token.
        """

        return self.payload