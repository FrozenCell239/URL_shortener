from app.error import error_bp
from flask import render_template, request

@error_bp.route('/', methods = ['GET'])
def index():
    match request.args.get('error_type') :
        case 'DELETED' :
            type = "lien inexistant"
            description = "Il semblerait que le lien sur lequel vous avez cliqué n'existe pas ou a été supprimé. =/"
        case 'DISABLED' :
            type = "lien désactivé"
            description = "Le/la propriétaire du lien sur lequel vous avez cliqué l'a désactivé pour le moment. Réessayez plus tard. ;)"
        case 'FILE_NOT_FOUND' :
            type = "fichier manquant"
            description = "Le fichier attaché à ce lien est bien repertorié et n'est pas désactivé, mais le fichier n'est pas présent sur notre serveur."
        case _ :
            type = "inconnue"
            description = "Un problème d'origine inconnue vient de se produire. =("
    return render_template(
        'error/index.html.jinja',
        title = type[0].upper() + type[1:],
        error_type = type,
        error_description = description
    )