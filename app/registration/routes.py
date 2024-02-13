from flask import render_template, redirect, url_for, flash, request
from app.extensions import db
from app.registration import registration_bp
from app.models.user import User
from app.utils import JWT, sendMail, logout_required

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
            try :
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
                    to = request.form['mail'],
                    subject = "EasyLink : activation de votre compte",
                    template_path = 'emails/register_mail.html.jinja',
                    infos = {
                        'username' : request.form['username'].title(),
                        'token_validity_time' : str(token_validity_time),
                        'token' : JWT.generate(
                            validity_time = token_validity_time,
                            payload = {'user_id' : user.getID()}
                        )
                    }
                )
            except :
                flash(
                    "Un problème est survenu lors de la création de votre compte. Veuillez réessayer ultérieurement.",
                    'danger'
                )
                return redirect(url_for('registration.index'))
            else :
                flash(
                    "Votre compte a été créé avec succès ! Connectez-vous dès à présent.",
                    'success'
                )

            # Redirecting user to login page
            return redirect(url_for('security.login'))
        
    # Register page display with errors if some occured
    for error in errors : flash(error, 'danger')
    return render_template('register.html.jinja', title = "Inscription")