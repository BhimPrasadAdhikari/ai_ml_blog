function sendNewsletter(newsletterId) {
    if (confirm('Are you sure you want to send this newsletter to all subscribers?')) {
        fetch(`/newsletters/${newsletterId}/send/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert('Newsletter sent successfully!');
                location.reload();
            } else {
                alert('Error sending newsletter: ' + data.message);
            }
        });
    }
}

function previewNewsletter(newsletterId) {
    window.open(`/newsletters/${newsletterId}/preview/`, '_blank');
}

function editNewsletter(newsletterId) {
    window.location.href = `/newsletters/${newsletterId}/edit/`;
}

function deleteNewsletter(newsletterId) {
    if (confirm('Are you sure you want to delete this newsletter? This action cannot be undone.')) {
        fetch(`/newsletters/${newsletterId}/delete/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert('Newsletter deleted successfully!');
                location.reload();
            } else {
                alert('Error deleting newsletter: ' + data.message);
            }
        });
    }
} 