from flask import flash, redirect, url_for, session
from functools import wraps

def login_required(route):
    """
    When applied to a route as a decorator, redirects the user to login page if they're not logged in.
    """

    @wraps(route)
    def decorated_route(*args, **kwargs):
        if not 'username' in session :
            flash("Vous devez être connecté pour accéder à cette page/fonctionnalité.", 'danger')
            return redirect(url_for('main.login'))

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