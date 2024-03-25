from app.extensions import db, limiter
from app.models.user import User
from app.registration import registration_bp
from app.utils import JWT, sendMail, logout_required, login_required
from config import Config
from flask import render_template, redirect, url_for, flash, request, session

@registration_bp.route('/register', methods = ['POST', 'GET'])
@logout_required
def index():
    # Register form handling
    errors = []
    if request.method == 'POST' :
        # Errors handling
        if request.form['username'] == '' :
            errors.append("Le nom d'utilisateur ne peut pas être vide.")
        if request.form['mail'] == '' :
            errors.append("L'adresse mail ne peut pas être vide.")
        if request.form['password'] == '' :
            errors.append("Le mot de passe ne peut pas être vide.")
        if request.form['password'] != request.form['password_confirm'] :
            errors.append("Les mots de passes ne sont pas identiques.")
        if User.query.filter_by(username = request.form['username']).first():
            errors.append("Un autre compte possède déjà le nom d'utilisateur que vous avez saisi.")
        if User.query.filter_by(mail = request.form['mail']).first():
            errors.append("Un autre compte possède déjà l'adresse mail que vous avez saisie.")
        password_strength_check = User.checkPasswordStrength(request.form['password'])
        if not password_strength_check['password_ok'] :
            strength_errors = "Le mot de passe ne respecte pas la/les condition(s) de sécurité suivante(s) : "
            for criteria, checked in password_strength_check.items() :
                if checked :
                    match criteria :
                        case 'length_error' : strength_errors += "8 caractères ou plus, "
                        case 'digit_error' : strength_errors += "1 chiffre ou plus, "
                        case 'uppercase_error' : strength_errors += "1 lettre majuscule ou plus, "
                        case 'lowercase_error' : strength_errors += "1 lettre minuscule ou plus, "
                        case 'symbol_error' : strength_errors += "1 caractère spécial ou plus, "
            errors.append(strength_errors[:-2] + ".")

        # New user registering if no error occured
        if errors == [] :
            try:
                # Register user into the database
                user = User(
                    request.form['username'],
                    request.form['mail']
                )
                user.setPassword(request.form['password'])
                db.session.add(user)
                db.session.commit()

                # Sending verification mail to user
                token_validity_time = 24
                sendMail(
                    to = user.mail,
                    subject = f"{Config.WEB_APP_NAME} : Activation de votre compte",
                    template_path = 'emails/register_mail.html.jinja',
                    infos = {
                        'username' : user.username.title(),
                        'token_validity_time' : token_validity_time,
                        'token' : JWT.generate(
                            validity_time = token_validity_time,
                            payload = {'user_id' : user.id}
                        )
                    }
                )
            except:
                flash(
                    "Un problème est survenu lors de la création de votre compte. Veuillez réessayer ultérieurement.",
                    'danger'
                )
                return redirect(url_for('registration.index'))
            else:
                # Automatically log-in the user
                session.permanent = True
                session['user_id'] = (User.query.filter_by(mail = user.mail).first()).id
                session['username'] = user.username

                # Redirecting user to main page
                return redirect(url_for('main.index'))
        
    # Register page display with errors if some occured
    for error in errors : flash(error, 'danger')
    return render_template('register.html.jinja', title = "Inscription")

@registration_bp.route('/verify/<string:token>')
@limiter.limit('200/day;100/hour;20/minute')
def verify_user(token : str = None):
    # Checking token's validity, expiration, and integrity
    try: token = JWT(token)
    
    # Invalid or expired token case
    except: flash("Jeton de vérification invalide.", 'danger')

    # Getting user from its ID and verify its mail address
    else:
        verified_user_id = token.getPayload()['user_id']
        user = User.query.filter_by(id = verified_user_id).first()
        if user.is_verified :
            flash("Votre adresse mail a déjà été vérifiée.", 'info')
        else:
            user.is_verified = True
            db.session.commit()
            flash("Votre adresse mail a été vérifiée avec succès !", 'success')

    return redirect(url_for('main.index'))

@registration_bp.route('/resend_verification')
@limiter.limit('30/day;20/hour;10/minute')
@login_required
def resend_verification():
    # Getting user's mail address
    user = User.query.filter_by(id = session['user_id']).first()

    # Sending verification mail to user if still not verified
    if not user.is_verified :
        try:
            # Sending verification mail to user
            token_validity_time : float = 24
            sendMail(
                to = user.mail,
                subject = f"{Config.WEB_APP_NAME} : Activation de votre compte",
                template_path = 'emails/register_mail.html.jinja',
                infos = {
                    'username' : user.username.title(),
                    'token_validity_time' : str(token_validity_time),
                    'token' : JWT.generate(
                        validity_time = token_validity_time,
                        payload = {'user_id' : user.id}
                    )
                }
            )
        except:
            flash(
                "Un problème est survenu lors du renvoi du mail. Veuillez réessayer ultérieurement.",
                'danger'
            )
            return redirect(url_for('registration.index'))
        else:
            flash(
                "Un nouveau mail de vérification vient de vous être envoyé.",
                'info'
            )

    return redirect(url_for('main.index'))