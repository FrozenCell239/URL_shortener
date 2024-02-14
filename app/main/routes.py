from flask import\
    render_template,\
    redirect,\
    url_for,\
    flash,\
    send_from_directory,\
    request,\
    session
from app import csrf
from app.extensions import db
from app.main import main_bp
from app.models.link import Link, File
from app.models.user import User
from config import AppInfos
from datetime import datetime
from os import makedirs, stat, remove
from os.path import join, isdir, isfile
from shutil import move
from werkzeug.utils import secure_filename as sf

@main_bp.route('/', methods = ['POST', 'GET'])
@main_bp.route('/<string:requested_link>')
@csrf.exempt
def index(requested_link : str = None):
    # Redirecting short links to original ones
    if requested_link :
        # Getting the link from database
        link = Link.query.filter_by(short = requested_link).first()

        # Redirecting to the original link if the short one exists and is not disabled
        if link and link.getState() == True :
            link.incrementClicks()
            db.session.commit()
            return redirect(link.getOriginal(), code = 301)

        # Redirecting to an error page if the short link is not active or doesn't exist
        elif link and not link.getState() : error_type = 'DISABLED'
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
                    #//shortened_length = 8,
                    owner_id = session['user_id'],
                    original = original_url
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
                        onclick="toClipboard('{ AppInfos.domain_name() + new_link.getShort() }')"
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
            no_tmp_file = False

            # Checking if file's format is allowed
            if not File.isFileFormatAllowed(new_upload.filename) :
                errors.append("Ce format de fichier n'est pas autorisé.")
                no_tmp_file = True

            # Saving first the file in a temp folder
            if not isdir(AppInfos.tmp_folder()) : makedirs(AppInfos.tmp_folder())
            if not no_tmp_file : new_upload.save(join(AppInfos.tmp_folder(), new_filename))

            # Checking if file size limit is exceeded
            if(
                not no_tmp_file and
                stat(join(AppInfos.tmp_folder(), new_filename)).st_size > AppInfos.max_upload_size()
            ):
                errors.append(
                    f"Fichier trop volumineux. Taille max supportée : {AppInfos.max_upload_size(str)}."
                )
                remove(join(AppInfos.tmp_folder(), new_filename))
            
            # File upload if no error occured
            if errors == [] :
                # Creating the uploads directory if it doesn't exist
                if not isdir(AppInfos.upload_folder()) : makedirs(AppInfos.upload_folder())

                # Saving the file on the server
                move(
                    join(AppInfos.tmp_folder(), new_filename),
                    join(AppInfos.upload_folder(), new_filename)
                )

                # Registering the file in the database
                new_file_link = File(
                    #//shortened_length = 8,
                    owner_id = session['user_id'],
                    attached_file_name = new_filename
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
                        onclick="toClipboard('{ AppInfos.domain_name()}dl/{new_file_link.getShort() }')"
                    >
                        Copier le lien
                    </a>
                    """,
                    'success'
                )

    # Remind user to verify its mail address if it's still not verified
    if(
        'user_id' in session and not
        (User.query.filter_by(id = session['user_id']).first()).getIsVerified()
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
    return render_template('index.html.jinja', title = AppInfos.web_app_name())

@main_bp.route('/dl/<string:requested_file>')
def download(requested_file : str = None):
    # Main page display if no file link is passed
    if not requested_file : return redirect(url_for('main.index'))
    
    # Getting the file name from database
    file = File.query.filter_by(short = requested_file).first()

    # Sending the file if it exists and is not disabled
    if file and file.getState() :
        # Checking if the file still exists on the server
        if not isfile(f'{AppInfos.upload_folder()}/{file.getAttachedFileName()}') :
            return redirect(url_for('error.index', error_type = 'FILE_NOT_FOUND'))

        # Sending the file to the user
        file.incrementClicks()
        db.session.commit()
        return send_from_directory(
            '../' + AppInfos.upload_folder(),
            file.getAttachedFileName(),
            as_attachment = True
        )

    # Redirecting to an error page if the short file is not active or doesn't exist
    elif file and not file.getState() : error_type = 'DISABLED'
    elif not file : error_type = 'DELETED'
    return redirect(url_for('error.index', error_type = error_type))