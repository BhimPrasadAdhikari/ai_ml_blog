// Real-time preview functionality

document.addEventListener('DOMContentLoaded', function() {
    const subjectInput = document.querySelector('input[name="subject"]');
    const contentTextarea = document.querySelector('textarea[name="content"]');
    const previewSubject = document.getElementById('preview-subject');
    const previewBody = document.getElementById('preview-body');

    function updatePreview() {
        if (subjectInput) {
            previewSubject.textContent = subjectInput.value || 'Your newsletter subject will appear here';
        }
        if (contentTextarea) {
            previewBody.innerHTML = contentTextarea.value || 'Your newsletter content will appear here';
        }
    }

    if (subjectInput) {
        subjectInput.addEventListener('input', updatePreview);
    }
    if (contentTextarea) {
        contentTextarea.addEventListener('input', updatePreview);
    }

    // Initialize preview
    updatePreview();
});

function sendNewsletter() {
    if (confirm('Are you sure you want to send this newsletter to all subscribers? This action cannot be undone.')) {
        // You can add AJAX call here to send the newsletter
        alert('Newsletter sending functionality will be implemented here.');
    }
} 