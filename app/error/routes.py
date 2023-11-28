from flask import render_template, request
from app.error import error_bp

@error_bp.route('/', methods = ['GET'])
def index():
    if request.args.get('error_type') == 'DELETED' :
        type = "lien inexistant"
        description = "Il semblerait que le lien sur lequel vous avez cliqué n'existe pas ou a été supprimé. =/"
    elif request.args.get('error_type') == 'DISABLED' :
        type = "lien désactivé"
        description = "Le/la propriétaire du lien sur lequel vous avez cliqué l'a désactivé pour le moment. Réessayez plus tard. ;)"
    else:
        type = "inconnue"
        description = "Un problème d'origine inconnue vient de se produire. =("
    return render_template(
        'error/index.html.jinja',
        title = 'Erreur de redirection',
        error_type = type,
        error_description = description
    )