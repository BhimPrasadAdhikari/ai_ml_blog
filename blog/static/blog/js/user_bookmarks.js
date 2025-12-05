// user_bookmarks.js - Enhanced bookmarks page functionality

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const notesModal = document.getElementById('notesModal');
    const notesTextarea = document.getElementById('notesTextarea');
    const closeNotesModal = document.getElementById('closeNotesModal');
    const cancelNotes = document.getElementById('cancelNotes');
    const saveNotes = document.getElementById('saveNotes');
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toastMessage');

    let currentPostSlug = null;
    let currentCardElement = null;

    // Initialize all event listeners
    initRemoveButtons();
    initAddNotesButtons();
    initEditNotesButtons();
    initModalControls();

    // Remove bookmark functionality
    function initRemoveButtons() {
        document.querySelectorAll('.remove-btn').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                const postSlug = this.dataset.postSlug;
                const card = this.closest('.bookmark-card');
                
                if (confirm('Remove this bookmark?')) {
                    removeBookmark(postSlug, card);
                }
            });
        });
    }

    // Add notes button functionality
    function initAddNotesButtons() {
        document.querySelectorAll('.add-notes-btn').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                currentPostSlug = this.dataset.postSlug;
                currentCardElement = this.closest('.bookmark-card');
                notesTextarea.value = '';
                openModal();
            });
        });
    }

    // Edit notes button functionality
    function initEditNotesButtons() {
        document.querySelectorAll('.edit-notes-btn').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                currentPostSlug = this.dataset.postSlug;
                currentCardElement = this.closest('.bookmark-card');
                notesTextarea.value = this.dataset.notes || '';
                openModal();
            });
        });
    }

    // Modal controls
    function initModalControls() {
        if (closeNotesModal) {
            closeNotesModal.addEventListener('click', closeModal);
        }
        if (cancelNotes) {
            cancelNotes.addEventListener('click', closeModal);
        }
        if (saveNotes) {
            saveNotes.addEventListener('click', handleSaveNotes);
        }
        if (notesModal) {
            notesModal.addEventListener('click', function(e) {
                if (e.target === notesModal) {
                    closeModal();
                }
            });
        }
        // Close modal on Escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && notesModal && notesModal.classList.contains('active')) {
                closeModal();
            }
        });
    }

    // Open modal
    function openModal() {
        if (notesModal) {
            notesModal.classList.add('active');
            notesTextarea.focus();
        }
    }

    // Close modal
    function closeModal() {
        if (notesModal) {
            notesModal.classList.remove('active');
            currentPostSlug = null;
            currentCardElement = null;
        }
    }

    // Handle save notes
    function handleSaveNotes() {
        if (!currentPostSlug) return;

        const notes = notesTextarea.value.trim();
        
        fetch(`/post/${currentPostSlug}/bookmark/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: `action=update_notes&notes=${encodeURIComponent(notes)}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showToast('Notes saved successfully!', 'success');
                updateNotesUI(notes);
                closeModal();
            } else {
                showToast(data.message || 'Failed to save notes', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('An error occurred', 'error');
        });
    }

    // Update notes UI after saving
    function updateNotesUI(notes) {
        if (!currentCardElement) return;

        const cardContent = currentCardElement.querySelector('.bookmark-card-content');
        const existingNotes = cardContent.querySelector('.bookmark-notes');
        const addNotesBtn = cardContent.querySelector('.add-notes-btn');

        if (notes) {
            const notesHtml = `
                <div class="bookmark-notes">
                    <i class="fas fa-sticky-note"></i>
                    <span class="bookmark-notes-text">${escapeHtml(notes)}</span>
                    <div class="bookmark-notes-actions">
                        <button class="bookmark-notes-btn edit-notes-btn" title="Edit notes" data-post-slug="${currentPostSlug}" data-notes="${escapeHtml(notes)}">
                            <i class="fas fa-edit"></i>
                        </button>
                    </div>
                </div>
            `;

            if (existingNotes) {
                existingNotes.outerHTML = notesHtml;
            } else if (addNotesBtn) {
                addNotesBtn.outerHTML = notesHtml;
            }

            // Re-initialize edit button
            const newEditBtn = cardContent.querySelector('.edit-notes-btn');
            if (newEditBtn) {
                newEditBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    currentPostSlug = this.dataset.postSlug;
                    currentCardElement = this.closest('.bookmark-card');
                    notesTextarea.value = this.dataset.notes || '';
                    openModal();
                });
            }
        } else {
            // Notes cleared, show add button
            if (existingNotes) {
                existingNotes.outerHTML = `
                    <button class="add-notes-btn" data-post-slug="${currentPostSlug}">
                        <i class="fas fa-plus"></i> Add personal notes
                    </button>
                `;
                
                const newAddBtn = cardContent.querySelector('.add-notes-btn');
                if (newAddBtn) {
                    newAddBtn.addEventListener('click', function(e) {
                        e.preventDefault();
                        currentPostSlug = this.dataset.postSlug;
                        currentCardElement = this.closest('.bookmark-card');
                        notesTextarea.value = '';
                        openModal();
                    });
                }
            }
        }
    }

    // Remove bookmark
    function removeBookmark(postSlug, cardElement) {
        fetch(`/post/${postSlug}/bookmark/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: 'action=remove'
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Animate card removal
                cardElement.style.transition = 'all 0.3s ease';
                cardElement.style.transform = 'scale(0.8)';
                cardElement.style.opacity = '0';
                
                setTimeout(() => {
                    cardElement.remove();
                    showToast('Bookmark removed', 'success');
                    
                    // Check if no more bookmarks
                    const remainingCards = document.querySelectorAll('.bookmark-card');
                    if (remainingCards.length === 0) {
                        location.reload(); // Reload to show empty state
                    }
                    
                    // Update count
                    updateBookmarkCount();
                }, 300);
            } else {
                showToast(data.message || 'Failed to remove bookmark', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('An error occurred', 'error');
        });
    }

    // Update bookmark count in header
    function updateBookmarkCount() {
        const countElement = document.querySelector('.bookmarks-count');
        if (countElement) {
            const currentCards = document.querySelectorAll('.bookmark-card').length;
            countElement.innerHTML = `<i class="fas fa-layer-group"></i> ${currentCards} saved post${currentCards !== 1 ? 's' : ''}`;
        }
    }

    // Show toast notification
    function showToast(message, type = 'success') {
        if (!toast || !toastMessage) return;
        
        toastMessage.textContent = message;
        toast.className = `toast ${type}`;
        
        const icon = toast.querySelector('i');
        if (icon) {
            icon.className = type === 'success' ? 'fas fa-check-circle' : 'fas fa-exclamation-circle';
        }
        
        toast.classList.add('show');
        
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }

    // Helper: Get CSRF token from cookies
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

    // Helper: Escape HTML to prevent XSS
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
});

// Legacy support for bookmark button on post detail page
document.addEventListener('DOMContentLoaded', function() {
    const bookmarkBtn = document.getElementById('bookmark-btn');

    if (bookmarkBtn) {
        bookmarkBtn.addEventListener('click', function() {
            const postSlug = this.dataset.postSlug;
            const icon = this.querySelector('i');
            const isCurrentlyBookmarked = this.classList.contains('bookmarked');

            // Optimistic UI Update
            this.classList.toggle('bookmarked');
            if (isCurrentlyBookmarked) {
                icon.classList.remove('fas');
                icon.classList.add('far');
            } else {
                icon.classList.remove('far');
                icon.classList.add('fas');
            }

            // Determine action
            const action = isCurrentlyBookmarked ? 'remove' : 'add';

            // Send Request to Backend
            fetch(`/post/${postSlug}/bookmark/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: `action=${action}`
            })
            .then(response => {
                if (response.status === 403 || response.status === 401) {
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
                    toggleBookmarkUI(bookmarkBtn, icon, !isCurrentlyBookmarked);
                }
            });
        });
    }

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
});