from flask import flash, redirect, url_for, session
from functools import wraps

def login_required(func):
    """
    When applied to a route as a decorator, redirects the user to login page if they're not logged in.
    """

    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not 'username' in session :
            flash("Vous devez être connecté pour accéder à cette page/fonctionnalité.", 'danger')
            return redirect(url_for('main.login'))

        return func(*args, **kwargs)

    return decorated_view