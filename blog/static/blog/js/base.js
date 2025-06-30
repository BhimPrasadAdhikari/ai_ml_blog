// Newsletter subscribe/unsubscribe and theme toggling

document.addEventListener('DOMContentLoaded', function() {
    const subscribeForm = document.getElementById('newsletter-form');
    const unsubscribeForm = document.getElementById('unsubscribe-newsletter-form');
    const subscribeDiv = document.getElementById('subscribe-form');
    const unsubscribeDiv = document.getElementById('unsubscribe-form');
    const messageDiv = document.getElementById('newsletter-message');
    
    // Check subscription status when email is entered
    const emailInput = document.querySelector('input[name="email"]');
    if (emailInput) {
        emailInput.addEventListener('blur', function() {
            const email = this.value;
            if (email && email.includes('@')) {
                fetch(subscribeForm.action + `?email=${encodeURIComponent(email)}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.is_subscribed) {
                            subscribeDiv.style.display = 'none';
                            unsubscribeDiv.style.display = 'block';
                            document.getElementById('unsubscribe-email').value = email;
                        } else {
                            subscribeDiv.style.display = 'block';
                            unsubscribeDiv.style.display = 'none';
                        }
                    });
            }
        });
    }
    
    // Handle subscribe form submission
    if (subscribeForm) {
        subscribeForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const data = new FormData(this);
            fetch(this.action, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': data.get('csrfmiddlewaretoken'),
                },
                body: data
            })
            .then(response => response.json())
            .then(data => {
                messageDiv.innerText = data.message;
                messageDiv.style.color = data.status === 'success' ? '#28a745' : '#dc3545';
                if (data.status === 'success') {
                    // Show unsubscribe form after successful subscription
                    subscribeDiv.style.display = 'none';
                    unsubscribeDiv.style.display = 'block';
                    document.getElementById('unsubscribe-email').value = data.email || '';
                    this.reset();
                }
            });
        });
    }
    
    // Handle unsubscribe form submission
    if (unsubscribeForm) {
        unsubscribeForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const data = new FormData(this);
            fetch(this.action, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': data.get('csrfmiddlewaretoken'),
                },
                body: data
            })
            .then(response => response.json())
            .then(data => {
                messageDiv.innerText = data.message;
                messageDiv.style.color = data.status === 'success' ? '#28a745' : '#dc3545';
                if (data.status === 'success') {
                    // Show subscribe form after successful unsubscription
                    subscribeDiv.style.display = 'block';
                    unsubscribeDiv.style.display = 'none';
                    this.reset();
                }
            });
        });
    }
});
    
// Theme toggling
const themeToggle = document.getElementById('theme-toggle');
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');
const body = document.body;
function setTheme(isDark) {
    body.classList.toggle('dark-theme', isDark);
    themeToggle.innerHTML = isDark ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
}
const savedTheme = localStorage.getItem('theme');
const isDark = savedTheme ? savedTheme === 'dark' : prefersDark.matches;
setTheme(isDark);
themeToggle?.addEventListener('click', () => {
    setTheme(!body.classList.contains('dark-theme'));
});
prefersDark.addEventListener('change', (e) => {
    if (!localStorage.getItem('theme')) setTheme(e.matches);
}); 