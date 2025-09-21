function sendNewsletter(newsletterId) {
    if (confirm('Are you sure you want to send this newsletter to all subscribers? This action cannot be undone.')) {
        fetch(`/newsletters/${newsletterId}/send/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert(data.message);
                location.reload();
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(error => {
            alert('Error sending newsletter: ' + error);
        });
    }
} 