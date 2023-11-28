from flask import render_template, flash, redirect, url_for, request, session
from app.user import user_bp
from app.extensions import db
from app.models.user import User
from app.models.link import Link

@user_bp.route('/')
def index():
    if 'username' in session :
        found_user = User.query.filter_by(username = session['username']).first()
        user_links = Link.query.filter_by(owner_id = found_user.id).order_by(Link.id).all()
        return render_template(
            'user/index.html.jinja',
            title = "Mes infos",
            links = user_links
        )
    else:
        flash("Vous devez être connecté pour accéder à cette page/fonctionnalité.", 'error')
        return redirect(url_for('main.login'))

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
            title = "Mes infos",
            username = session['username'],
            mail = found_user.mail #//if found_user.mail else None
        )
    else:
        flash("Vous devez être connecté pour accéder à cette page/fonctionnalité.", 'error')
        return redirect(url_for('main.login'))

@user_bp.route('/toggle/<int:link_id>')
def toggle_link(link_id : int):
    # Getting the link to toggle
    link = Link.query.filter_by(id = link_id, owner_id = session['user_id']).first()

    # Redirecting to error page if a link is trying to get toggled by someone else than its owner
    if not link : return redirect(url_for('error.index'))

    # Toggling link state
    else:
        link = Link.query.filter_by(id = link_id).first()
        link.state = not link.state
        db.session.commit()
        return redirect(url_for('user.index'))