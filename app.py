from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
import sqlite3
from datetime import datetime
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Assurez-vous que le dossier d'upload existe
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Fonction pour vérifier si l'extension de fichier est autorisée
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Fonction pour obtenir une connexion à la base de données
def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE_PATH'])
    conn.row_factory = sqlite3.Row
    return conn

# Initialisation de la base de données si elle n'existe pas
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Création de la table users si elle n'existe pas
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        is_admin INTEGER NOT NULL DEFAULT 0
    )
    ''')
    
    # Création de la table files si elle n'existe pas
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
    
    # Vérifier si un admin existe déjà, sinon en créer un
    cursor.execute("SELECT * FROM users WHERE is_admin = 1")
    if not cursor.fetchone():
        admin_password = generate_password_hash('admin123')
        cursor.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, 1)", 
                      ('admin', admin_password))
    
    conn.commit()
    conn.close()

# Initialiser la base de données au démarrage de l'application
init_db()

# Middleware pour vérifier si l'utilisateur est connecté
@app.before_request
def require_login():
    allowed_routes = ['login', 'static']
    if request.endpoint not in allowed_routes and 'user_id' not in session:
        return redirect(url_for('login'))

# Route pour la page de connexion
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = user['is_admin']
            
            if user['is_admin']:
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        
        flash('Nom d\'utilisateur ou mot de passe incorrect')
    
    return render_template('login.html')

# Route pour la déconnexion
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Route pour le tableau de bord utilisateur
@app.route('/user')
def user_dashboard():
    if session.get('is_admin'):
        return redirect(url_for('admin_dashboard'))
    
    conn = get_db_connection()
    files = conn.execute('''
    SELECT files.id, files.original_filename, files.upload_date, files.filesize, users.username 
    FROM files 
    JOIN users ON files.uploaded_by = users.id
    ORDER BY files.upload_date DESC
    ''').fetchall()
    conn.close()
    
    return render_template('user.html', files=files)

# Route pour le tableau de bord admin
@app.route('/admin')
def admin_dashboard():
    if not session.get('is_admin'):
        return redirect(url_for('user_dashboard'))
    
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    files = conn.execute('''
    SELECT files.id, files.original_filename, files.upload_date, files.filesize, users.username 
    FROM files 
    JOIN users ON files.uploaded_by = users.id
    ORDER BY files.upload_date DESC
    ''').fetchall()
    conn.close()
    
    return render_template('admin.html', users=users, files=files)

# Route pour télécharger un fichier
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('Aucun fichier sélectionné')
        return redirect(request.referrer)
    
    file = request.files['file']
    
    if file.filename == '':
        flash('Aucun fichier sélectionné')
        return redirect(request.referrer)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Ajouter un timestamp pour éviter les conflits de noms de fichiers
        unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        # Enregistrer les informations du fichier dans la base de données
        conn = get_db_connection()
        conn.execute('''
        INSERT INTO files (filename, original_filename, uploaded_by, upload_date, filesize)
        VALUES (?, ?, ?, ?, ?)
        ''', (unique_filename, filename, session['user_id'], datetime.now(), os.path.getsize(file_path)))
        conn.commit()
        conn.close()
        
        flash('Fichier téléchargé avec succès')
    else:
        flash('Type de fichier non autorisé')
    
    if session.get('is_admin'):
        return redirect(url_for('admin_dashboard'))
    else:
        return redirect(url_for('user_dashboard'))

# Route pour télécharger un fichier
@app.route('/download/<int:file_id>')
def download_file(file_id):
    conn = get_db_connection()
    file = conn.execute('SELECT * FROM files WHERE id = ?', (file_id,)).fetchone()
    conn.close()
    
    if file:
        return send_from_directory(app.config['UPLOAD_FOLDER'], file['filename'], 
                                   download_name=file['original_filename'], as_attachment=True)
    
    flash('Fichier non trouvé')
    return redirect(request.referrer)

# Routes pour la gestion des utilisateurs (admin uniquement)
@app.route('/admin/create_user', methods=['POST'])
def create_user():
    if not session.get('is_admin'):
        return redirect(url_for('user_dashboard'))
    
    username = request.form['username']
    password = request.form['password']
    is_admin = 1 if request.form.get('is_admin') else 0
    
    # Vérifier si l'utilisateur existe déjà
    conn = get_db_connection()
    existing_user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    
    if existing_user:
        flash('Ce nom d\'utilisateur existe déjà')
        return redirect(url_for('admin_dashboard'))
    
    # Hasher le mot de passe et créer l'utilisateur
    hashed_password = generate_password_hash(password)
    conn.execute('INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)', 
                (username, hashed_password, is_admin))
    conn.commit()
    conn.close()
    
    flash('Utilisateur créé avec succès')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if not session.get('is_admin'):
        return redirect(url_for('user_dashboard'))
    
    # Ne pas permettre de supprimer l'administrateur courant
    if user_id == session['user_id']:
        flash('Vous ne pouvez pas supprimer votre propre compte')
        return redirect(url_for('admin_dashboard'))
    
    conn = get_db_connection()
    conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    
    flash('Utilisateur supprimé avec succès')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/update_user/<int:user_id>', methods=['POST'])
def update_user(user_id):
    if not session.get('is_admin'):
        return redirect(url_for('user_dashboard'))
    
    is_admin = 1 if request.form.get('is_admin') else 0
    
    conn = get_db_connection()
    conn.execute('UPDATE users SET is_admin = ? WHERE id = ?', (is_admin, user_id))
    conn.commit()
    conn.close()
    
    flash('Droits utilisateur mis à jour avec succès')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_file/<int:file_id>', methods=['POST'])
def delete_file(file_id):
    if not session.get('is_admin'):
        return redirect(url_for('user_dashboard'))
    
    conn = get_db_connection()
    file = conn.execute('SELECT * FROM files WHERE id = ?', (file_id,)).fetchone()
    
    if file:
        # Supprimer le fichier physique
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], file['filename']))
        except:
            pass
        
        # Supprimer l'entrée de la base de données
        conn.execute('DELETE FROM files WHERE id = ?', (file_id,))
        conn.commit()
        flash('Fichier supprimé avec succès')
    else:
        flash('Fichier non trouvé')
    
    conn.close()
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
