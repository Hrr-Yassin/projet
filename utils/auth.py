from functools import wraps
from flask import session, redirect, url_for, request, flash
from database.models import User

def login_required(f):
    """
    Décorateur pour protéger les routes qui nécessitent une authentification.
    Redirige vers la page de connexion si l'utilisateur n'est pas connecté.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """
    Décorateur pour protéger les routes qui nécessitent des droits d'administrateur.
    Redirige vers le tableau de bord utilisateur si l'utilisateur n'est pas admin.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.url))
        if not session.get('is_admin'):
            flash("Vous n'avez pas les droits d'accès nécessaires.")
            return redirect(url_for('user_dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def authenticate_user(username, password):
    """
    Authentifie un utilisateur en vérifiant son nom d'utilisateur et son mot de passe.
    
    Args:
        username (str): Nom d'utilisateur
        password (str): Mot de passe
        
    Returns:
        User or None: L'objet utilisateur s'il est authentifié, None sinon
    """
    user = User.get_by_username(username)
    if user and user.check_password(password):
        return user
    return None

def set_user_session(user):
    """
    Configure la session utilisateur après une authentification réussie.
    
    Args:
        user (User): L'objet utilisateur
    """
    session['user_id'] = user.id
    session['username'] = user.username
    session['is_admin'] = user.is_admin
