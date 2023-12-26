from flask import render_template, flash, redirect, url_for, request, session
from app.user import user_bp
from app.extensions import db, bcrypt, limiter
from app.models.user import User
from app.models.link import Link
from config import AppInfos
from os import remove, path

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
    if request.method == 'POST' :
       # Errors handling
        errors = []
        if User.query.filter_by(username = request.form['username']).first():
            errors.append("Un autre compte possède déjà le nom d'utilisateur que vous avez saisi.")
        if User.query.filter_by(mail = request.form['mail']).first():
            errors.append("Un autre compte possède déjà l'adresse mail que vous avez saisie.")

        # New user's informations registering if no error occured
        if errors == [] :
            found_user.username = request.form['username']
            found_user.mail = request.form['mail']
            db.session.commit()
            session['username'] = request.form['username']
            flash("Vos informations ont été modifiées avec succès.", 'success')
            return redirect(url_for('main.index'))

        # Profile page display with errors if some occured
        else:
            for error in errors : flash(error, 'danger')
            return render_template(
            'user/profile.html.jinja',
            title = "Mon profil",
            user_infos = {
                'mail' : found_user.mail,
                'username' : found_user.username
            }
        )

    # Profile page display
    else:
        return render_template(
            'user/profile.html.jinja',
            title = "Mon profil",
            user_infos = {
                'mail' : found_user.mail,
                'username' : found_user.username
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
    if request.method == 'POST' :
        # Getting user
        found_user = User.query.filter_by(id = session['user_id']).first()

       # Errors handling
        errors = []
        if request.form['new_password'] != request.form['new_password_confirm'] :
            errors.append("Les mots de passes ne sont pas identiques.")
        if found_user :
            pw_check = bcrypt.check_password_hash(
                found_user.password,
                request.form['old_password']
            )
        else: pw_check = None
        if not pw_check :
            errors.append("L'ancien mot de passe saisi est incorrect.")
        if not found_user :
            redirect(url_for('error.index'))

        # New user's informations registering if no error occured
        if errors == [] :
            found_user.setPassword(
                bcrypt
                    .generate_password_hash(request.form['new_password'])
                    .decode('utf-8')
            )
            db.session.commit()
            flash("Votre mot de passe a été modifié avec succès.", 'success')
            return redirect(url_for('main.index'))

        # Profile page display with errors if some occured
        else:
            for error in errors : flash(error, 'danger')
            return render_template(
                'user/password.html.jinja',
                title = "Modification mot de passe"
            )

    # Profile page display
    else:
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

    # User's links page display
    found_user = User.query.filter_by(username = session['username']).first()
    user_links = Link.query.filter_by(owner_id = found_user.id, attached_file_name = None).order_by(Link.id).all()
    return render_template(
        'user/links.html.jinja',
        domain_name = AppInfos.domain_name(),
        title = "Mes liens",
        links = user_links
    )

@user_bp.route('/links/<int:link_id>/toggle')
def toggle_link(link_id : int):
    # Redirecting user if not connected
    if not 'username' in session :
        flash("Vous devez être connecté pour accéder à cette page/fonctionnalité.", 'danger')
        return redirect(url_for('main.login'))

    # Getting the link to toggle
    link = Link.query.filter_by(id = link_id, owner_id = session['user_id']).first()

    # Redirecting to error page if user try to toggle a link they don't own or a file
    if not link or not link.original : return redirect(url_for('error.index'))

    # Toggling link state
    else:
        link = Link.query.filter_by(id = link_id).first()
        link.state = not link.state
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

    # Redirecting to error page if user try to delete a link they don't own or a file
    if not link or not link.original : return redirect(url_for('error.index'))

    # Deleting link
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

    # User's files page display
    found_user = User.query.filter_by(username = session['username']).first()
    user_files = Link.query.filter_by(owner_id = found_user.id, original = None).order_by(Link.id).all()
    return render_template(
        'user/files.html.jinja',
        domain_name = AppInfos.domain_name(),
        title = "Mes fichiers",
        files = user_files
    )

@user_bp.route('/files/<int:file_id>/toggle')
def toggle_file(file_id : int):
    # Redirecting user if not connected
    if not 'username' in session :
        flash("Vous devez être connecté pour accéder à cette page/fonctionnalité.", 'danger')
        return redirect(url_for('main.login'))

    # Getting the file to toggle
    file = Link.query.filter_by(id = file_id, owner_id = session['user_id']).first()

    # Redirecting to error page if user try to toggle a file they don't own or a link
    if not file or not file.attached_file_name : return redirect(url_for('error.index'))

    # Toggling file state
    else:
        file = Link.query.filter_by(id = file_id).first()
        file.state = not file.state
        db.session.commit()
        return redirect(url_for('user.files'))

@user_bp.route('/files/<int:file_id>/delete')
def delete_file(file_id : int):
    # Redirecting user if not connected
    if not 'username' in session :
        flash("Vous devez être connecté pour accéder à cette page/fonctionnalité.", 'danger')
        return redirect(url_for('main.login'))

    # Getting the file to delete
    file = Link.query.filter_by(id = file_id, owner_id = session['user_id']).first()

    # Redirecting to error page if user try to delete a file they don't own or a link
    if not file or not file.attached_file_name : return redirect(url_for('error.index'))

    # Deleting file
    else:
        # Deleting from the server
        file_path = path.join(
            AppInfos.upload_folder(),
            file.attached_file_name
        )
        if path.exists(file_path) : remove(file_path)

        # Unregistering from the database
        file = Link.query.filter_by(id = file_id).delete()
        db.session.commit()

        # User's files page display
        return redirect(url_for('user.files'))