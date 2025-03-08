import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config

class User:
    """
    Modèle pour la gestion des utilisateurs.
    """
    def __init__(self, id=None, username=None, password=None, is_admin=0):
        self.id = id
        self.username = username
        self.password = password  # Stocke le hash du mot de passe
        self.is_admin = is_admin
    
    @classmethod
    def get_db_connection(cls):
        """
        Établit une connexion à la base de données.
        
        Returns:
            sqlite3.Connection: Objet de connexion à la base de données.
        """
        conn = sqlite3.connect(Config.DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    
    @classmethod
    def get_by_id(cls, user_id):
        """
        Récupère un utilisateur par son ID.
        
        Args:
            user_id (int): ID de l'utilisateur à récupérer.
            
        Returns:
            User: Instance de User si trouvé, None sinon.
        """
        conn = cls.get_db_connection()
        user_data = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        conn.close()
        
        if user_data:
            return cls(
                id=user_data['id'],
                username=user_data['username'],
                password=user_data['password'],
                is_admin=user_data['is_admin']
            )
        return None
    
    @classmethod
    def get_by_username(cls, username):
        """
        Récupère un utilisateur par son nom d'utilisateur.
        
        Args:
            username (str): Nom d'utilisateur à rechercher.
            
        Returns:
            User: Instance de User si trouvé, None sinon.
        """
        conn = cls.get_db_connection()
        user_data = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()
        
        if user_data:
            return cls(
                id=user_data['id'],
                username=user_data['username'],
                password=user_data['password'],
                is_admin=user_data['is_admin']
            )
        return None
    
    @classmethod
    def get_all(cls):
        """
        Récupère tous les utilisateurs.
        
        Returns:
            list: Liste d'instances de User.
        """
        conn = cls.get_db_connection()
        users_data = conn.execute("SELECT * FROM users ORDER BY id").fetchall()
        conn.close()
        
        return [cls(
            id=user['id'],
            username=user['username'],
            password=user['password'],
            is_admin=user['is_admin']
        ) for user in users_data]
    
    def save(self):
        """
        Enregistre l'utilisateur dans la base de données (création ou mise à jour).
        
        Returns:
            int: ID de l'utilisateur.
        """
        conn = self.get_db_connection()
        
        if self.id:  # Mise à jour
            conn.execute(
                "UPDATE users SET username = ?, password = ?, is_admin = ? WHERE id = ?",
                (self.username, self.password, self.is_admin, self.id)
            )
        else:  # Création
            cursor = conn.execute(
                "INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)",
                (self.username, self.password, self.is_admin)
            )
            self.id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        return self.id
    
    def delete(self):
        """
        Supprime l'utilisateur de la base de données.
        
        Returns:
            bool: True si supprimé avec succès, False sinon.
        """
        if not self.id:
            return False
        
        conn = self.get_db_connection()
        conn.execute("DELETE FROM users WHERE id = ?", (self.id,))
        conn.commit()
        conn.close()
        return True
    
    def set_password(self, password):
        """
        Définit le mot de passe de l'utilisateur en le hashant.
        
        Args:
            password (str): Mot de passe en clair.
        """
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """
        Vérifie si le mot de passe fourni correspond au hash stocké.
        
        Args:
            password (str): Mot de passe en clair à vérifier.
            
        Returns:
            bool: True si le mot de passe correspond, False sinon.
        """
        return check_password_hash(self.password, password)


class File:
    """
    Modèle pour la gestion des fichiers.
    """
    def __init__(self, id=None, filename=None, original_filename=None, 
                 uploaded_by=None, upload_date=None, filesize=None):
        self.id = id
        self.filename = filename  # Nom du fichier stocké sur le serveur
        self.original_filename = original_filename  # Nom original du fichier
        self.uploaded_by = uploaded_by  # ID de l'utilisateur qui a téléchargé le fichier
        self.upload_date = upload_date or datetime.now()  # Date de téléchargement
        self.filesize = filesize  # Taille du fichier en octets
    
    @classmethod
    def get_db_connection(cls):
        """
        Établit une connexion à la base de données.
        
        Returns:
            sqlite3.Connection: Objet de connexion à la base de données.
        """
        conn = sqlite3.connect(Config.DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    
    @classmethod
    def get_by_id(cls, file_id):
        """
        Récupère un fichier par son ID.
        
        Args:
            file_id (int): ID du fichier à récupérer.
            
        Returns:
            File: Instance de File si trouvé, None sinon.
        """
        conn = cls.get_db_connection()
        file_data = conn.execute("SELECT * FROM files WHERE id = ?", (file_id,)).fetchone()
        conn.close()
        
        if file_data:
            return cls(
                id=file_data['id'],
                filename=file_data['filename'],
                original_filename=file_data['original_filename'],
                uploaded_by=file_data['uploaded_by'],
                upload_date=file_data['upload_date'],
                filesize=file_data['filesize']
            )
        return None
    
    @classmethod
    def get_all(cls):
        """
        Récupère tous les fichiers.
        
        Returns:
            list: Liste d'instances de File.
        """
        conn = cls.get_db_connection()
        files_data = conn.execute(
            "SELECT * FROM files ORDER BY upload_date DESC"
        ).fetchall()
        conn.close()
        
        return [cls(
            id=file['id'],
            filename=file['filename'],
            original_filename=file['original_filename'],
            uploaded_by=file['uploaded_by'],
            upload_date=file['upload_date'],
            filesize=file['filesize']
        ) for file in files_data]
    
    @classmethod
    def get_all_with_users(cls):
        """
        Récupère tous les fichiers avec les informations des utilisateurs qui les ont téléchargés.
        
        Returns:
            list: Liste de dictionnaires contenant les informations des fichiers et utilisateurs.
        """
        conn = cls.get_db_connection()
        files_data = conn.execute("""
            SELECT files.*, users.username 
            FROM files 
            JOIN users ON files.uploaded_by = users.id
            ORDER BY files.upload_date DESC
        """).fetchall()
        conn.close()
        
        return files_data
    
    def save(self):
        """
        Enregistre le fichier dans la base de données (création ou mise à jour).
        
        Returns:
            int: ID du fichier.
        """
        conn = self.get_db_connection()
        
        if self.id:  # Mise à jour
            conn.execute(
                """UPDATE files 
                   SET filename = ?, original_filename = ?, uploaded_by = ?, 
                       upload_date = ?, filesize = ? 
                   WHERE id = ?""",
                (self.filename, self.original_filename, self.uploaded_by, 
                 self.upload_date, self.filesize, self.id)
            )
        else:  # Création
            cursor = conn.execute(
                """INSERT INTO files 
                   (filename, original_filename, uploaded_by, upload_date, filesize) 
                   VALUES (?, ?, ?, ?, ?)""",
                (self.filename, self.original_filename, self.uploaded_by, 
                 self.upload_date, self.filesize)
            )
            self.id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        return self.id
    
    def delete(self):
        """
        Supprime le fichier de la base de données.
        
        Returns:
            bool: True si supprimé avec succès, False sinon.
        """
        if not self.id:
            return False
        
        conn = self.get_db_connection()
        conn.execute("DELETE FROM files WHERE id = ?", (self.id,))
        conn.commit()
        conn.close()
        return True
