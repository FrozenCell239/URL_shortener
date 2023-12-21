from flask import render_template, flash, redirect, url_for, request, session
from app.user import user_bp
from app.extensions import db
from app.models.user import User
from app.models.link import Link
from config import AppInfos
import os

@user_bp.route('/')
def index(): return redirect(url_for('user.links'))

@user_bp.route('/profile')
def profile():
    if 'username' in session :
        found_user = User.query.filter_by(username = session['username']).first()
        #if request.method != 'POST' :
        #    return render_template('user/index.html.jinja', title = "Mes infos")
        #else:
        #    session['mail'] = request.form['mail']
        #    found_user.mail = session['mail']
        #    db.session.commit()
        #    flash("Votre adresse mail a été modifiée avec succès.", 'success')
        return render_template(
            'user/profile.html.jinja',
            title = "Mes liens",
            username = session['username'],
            mail = found_user.mail
        )
    else:
        flash("Vous devez être connecté pour accéder à cette page/fonctionnalité.", 'danger')
        return redirect(url_for('main.login'))

@user_bp.route('/links')
def links():
    # Redirecting user if not connected
    if not 'username' in session :
        flash("Vous devez être connecté pour accéder à cette page/fonctionnalité.", 'danger')
        return redirect(url_for('main.login'))

    # User's links page display
    else :
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
    else:
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
    # Getting the file to delete
    file = Link.query.filter_by(id = file_id, owner_id = session['user_id']).first()

    # Redirecting to error page if user try to delete a file they don't own or a link
    if not file or not file.attached_file_name : return redirect(url_for('error.index'))

    # Deleting file
    else:
        # Deleting from the server
        file_path = os.path.join(
            AppInfos.upload_folder(),
            file.attached_file_name
        )
        if os.path.exists(file_path) : os.remove(file_path)

        # Unregistering from the database
        file = Link.query.filter_by(id = file_id).delete()
        db.session.commit()

        return redirect(url_for('user.files'))