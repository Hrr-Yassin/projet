import sqlite3
import os
from werkzeug.security import generate_password_hash
from config import Config

def init_database():
    """
    Initialise la base de données en créant les tables nécessaires
    et l'utilisateur administrateur par défaut si nécessaire.
    """
    # S'assurer que le répertoire parent existe
    os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
    
    # Établir une connexion à la base de données
    conn = sqlite3.connect(Config.DATABASE_PATH)
    cursor = conn.cursor()
    
    # Créer la table des utilisateurs
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        is_admin INTEGER NOT NULL DEFAULT 0
    )
    ''')
    
    # Créer la table des fichiers
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        original_filename TEXT NOT NULL,
        uploaded_by INTEGER NOT NULL,
        upload_date TIMESTAMP NOT NULL,
        filesize INTEGER NOT NULL,
        FOREIGN KEY (uploaded_by) REFERENCES users (id)
    )
    ''')
    
    # Vérifier si un administrateur existe déjà
    cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = 1")
    admin_count = cursor.fetchone()[0]
    
    # Si aucun administrateur n'existe, en créer un par défaut
    if admin_count == 0:
        admin_username = 'admin'
        admin_password = 'admin123'  # Mot de passe par défaut, à modifier après la première connexion
        hashed_password = generate_password_hash(admin_password)
        
        cursor.execute(
            "INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)",
            (admin_username, hashed_password, 1)
        )
        print(f"Utilisateur administrateur créé : {admin_username} (mot de passe: {admin_password})")
    
    # Valider les modifications et fermer la connexion
    conn.commit()
    conn.close()
    
    print("Base de données initialisée avec succès.")

if __name__ == "__main__":
    # Ce bloc permet d'exécuter le script directement
    init_database()
