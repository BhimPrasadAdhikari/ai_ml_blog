// user_bookmarks.js

document.addEventListener('DOMContentLoaded', function() {
    const bookmarkBtn = document.getElementById('bookmark-btn');

    if (bookmarkBtn) {
        bookmarkBtn.addEventListener('click', function() {
            // Check if user is logged in (simple check based on button existence/state)
            // ideally, the backend should return 401 or 403, handled below.
            
            const postSlug = this.dataset.postSlug;
            const icon = this.querySelector('i');
            const isCurrentlyBookmarked = this.classList.contains('bookmarked');

            // 1. Optimistic UI Update (Make it feel instant)
            this.classList.toggle('bookmarked');
            if (isCurrentlyBookmarked) {
                // Was bookmarked, now removing
                icon.classList.remove('fas');
                icon.classList.add('far');
            } else {
                // Was not bookmarked, now adding
                icon.classList.remove('far');
                icon.classList.add('fas');
            }

            // 2. Send Request to Backend
            fetch(`/post/${postSlug}/bookmark/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                if (response.status === 403 || response.status === 401) {
                    // User not logged in
                    alert("Please login to bookmark posts.");
                    window.location.href = "/accounts/login/";
                    throw new Error("Not logged in");
                }
                return response.json();
            })
            .then(data => {
                if (data.status !== 'success') {
                    // Revert UI on error
                    toggleBookmarkUI(bookmarkBtn, icon, !isCurrentlyBookmarked);
                    console.error('Bookmark failed:', data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                if (error.message !== "Not logged in") {
                    // Revert UI on network error
                    toggleBookmarkUI(bookmarkBtn, icon, !isCurrentlyBookmarked);
                }
            });
        });
    }
});

// Helper to toggle UI classes
function toggleBookmarkUI(btn, icon, makeBookmarked) {
    if (makeBookmarked) {
        btn.classList.add('bookmarked');
        icon.classList.remove('far');
        icon.classList.add('fas');
    } else {
        btn.classList.remove('bookmarked');
        icon.classList.remove('fas');
        icon.classList.add('far');
    }
}

// Helper to get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}