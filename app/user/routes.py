from app.extensions import db, limiter
from app.models.link import Link
from app.models.user import User
from app.user import user_bp
from app.utils import login_required
from config import Config
from flask import render_template, flash, redirect, url_for, request, session
from os import remove
from os.path import join, isfile

@user_bp.route('/')
def index(): return redirect(url_for('user.links'))

@user_bp.route('/profile', methods = ['POST', 'GET'])
@login_required
def profile():
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
            found_user.username != request.form['username'] and
            User.query.filter_by(username = request.form['username']).first()
        ):
            errors.append("Un autre compte possède déjà le nom d'utilisateur que vous avez saisi.")
        if(
            found_user.mail != request.form['mail'] and
            User.query.filter_by(mail = request.form['mail']).first()
        ):
            errors.append("Un autre compte possède déjà l'adresse mail que vous avez saisie.")

        # New user's informations registering if no error occured
        if errors == [] :
            if found_user.username != request.form['username'] :
                found_user.username = request.form['username']
                session['username'] = request.form['username']
            if found_user.mail != request.form['mail'] :
                found_user.mail = request.form['mail']
            db.session.commit()
            flash("Vos informations ont été modifiées avec succès.", 'success')
            return redirect(url_for('user.profile'))

    # Profile page display with errors if some occured
    for error in errors : flash(error, 'danger')
    return render_template(
        'user/profile.html.jinja',
        title = "Mon profil",
        user_infos = {
            'mail' : found_user.mail,
            'username' : found_user.username,
            'created_at' : found_user.getCreatedAt()
        }
    )

@user_bp.route('/password', methods = ['POST', 'GET'])
@limiter.limit(Config.PASSWORD_LIMITS)
@login_required
def password():
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
            strength_errors = "Le nouveau mot de passe ne respecte pas la/les condition(s) de sécurité suivante(s) : "
            for criteria, checked in password_strength_check.items() :
                if checked :
                    match criteria :
                        case 'length_error' : strength_errors += "8 caractères ou plus, "
                        case 'digit_error' : strength_errors += "1 chiffre ou plus, "
                        case 'uppercase_error' : strength_errors += "1 lettre majuscule ou plus, "
                        case 'lowercase_error' : strength_errors += "1 lettre minuscule ou plus, "
                        case 'symbol_error' : strength_errors += "1 caractère spécial ou plus, "
            errors.append(strength_errors[:-2] + ".")

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
@login_required
def links():
    # Getting user's links
    user_links = (Link.query
        .filter_by(
            link_type = 'link',
            owner_id = session['user_id']
        )
        .order_by(Link.id)
        .all()
    )
    user_links_created_at = []
    user_links_last_visit_at = []
    for link in user_links :
        user_links_created_at.append(link.getCreatedAt())
        user_links_last_visit_at.append(link.getLastVisitAt())

    # User's links page display
    return render_template(
        'user/dashboard.html.jinja',
        domain_name = Config.DOMAIN_NAME,
        title = "Mes liens",
        type = 'links',
        links = user_links,
        links_created_at = user_links_created_at,
        links_last_visit_at = user_links_last_visit_at
    )

@user_bp.route('/links/<int:link_id>/toggle')
@login_required
def toggle_link(link_id : int):
    # Getting the link to toggle
    link = Link.query.filter_by(id = link_id, owner_id = session['user_id']).first()

    # Redirecting to error page if user try to toggle a link they don't own
    if not link : return redirect(url_for('error.index'))

    # Toggling link state
    else:
        link = Link.query.filter_by(id = link_id).first()
        link.state = not link.state
        db.session.commit()

    # User's links page display
    return redirect(url_for('user.links', page = request.args.get('back_to', 1, int)))

@user_bp.route('/links/<int:link_id>/delete')
@login_required
def delete_link(link_id : int):
    # Getting the link to delete
    link = Link.query.filter_by(id = link_id, owner_id = session['user_id']).first()

    # Redirecting to error page if user try to delete a link they don't own
    if not link : return redirect(url_for('error.index'))

    # Deleting link from database
    else:
        link = Link.query.filter_by(id = link_id).delete()
        db.session.commit()

    # User's links page display
    return redirect(url_for('user.links', page = request.args.get('back_to', 1, int)))

@user_bp.route('/files')
@login_required
def files():
    # Getting user's files
    user_files = (Link.query
        .filter_by(
            link_type = 'file',
            owner_id = session['user_id']
        )
        .order_by(Link.id)
        .all()
    )
    user_files_created_at = []
    user_files_last_visit_at = []
    for file in user_files :
        user_files_created_at.append(file.getCreatedAt())
        user_files_last_visit_at.append(file.getLastVisitAt())

    # User's files page display
    return render_template(
        'user/dashboard.html.jinja',
        domain_name = Config.DOMAIN_NAME,
        title = "Mes fichiers",
        type = 'files',
        links = user_files,
        links_created_at = user_files_created_at,
        links_last_visit_at = user_files_last_visit_at
    )

@user_bp.route('/files/<int:file_id>/toggle')
@login_required
def toggle_file(file_id : int):
    # Getting the file to toggle
    file = Link.query.filter_by(id = file_id, owner_id = session['user_id']).first()

    # Redirecting to error page if user try to toggle a file they don't own
    if not file : return redirect(url_for('error.index'))

    # Toggling file state
    else:
        file = Link.query.filter_by(id = file_id).first()
        file.state = not file.state
        db.session.commit()

    # User's files page display
    return redirect(url_for('user.files', page = request.args.get('back_to', 1, int)))

@user_bp.route('/files/<int:file_id>/delete')
@login_required
def delete_file(file_id : int):
    # Getting the file to delete
    file = Link.query.filter_by(id = file_id, owner_id = session['user_id']).first()

    # Redirecting to error page if user try to delete a file they don't own
    if not file : return redirect(url_for('error.index'))

    # Deleting file
    else:
        # Deleting from the server
        file_path = join(
            Config.UPLOAD_FOLDER,
            file.original
        )
        if isfile(file_path) : remove(file_path)

        # Unregistering from the database
        file = Link.query.filter_by(id = file_id).delete()
        db.session.commit()

    # User's files page display
    return redirect(url_for('user.files', page = request.args.get('back_to', 1, int)))