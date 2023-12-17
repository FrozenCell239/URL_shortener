from flask import render_template, redirect, url_for, flash, request, session
from app.main import main_bp
from app.extensions import db, bcrypt
from app.models.user import User
from app.models.link import Link
from config import AppInfos

@main_bp.route('/', methods = ['POST', 'GET'])
@main_bp.route('/<requested_link>')
def index(requested_link : str = None):
    # Redirecting short links to original ones
    if requested_link :
        # Getting the link from database
        link = Link.query.filter_by(
            short = requested_link
        ).first()

        # Redirecting to the original link if the short one exists and is valid
        if link and link.state == True :
            link.clicks += 1
            db.session.commit()
            return redirect(link.original, code = 301)

        # Redirecting to an error page if the short link is not active
        elif link and link.state == False :
            return redirect(url_for('error.index', error_type = 'DISABLED'))

        # Redirecting to an error page if the short link doesn't exist
        elif not link :
            return redirect(url_for('error.index', error_type = 'DELETED'))

    # Page display if no short link
    elif request.method == 'POST' :
        # Redirect to login page if no user is connected
        if not 'username' in session : 
            flash("Vous devez être connecté pour accéder à cette page/fonctionnalité.", 'danger')
            return redirect(url_for('main.login'))
        
        # Link shortening
        else:
            # Checking original link's validity
            if(
                request.form['original_url'].startswith("http://") ==
                request.form['original_url'].startswith("https://") ==
                request.form['original_url'].startswith("www.") ==
                False
            ):
                flash("Le lien saisi n'est pas un lien valide.", 'danger')

            # Creating the new short link if the original one is valid
            else:
                new_link = Link(
                    #//shortened_length = 8,
                    owner_id = session['user_id'],
                    original = request.form['original_url']
                )
                db.session.add(new_link)
                db.session.commit()
                flash(f"""Raccourci créé avec succès ! <a href="{ url_for('user.links') }" >Tout voir</a>""", 'success')

        return render_template('index.html.jinja', title = AppInfos.web_app_name())
    # Page display
    else: return render_template('index.html.jinja', title = AppInfos.web_app_name())

@main_bp.route('/register', methods = ['POST', 'GET'])
def register():
    # Forbid an already connected user to access this route
    if 'username' in session :
        return redirect(url_for('main.index'))

    # Page display
    if request.method != 'POST':
        return render_template('register.html.jinja', title = "S'inscrire")

    # Register form handling
    else:
        # Errors handling
        errors = []
        if request.form['password'] != request.form['password_confirm'] :
            errors.append("Les mots de passes ne sont pas identiques.")
        if User.query.filter_by(username = request.form['username']).first():
            errors.append("Un autre compte possède déjà le nom d'utilisateur que vous avez saisi.")
        if User.query.filter_by(mail = request.form['mail']).first():
            errors.append("Un autre compte possède déjà l'adresse mail que vous avez saisie.")
        
        # New user registering if no error occured
        if errors == [] :
            user = User(
                request.form['username'],
                request.form['mail']
            )
            user.setPassword(
                bcrypt
                    .generate_password_hash(request.form['password'])
                    .decode('utf-8')
            )
            db.session.add(user)
            db.session.commit()
            flash("Votre compte a été créé avec succès ! Vous pouvez vous connecter dès à présent.", 'success')
            return redirect(url_for('main.login'))
        
        # Page display with errors if some occured
        else:
            for error in errors : flash(error, 'danger')
            return render_template('register.html.jinja', title = "Création de compte")

@main_bp.route('/login', methods = ['POST', 'GET'])
def login():
    # Forbid an already connected user to access this route
    if 'username' in session :
        return redirect(url_for('main.index'))

    # Page display
    if request.method != 'POST':
        return render_template('login.html.jinja', title = "Connexion")

    # Login form handling
    else:
        # Looking for the user into the database
        found_user = User.query.filter_by(
            username = request.form['username']
        ).first()
        if found_user :
            pw_check = bcrypt.check_password_hash(
                found_user.password,
                request.form['password']
            )
        else: pw_check = None

        # Page display if the user doesn't exist in the database
        if not found_user or not pw_check :
            flash("Nom d'utilisateur et/ou mot de passe incorrect(s).", 'danger')
            return render_template('login.html.jinja', title = "Connexion")
        
        # Connecting the user if found in the database
        else:
            session.permanent = True
            session['user_id'] = found_user.id
            session['username'] = found_user.username
            session['mail'] = found_user.mail
            flash("Connexion réussie !", 'success')
            return redirect(url_for('main.index'))

@main_bp.route('/logout')
def logout():
    session.clear()
    flash("Vous avez été déconnecté(e) avec succès.", 'info')
    return redirect(url_for('main.login'))