from flask import\
    render_template,\
    redirect,\
    url_for,\
    flash,\
    send_from_directory,\
    request,\
    session
from app.main import main_bp
from app.extensions import db, bcrypt
from app.models.user import User
from app.models.link import Link
from config import AppInfos
from werkzeug.utils import secure_filename
from datetime import datetime
from shutil import move
import os

@main_bp.route('/', methods = ['POST', 'GET'])
@main_bp.route('/<string:requested_link>')
def index(requested_link : str = None):
    # Redirecting short links to original ones
    if requested_link :
        # Getting the link from database
        link = Link.query.filter_by(short = requested_link).first()

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

    # Main page display if no short link is requested
    elif request.method == 'POST' :
        # Redirect to login page if no user is connected
        if not 'username' in session : 
            flash("Vous devez être connecté(e) pour accéder à cette page/fonctionnalité.", 'danger')
            return redirect(url_for('main.login'))
        
        # File/link handling
        else:
            # Errors handling
            errors = []

            # Link shortening
            if(
                not request.form.getlist('file_or_link') and
                request.form['original_url']
            ):
                # Checking original link's validity
                if(
                    request.form['original_url'].startswith("http://") ==
                    request.form['original_url'].startswith("https://") ==
                    request.form['original_url'].startswith("www.") ==
                    False
                ): errors.append("Le lien saisi n'est pas un lien valide.")

                # Creating the new short link if no error occured
                if errors == [] :
                    new_link = Link(
                        #//shortened_length = 8,
                        owner_id = session['user_id'],
                        original = request.form['original_url']
                    )
                    db.session.add(new_link)
                    db.session.commit()
                    flash(
                        f"""Raccourci créé avec succès !&nbsp;<a href="{ url_for('user.links') }" >Tout voir</a>""",
                        'success'
                    )

            # File upload
            elif(
                request.form.getlist('file_or_link') and
                'to_upload' in request.files and
                request.files['to_upload'].filename != ''
            ):
                # Getting new upload file
                new_upload = request.files['to_upload']
                new_filename = datetime.now().strftime("[%d-%m-%Y_%H-%M-%S]_") + secure_filename(new_upload.filename)

                # Checking if file's format is allowed
                if(
                    '.' in new_upload.filename and
                    not new_upload.filename.rsplit('.', 1)[1].lower() in AppInfos.allowed_extensions()
                ): errors.append("Ce format de fichier n'est pas autorisé.")

                # Saving first the file in a temp folder
                if not os.path.exists(AppInfos.tmp_folder()) : os.makedirs(AppInfos.tmp_folder())
                new_upload.save(os.path.join(AppInfos.tmp_folder(), new_filename))

                # Checking if file size limit is exceeded
                if os.stat(os.path.join(AppInfos.tmp_folder(), new_filename)).st_size > AppInfos.max_upload_size() :
                    errors.append(f"Fichier trop volumineux. Taille max supportée : {AppInfos.max_upload_size(str)}.")
                    os.remove(os.path.join(AppInfos.tmp_folder(), new_filename))
                
                # File upload if no error occured
                if errors == [] :
                    # Creating the uploads directory if it doesn't exist
                    if not os.path.exists(AppInfos.upload_folder()) :
                        os.makedirs(AppInfos.upload_folder())

                    # Saving the file on the server
                    move(
                        os.path.join(AppInfos.tmp_folder(), new_filename),
                        os.path.join(AppInfos.upload_folder(), new_filename)
                    )

                    # Registering the file in the database
                    new_link = Link(
                        #//shortened_length = 8,
                        owner_id = session['user_id'],
                        attached_file_name = new_filename
                    )
                    db.session.add(new_link)
                    db.session.commit()

                    # Success message
                    flash(
                        f"""Votre fichier a bien été enregistré !&nbsp;<a href="{ url_for('user.files') }" >Tout voir</a>""",
                        'success'
                    )

        # Main page display with errors if some occured
        for error in errors : flash(error, 'danger')
        return render_template('index.html.jinja', title = AppInfos.web_app_name())
    # Main page display
    else: return render_template('index.html.jinja', title = AppInfos.web_app_name())

@main_bp.route('/dl/<string:requested_file>')
def download(requested_file : str = None):
    # Main page display if no file link is passed
    if not requested_file : return redirect(url_for('main.index'))
    
    # File download
    else :
        # Getting the file name from database
        file = Link.query.filter_by(short = requested_file).first()

        # Redirecting to the original file if the short one exists and is valid
        if file and file.state == True :
            file.clicks += 1
            db.session.commit()
            return send_from_directory(
                '../' + AppInfos.upload_folder(),
                file.attached_file_name,
                as_attachment = True
            )

        # Redirecting to an error page if the short file is not active
        elif file and file.state == False :
            return redirect(url_for('error.index', error_type = 'DISABLED'))

        # Redirecting to an error page if the short file doesn't exist
        elif not file :
            return redirect(url_for('error.index', error_type = 'DELETED'))

@main_bp.route('/register', methods = ['POST', 'GET'])
def register():
    # Forbid an already connected user to access this route
    if 'username' in session : return redirect(url_for('main.index'))

    # Register page display
    if request.method != 'POST' : return render_template('register.html.jinja', title = "S'inscrire")

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
        
        # Register page display with errors if some occured
        else:
            for error in errors : flash(error, 'danger')
            return render_template('register.html.jinja', title = "Création de compte")

@main_bp.route('/login', methods = ['POST', 'GET'])
def login():
    # Forbid an already connected user to access this route
    if 'username' in session : return redirect(url_for('main.index'))

    # Login page display
    if request.method != 'POST': return render_template('login.html.jinja', title = "Connexion")

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

        # Login page display if the user doesn't exist in the database
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