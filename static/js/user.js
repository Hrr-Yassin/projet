// JavaScript pour la page utilisateur

document.addEventListener('DOMContentLoaded', function() {
    // Sélectionner le formulaire de téléchargement de fichier
    const uploadForm = document.querySelector('form');
    
    // Ajouter un gestionnaire d'événements pour la soumission du formulaire
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(event) {
            const fileInput = document.getElementById('file');
            
            // Validation simple côté client
            if (!fileInput.files || fileInput.files.length === 0) {
                event.preventDefault();
                alert('Veuillez sélectionner un fichier.');
                return false;
            }
            
            // Vérifier l'extension du fichier
            const fileName = fileInput.files[0].name;
            const fileExt = fileName.split('.').pop().toLowerCase();
            const allowedExtensions = ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'zip'];
            
            if (!allowedExtensions.includes(fileExt)) {
                event.preventDefault();
                alert('Type de fichier non autorisé. Veuillez sélectionner un fichier avec une extension valide : ' + allowedExtensions.join(', '));
                return false;
            }
            
            // Vérifier la taille du fichier (max 16 Mo)
            const maxSize = 16 * 1024 * 1024; // 16 Mo en octets
            if (fileInput.files[0].size > maxSize) {
                event.preventDefault();
                alert('Le fichier est trop volumineux. La taille maximale autorisée est de 16 Mo.');
                return false;
            }
            
            // Si tout est valide, le formulaire sera soumis normalement
        });
    }
    
    // Faire disparaître les messages flash après quelques secondes
    const flashMessages = document.querySelectorAll('.flash-message');
    if (flashMessages.length > 0) {
        setTimeout(function() {
            flashMessages.forEach(function(message) {
                message.style.opacity = '0';
                setTimeout(function() {
                    message.style.display = 'none';
                }, 500);
            });
        }, 5000);
    }
    
    // Formatage de la date pour un affichage plus convivial
    const dateCells = document.querySelectorAll('td:nth-child(3)');
    dateCells.forEach(function(cell) {
        try {
            const date = new Date(cell.textContent);
            if (!isNaN(date)) {
                cell.textContent = date.toLocaleString();
            }
        } catch (e) {
            // Si la conversion échoue, conserver le format d'origine
        }
    });
});
