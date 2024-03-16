from app.extensions import db
from app.main import main_bp
from app.models.link import Link
from app.models.user import User
from config import Config
from datetime import datetime, timezone
from os import makedirs
from os.path import join, isdir, isfile
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename as sf
from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    send_from_directory,
    request,
    session
)

@main_bp.route('/', methods = ['POST', 'GET'])
@main_bp.route('/<string:requested_link>')
def index(requested_link : str = None):
    # Redirecting short links to original ones
    if requested_link :
        # Getting the link from database
        link = Link.query.filter_by(short = requested_link).first()

        # Redirecting to the original link if the short one exists and is not disabled
        if link and link.link_type == 'link' and link.state == True :
            link.clicks += 1
            link.last_visit_at = datetime.now(tz = timezone.utc)
            db.session.commit()
            return redirect(link.original, code = 301)

        # Redirecting to an error page if the short link is not active or doesn't exist
        elif link and not link.state : error_type = 'DISABLED'
        elif link and link.link_type != 'link' : error_type = None
        elif not link : error_type = 'DELETED'
        return redirect(url_for('error.index', error_type = error_type))

    # Main features handling if no short link is requested
    errors = []
    if request.method == 'POST' :
        # Redirect to login page if no user is connected
        if not 'username' in session : 
            flash("Vous devez être connecté(e) pour accéder à cette page/fonctionnalité.", 'danger')
            return redirect(url_for('security.login'))

        # Link shortening
        if(
            not request.form.getlist('file_or_link') and
            request.form['original_url']
        ):
            # Extracting the original URL
            original_url = request.form['original_url']

            # Checking original link's validity
            if not Link.checkOriginal(original_url) :
                errors.append("Le lien saisi n'est pas un lien valide.")

            # Creating the new short link if no error occured
            if errors == [] :
                # Registering the link in the database
                new_link = Link(
                    owner_id = session['user_id'],
                    original = original_url,
                    link_type = 'link'
                )
                db.session.add(new_link)
                db.session.commit()

                # Success message
                flash(
                    f"""
                    Raccourci créé avec succès !
                    <a
                        href="#"
                        id="new-link"
                        onclick="toClipboard('{Config.DOMAIN_NAME + new_link.short}')"
                    >
                        Copier
                    </a>
                    """,
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
            new_filename = datetime.now().strftime("[%d-%m-%Y_%H-%M-%S]_") + sf(new_upload.filename)

            # Checking if file's format is allowed
            if not Link.isFileFormatAllowed(new_upload.filename) :
                errors.append("Ce format de fichier n'est pas autorisé.")

            # File upload if no error occured
            if errors == [] :
                # Creating the uploads directory if it doesn't exist
                if not isdir(Config.UPLOAD_FOLDER) : makedirs(Config.UPLOAD_FOLDER)

                # Saving the file on the server
                new_upload.save(join(Config.UPLOAD_FOLDER, new_filename))

                # Registering the file in the database
                new_file_link = Link(
                    owner_id = session['user_id'],
                    original = new_filename,
                    link_type = 'file'
                )
                db.session.add(new_file_link)
                db.session.commit()

                # Success message
                flash(
                    f"""
                    Votre fichier a bien été enregistré !
                    <a
                        href="#"
                        id="new-link"
                        onclick="toClipboard('{Config.DOMAIN_NAME}dl/{new_file_link.short}')"
                    >
                        Copier le lien
                    </a>
                    """,
                    'success'
                )

    # Remind user to verify its mail address if it's still not verified
    if(
        'user_id' in session and not
        (User.query.filter_by(id = session['user_id']).first()).is_verified
    ) :
        flash(
            f"""
            Veuillez vérifier l'adresse mail de votre compte dès que possible.
            <a
                href="{ url_for('registration.resend_verification') }"
            >
                Renvoyer le lien
            </a>
            """,
            'warning'
        )

    # Main page display with errors if some occured
    for error in errors : flash(error, 'danger')
    return render_template('index.html.jinja', title = Config.WEB_APP_NAME)

@main_bp.route('/dl/<string:requested_file>')
def download(requested_file : str = None):
    # Main page display if no file link is passed
    if not requested_file : return redirect(url_for('main.index'))
    
    # Getting the file name from database
    file = Link.query.filter_by(short = requested_file).first()

    # Sending the file if it exists and is not disabled
    if file and file.link_type == 'file' and file.state :
        # Checking if the file still exists on the server
        if not isfile(f'{Config.UPLOAD_FOLDER}/{file.original}') :
            return redirect(url_for('error.index', error_type = 'FILE_NOT_FOUND'))

        # Sending the file to the user
        file.clicks += 1
        db.session.commit()
        return send_from_directory(
            '../' + Config.UPLOAD_FOLDER,
            file.original,
            as_attachment = True
        )

    # Redirecting to an error page if the short file is not active or doesn't exist
    elif file and not file.state : error_type = 'DISABLED'
    elif file and file.link_type != 'file' : error_type = None
    elif not file : error_type = 'DELETED'
    return redirect(url_for('error.index', error_type = error_type))

@main_bp.errorhandler(RequestEntityTooLarge)
def max_upload_size_exceeded(e):
    flash(
        f"Fichier trop volumineux. Taille max supportée : {Config.MAX_UPLOAD_SIZE}.",
        'danger'
    )
    return redirect(url_for('main.index'))