import os
from datetime import datetime
from werkzeug.utils import secure_filename
from config import Config
from database.models import File

def allowed_file(filename):
    """
    Vérifie si l'extension du fichier est autorisée.
    
    Args:
        filename (str): Nom du fichier à vérifier
        
    Returns:
        bool: True si l'extension est autorisée, False sinon
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def save_file(file, user_id):
    """
    Enregistre un fichier téléchargé et crée une entrée dans la base de données.
    
    Args:
        file: L'objet fichier provenant de request.files
        user_id (int): ID de l'utilisateur qui télécharge le fichier
        
    Returns:
        File or None: L'objet File si l'enregistrement a réussi, None sinon
    """
    if not file or file.filename == '':
        return None
    
    if not allowed_file(file.filename):
        return None
    
    # Sécuriser le nom du fichier
    original_filename = file.filename
    filename = secure_filename(original_filename)
    
    # Ajouter un timestamp pour éviter les collisions de noms
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    unique_filename = f"{timestamp}_{filename}"
    
    # S'assurer que le dossier d'upload existe
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    
    # Chemin complet du fichier
    file_path = os.path.join(Config.UPLOAD_FOLDER, unique_filename)
    
    # Enregistrer le fichier physiquement
    file.save(file_path)
    
    # Obtenir la taille du fichier
    filesize = os.path.getsize(file_path)
    
    # Créer et enregistrer l'entrée dans la base de données
    file_entry = File(
        filename=unique_filename,
        original_filename=original_filename,
        uploaded_by=user_id,
        upload_date=datetime.now(),
        filesize=filesize
    )
    file_entry.save()
    
    return file_entry

def delete_file(file_id):
    """
    Supprime un fichier du système de fichiers et de la base de données.
    
    Args:
        file_id (int): ID du fichier à supprimer
        
    Returns:
        bool: True si la suppression a réussi, False sinon
    """
    file_entry = File.get_by_id(file_id)
    
    if not file_entry:
        return False
    
    # Chemin complet du fichier
    file_path = os.path.join(Config.UPLOAD_FOLDER, file_entry.filename)
    
    # Supprimer le fichier physique s'il existe
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Erreur lors de la suppression du fichier: {e}")
            return False
    
    # Supprimer l'entrée de la base de données
    success = file_entry.delete()
    
    return success

def get_file_size_display(size_in_bytes):
    """
    Convertit une taille en octets en format lisible (Ko, Mo, Go).
    
    Args:
        size_in_bytes (int): Taille en octets
        
    Returns:
        str: Taille formatée avec unité
    """
    if size_in_bytes < 1024:
        return f"{size_in_bytes} octets"
    elif size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes / 1024:.2f} Ko"
    elif size_in_bytes < 1024 * 1024 * 1024:
        return f"{size_in_bytes / (1024 * 1024):.2f} Mo"
    else:
        return f"{size_in_bytes / (1024 * 1024 * 1024):.2f} Go"
