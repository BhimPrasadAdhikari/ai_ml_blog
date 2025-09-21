// Profile picture modal logic

document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('profile-picture-modal');
    const closeBtn = document.getElementById('profile-picture-modal-close');
    const thumb = document.getElementById('profile-picture-thumb');
    if (thumb) {
        thumb.addEventListener('click', function() {
            modal.classList.add('active');
        });
    }
    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            modal.classList.remove('active');
        });
    }
    modal?.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.classList.remove('active');
        }
    });
}); 