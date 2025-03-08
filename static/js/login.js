// JavaScript pour la page de connexion

document.addEventListener('DOMContentLoaded', function() {
    // Sélectionner le formulaire de connexion
    const loginForm = document.querySelector('form');
    
    // Ajouter un gestionnaire d'événements pour la soumission du formulaire
    if (loginForm) {
        loginForm.addEventListener('submit', function(event) {
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            // Validation simple côté client
            if (!username.trim() || !password.trim()) {
                event.preventDefault();
                alert('Veuillez remplir tous les champs.');
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
});
