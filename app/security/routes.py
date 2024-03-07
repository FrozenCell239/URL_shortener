from app.extensions import limiter
from app.security import security_bp
from app.models.user import User
from app.utils import logout_required, login_required
from config import AppInfos
from flask import render_template, redirect, url_for, flash, request, session

@security_bp.route('/login', methods = ['POST', 'GET'])
@limiter.limit(AppInfos.password_limits())
@logout_required
def login():
    # Login form handling
    if request.method == 'POST' :
        # Looking for the user into the database
        found_user = User.query.filter_by(username = request.form['username']).first()
        if found_user : pw_check = found_user.checkPassword(request.form['password'])

        # Login page display if the user doesn't exist in the database
        if not found_user or not pw_check :
            flash("Nom d'utilisateur et/ou mot de passe incorrect(s).", 'danger')
        
        # Log-in the user if found in the database
        else:
            # Getting user's informations
            session.permanent = True
            session['user_id'] = found_user.id
            session['username'] = found_user.username

            # Main page display
            flash("Connexion réussie !", 'success')
            return redirect(url_for('main.index'))

    # Login page display
    return render_template('login.html.jinja', title = "Connexion")

@security_bp.route('/logout')
@login_required
def logout():
    session.clear()
    flash("Vous avez été déconnecté(e) avec succès.", 'info')
    return redirect(url_for('security.login'))