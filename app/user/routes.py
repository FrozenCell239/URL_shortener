from flask import render_template, flash, redirect, url_for, request, session
from app.user import user_bp
from app.extensions import db, limiter
from app.models.user import User
from app.models.link import Link, File
from config import AppInfos
from os import remove
from os.path import join, isfile

@user_bp.route('/')
def index(): return redirect(url_for('user.links'))

@user_bp.route('/profile', methods = ['POST', 'GET'])
def profile():
    # Redirecting user if not connected
    if not 'username' in session :
        flash("Vous devez être connecté pour accéder à cette page/fonctionnalité.", 'danger')
        return redirect(url_for('main.login'))

    # Getting user's informations
    found_user = User.query.filter_by(username = session['username']).first()

    # Register form handling
    errors = []
    if request.method == 'POST' :
        # Errors handling
        if request.form['username'] == '' :
            errors.append("Le nom d'utilisateur ne peut pas être vide.")
        if request.form['mail'] == '' :
            errors.append("L'adresse mail ne peut pas être vide.")
        if(
            found_user.getUsername() != request.form['username'] and
            User.query.filter_by(username = request.form['username']).first()
        ):
            errors.append("Un autre compte possède déjà le nom d'utilisateur que vous avez saisi.")
        if(
            found_user.getMail() != request.form['mail'] and
            User.query.filter_by(mail = request.form['mail']).first()
        ):
            errors.append("Un autre compte possède déjà l'adresse mail que vous avez saisie.")

        # New user's informations registering if no error occured
        if errors == [] :
            if found_user.getUsername() != request.form['username'] :
                found_user.setUsername(request.form['username'])
                session['username'] = request.form['username']
            if found_user.getMail() != request.form['mail'] :
                found_user.setMail(request.form['mail'])
            db.session.commit()
            flash("Vos informations ont été modifiées avec succès.", 'success')
            return redirect(url_for('main.index'))

    # Profile page display with errors if some occured
    for error in errors : flash(error, 'danger')
    return render_template(
        'user/profile.html.jinja',
        title = "Mon profil",
        user_infos = {
            'mail' : found_user.getMail(),
            'username' : found_user.getUsername(),
            'created_at' : found_user.getCreatedAt()
        }
    )

@user_bp.route('/password', methods = ['POST', 'GET'])
@limiter.limit(AppInfos.password_limits())
def password():
    # Redirecting user if not connected
    if not 'username' in session :
        flash("Vous devez être connecté pour accéder à cette page/fonctionnalité.", 'danger')
        return redirect(url_for('main.login'))

    # Register form handling
    errors = []
    if request.method == 'POST' :
        # Getting user
        found_user = User.query.filter_by(id = session['user_id']).first()

       # Errors handling
        password_strength_check = User.checkPasswordStrength(request.form['new_password'])
        if not found_user : return redirect(url_for('error.index'))
        if not found_user.checkPassword(request.form['old_password']) :
            errors.append("L'ancien mot de passe saisi est incorrect.")
        if request.form['new_password'] != request.form['new_password_confirm'] :
            errors.append("Les mots de passe ne sont pas identiques.")
        if request.form['new_password'] == '' :
            errors.append("Le nouveau mot de passe ne peut pas être vide.")
        if not password_strength_check['password_ok'] :
            strength_errors = "Le nouveau mot de passe ne respecte pas les conditions de sécurité suivantes. :"
            for criteria, checked in password_strength_check.items() :
                if checked :
                    match criteria :
                        case 'length_error' : strength_errors += '<br>- 8 caractères ou plus.'
                        case 'digit_error' : strength_errors += '<br>- 1 chiffre ou plus.'
                        case 'uppercase_error' : strength_errors += '<br>- 1 lettre minuscule ou plus.'
                        case 'lowercase_error' : strength_errors += '<br>- 1 lettre majuscule ou plus.'
                        case 'symbol_error' : strength_errors += '<br>- 1 caractère spécial ou plus.'
            errors.append(strength_errors)

        # New user's informations registering if no error occured
        if errors == [] :
            found_user.setPassword(request.form['new_password'])
            db.session.commit()
            flash("Votre mot de passe a été modifié avec succès.", 'success')
            return redirect(url_for('main.index'))

    # Profile page display with errors if some occured
    for error in errors : flash(error, 'danger')
    return render_template(
        'user/password.html.jinja',
        title = "Modification mot de passe"
    )

@user_bp.route('/links')
def links():
    # Redirecting user if not connected
    if not 'username' in session :
        flash("Vous devez être connecté pour accéder à cette page/fonctionnalité.", 'danger')
        return redirect(url_for('main.login'))

    # Getting user's links
    found_user = User.query.filter_by(username = session['username']).first()
    user_links = Link.query.filter_by(owner_id = found_user.getID()).order_by(Link.id).all()
    
    # Getting user's links' creation datetime
    user_links_dates = []
    for link in user_links : user_links_dates.append(link.getCreatedAt())

    # User's links page display
    return render_template(
        'user/links.html.jinja',
        domain_name = AppInfos.domain_name(),
        title = "Mes liens",
        links = user_links,
        links_dates = user_links_dates
    )

@user_bp.route('/links/<int:link_id>/toggle')
def toggle_link(link_id : int):
    # Redirecting user if not connected
    if not 'username' in session :
        flash("Vous devez être connecté pour accéder à cette page/fonctionnalité.", 'danger')
        return redirect(url_for('main.login'))

    # Getting the link to toggle
    link = Link.query.filter_by(id = link_id, owner_id = session['user_id']).first()

    # Redirecting to error page if user try to toggle a link they don't own
    if not link : return redirect(url_for('error.index'))

    # Toggling link state
    else:
        link = Link.query.filter_by(id = link_id).first()
        link.toggleState()
        db.session.commit()
        return redirect(url_for('user.links'))

@user_bp.route('/links/<int:link_id>/delete')
def delete_link(link_id : int):
    # Redirecting user if not connected
    if not 'username' in session :
        flash("Vous devez être connecté pour accéder à cette page/fonctionnalité.", 'danger')
        return redirect(url_for('main.login'))

    # Getting the link to delete
    link = Link.query.filter_by(id = link_id, owner_id = session['user_id']).first()

    # Redirecting to error page if user try to delete a link they don't own
    if not link : return redirect(url_for('error.index'))

    # Deleting link from database
    else:
        link = Link.query.filter_by(id = link_id).delete()
        db.session.commit()
        return redirect(url_for('user.links'))

@user_bp.route('/files')
def files():
    # Redirecting user if not connected
    if not 'username' in session :
        flash("Vous devez être connecté pour accéder à cette page/fonctionnalité.", 'danger')
        return redirect(url_for('main.login'))

    # Getting user's files
    found_user = User.query.filter_by(username = session['username']).first()
    user_files = File.query.filter_by(owner_id = found_user.getID()).order_by(File.id).all()

    # Getting user's files' creation datetime
    user_files_dates = []
    for link in user_files : user_files_dates.append(link.getCreatedAt())

    # User's files page display
    return render_template(
        'user/files.html.jinja',
        domain_name = AppInfos.domain_name(),
        title = "Mes fichiers",
        files = user_files,
        files_dates = user_files_dates
    )

@user_bp.route('/files/<int:file_id>/toggle')
def toggle_file(file_id : int):
    # Redirecting user if not connected
    if not 'username' in session :
        flash("Vous devez être connecté pour accéder à cette page/fonctionnalité.", 'danger')
        return redirect(url_for('main.login'))

    # Getting the file to toggle
    file = File.query.filter_by(id = file_id, owner_id = session['user_id']).first()

    # Redirecting to error page if user try to toggle a file they don't own
    if not file : return redirect(url_for('error.index'))

    # Toggling file state
    else:
        file = File.query.filter_by(id = file_id).first()
        file.toggleState()
        db.session.commit()
        return redirect(url_for('user.files'))

@user_bp.route('/files/<int:file_id>/delete')
def delete_file(file_id : int):
    # Redirecting user if not connected
    if not 'username' in session :
        flash("Vous devez être connecté pour accéder à cette page/fonctionnalité.", 'danger')
        return redirect(url_for('main.login'))

    # Getting the file to delete
    file = File.query.filter_by(id = file_id, owner_id = session['user_id']).first()

    # Redirecting to error page if user try to delete a file they don't own
    if not file : return redirect(url_for('error.index'))

    # Deleting file
    else:
        # Deleting from the server
        file_path = join(
            AppInfos.upload_folder(),
            file.getAttachedFileName()
        )
        if isfile(file_path) : remove(file_path)

        # Unregistering from the database
        file = File.query.filter_by(id = file_id).delete()
        db.session.commit()

        # User's files page display
        return redirect(url_for('user.files'))