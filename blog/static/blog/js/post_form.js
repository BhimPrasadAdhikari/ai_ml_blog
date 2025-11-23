// JS for post_form.html: EasyMDE, autosave, file input, form validation, slug generation

let easyMDE;
let autosaveTimeout;
const AUTOSAVE_DELAY = 2000; // 2 seconds
const DRAFT_KEY = window.draftKey || 'blog_post_draft_new';

document.addEventListener('DOMContentLoaded', function() {
    initializeEasyMDE();
    initializeAutosave();
    checkForDraft();
    initializeOtherFeatures();
});

function initializeEasyMDE() {
    const contentTextarea = document.getElementById(window.contentId);
    easyMDE = new EasyMDE({
        element: contentTextarea,
        spellChecker: false,
        autosave: { enabled: false },
        placeholder: window.easyMDEPlaceholder,
        toolbar: [
            'bold', 'italic', 'strikethrough', '|',
            'heading-1', 'heading-2', 'heading-3', '|',
            'code', 'quote', 'unordered-list', 'ordered-list', '|',
            'link', 'image', 'table', '|',
            'preview', 'side-by-side', 'fullscreen', '|',
            'guide'
        ],
        status: ['autosave', 'lines', 'words', 'cursor'],
        previewRender: function(plainText) {
            // FIX: Check for marked.parse (v4+) or fallback to marked (v3-)
            if (typeof marked !== 'undefined') {
                if (typeof marked.parse === 'function') {
                    return marked.parse(plainText);
                } else if (typeof marked === 'function') {
                    return marked(plainText);
                }
            }
            return plainText.replace(/\n/g, '<br>');
        },
        shortcuts: {
            drawTable: "Cmd-Alt-T",
            togglePreview: "Cmd-P",
            toggleSideBySide: "F9",
            toggleFullScreen: "F11"
        }
    });
    easyMDE.codemirror.on('change', function() {
        scheduleAutosave();
    });
}

function initializeAutosave() {
    const formFields = ['title', 'slug', 'summary', 'tags'];
    formFields.forEach(fieldName => {
        const field = document.getElementById('id_' + fieldName);
        if (field) {
            field.addEventListener('input', scheduleAutosave);
        }
    });
    const categoriesField = document.getElementById(window.categoriesId);
    const statusField = document.getElementById(window.statusId);
    if (categoriesField) categoriesField.addEventListener('change', scheduleAutosave);
    if (statusField) statusField.addEventListener('change', scheduleAutosave);
}

function scheduleAutosave() {
    clearTimeout(autosaveTimeout);
    showAutosaveIndicator('saving');
    autosaveTimeout = setTimeout(() => {
        saveDraft();
    }, AUTOSAVE_DELAY);
}

function saveDraft() {
    try {
        const draftData = {
            title: document.getElementById(window.titleId).value,
            slug: document.getElementById(window.slugId).value,
            summary: document.getElementById(window.summaryId).value,
            content: easyMDE.value(),
            tags: document.getElementById(window.tagsId).value,
            status: document.getElementById(window.statusId).value,
            categories: Array.from(document.getElementById(window.categoriesId).selectedOptions).map(option => option.value),
            timestamp: new Date().toISOString()
        };
        localStorage.setItem(DRAFT_KEY, JSON.stringify(draftData));
        showAutosaveIndicator('saved');
    } catch (error) {
        console.error('Failed to save draft:', error);
        showAutosaveIndicator('error');
    }
}

function checkForDraft() {
    try {
        const savedDraft = localStorage.getItem(DRAFT_KEY);
        if (savedDraft) {
            const draftData = JSON.parse(savedDraft);
            const draftAge = Date.now() - new Date(draftData.timestamp).getTime();
            const maxAge = 24 * 60 * 60 * 1000; // 24 hours
            if (draftAge < maxAge && isFormEmpty()) {
                document.getElementById('draft-recovery').classList.add('show');
            }
        }
    } catch (error) {
        console.error('Failed to check for draft:', error);
    }
}

function isFormEmpty() {
    const title = document.getElementById(window.titleId).value.trim();
    const content = document.getElementById(window.contentId).value.trim();
    return !title && !content;
}

function recoverDraft() {
    try {
        const savedDraft = localStorage.getItem(DRAFT_KEY);
        if (savedDraft) {
            const draftData = JSON.parse(savedDraft);
            document.getElementById(window.titleId).value = draftData.title || '';
            document.getElementById(window.slugId).value = draftData.slug || '';
            document.getElementById(window.summaryId).value = draftData.summary || '';
            document.getElementById(window.tagsId).value = draftData.tags || '';
            document.getElementById(window.statusId).value = draftData.status || 'draft';
            if (easyMDE) {
                easyMDE.value(draftData.content || '');
            }
            if (draftData.categories) {
                const categoriesField = document.getElementById(window.categoriesId);
                Array.from(categoriesField.options).forEach(option => {
                    option.selected = draftData.categories.includes(option.value);
                });
            }
            updateAllCharacterCounts();
            document.getElementById('draft-recovery').classList.remove('show');
        }
    } catch (error) {
        console.error('Failed to recover draft:', error);
    }
}

function dismissDraft() {
    localStorage.removeItem(DRAFT_KEY);
    document.getElementById('draft-recovery').classList.remove('show');
}

function showAutosaveIndicator(status) {
    const indicator = document.getElementById('autosave-indicator');
    const text = document.getElementById('autosave-text');
    indicator.classList.remove('saving', 'saved', 'error', 'show');
    indicator.classList.add(status, 'show');
    switch (status) {
        case 'saving':
            text.textContent = '💾 Saving draft...';
            break;
        case 'saved':
            text.textContent = '✅ Draft saved';
            break;
        case 'error':
            text.textContent = '❌ Save failed';
            break;
    }
    if (status !== 'saving') {
        setTimeout(() => {
            indicator.classList.remove('show');
        }, 2000);
    }
}

function initializeOtherFeatures() {
    updateCharacterCount(window.titleId, 'title-count', 200);
    updateCharacterCount(window.slugId, 'slug-count', 255);
    updateCharacterCount(window.summaryId, 'summary-count', 500);
    const titleField = document.getElementById(window.titleId);
    const slugField = document.getElementById(window.slugId);
    if (titleField && slugField) {
        titleField.addEventListener('input', function() {
            if (!slugField.value || slugField.dataset.autoGenerated === 'true') {
                const slug = this.value
                    .toLowerCase()
                    .replace(/[^a-z0-9\s-]/g, '')
                    .replace(/\s+/g, '-')
                    .replace(/-+/g, '-')
                    .trim('-');
                slugField.value = slug;
                slugField.dataset.autoGenerated = 'true';
                const slugCounter = document.getElementById('slug-count');
                if (slugCounter) {
                    slugCounter.textContent = `${slug.length} / 255 characters`;
                }
            }
        });
        slugField.addEventListener('input', function() {
            this.dataset.autoGenerated = 'false';
        });
    }
    const fileInput = document.getElementById(window.imageId);
    const fileInputContainer = document.getElementById('image-input');
    const fileInputLabel = fileInputContainer?.querySelector('.file-input-label span:last-child');
    if (fileInput && fileInputContainer && fileInputLabel) {
        fileInput.addEventListener('change', function() {
            if (this.files && this.files.length > 0) {
                const fileName = this.files[0].name;
                fileInputLabel.textContent = `Selected: ${fileName}`;
                fileInputContainer.classList.add('has-file');
            } else {
                fileInputLabel.textContent = 'Choose an image or drag and drop';
                fileInputContainer.classList.remove('has-file');
            }
        });
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            fileInputContainer.addEventListener(eventName, preventDefaults, false);
        });
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        ['dragenter', 'dragover'].forEach(eventName => {
            fileInputContainer.addEventListener(eventName, highlight, false);
        });
        ['dragleave', 'drop'].forEach(eventName => {
            fileInputContainer.addEventListener(eventName, unhighlight, false);
        });
        function highlight(e) {
            fileInputContainer.style.borderColor = '#667eea';
            fileInputContainer.style.backgroundColor = '#f0f2ff';
        }
        function unhighlight(e) {
            fileInputContainer.style.borderColor = '';
            fileInputContainer.style.backgroundColor = '';
        }
        fileInputContainer.addEventListener('drop', handleDrop, false);
        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files.length > 0) {
                fileInput.files = files;
                const event = new Event('change', { bubbles: true });
                fileInput.dispatchEvent(event);
            }
        }
    }
    document.getElementById('post-form').addEventListener('submit', function(e) {

        if (easyMDE) {
            easyMDE.codemirror.save();
        }
        const title = document.getElementById(window.titleId).value.trim();
        const content = easyMDE ? easyMDE.value().trim() : document.getElementById(window.contentId).value.trim();
        if (!title) {
            e.preventDefault();
            alert('Please enter a title for your post.');
            return;
        }
        if (!content) {
            e.preventDefault();
            alert('Please enter some content for your post.');
            return;
        }
        localStorage.removeItem(DRAFT_KEY);
        const submitBtn = this.querySelector('button[type="submit"]');
        submitBtn.innerHTML = '⏳ Publishing...';
        // submitBtn.disabled = true;
    });
}

function updateCharacterCount(inputId, countId, maxLength) {
    const input = document.getElementById(inputId);
    const counter = document.getElementById(countId);
    if (input && counter) {
        function updateCount() {
            const length = input.value.length;
            counter.textContent = `${length} / ${maxLength} characters`;
            counter.classList.remove('warning', 'error');
            if (length > maxLength * 0.9) {
                counter.classList.add('warning');
            }
            if (length > maxLength) {
                counter.classList.add('error');
            }
        }
        input.addEventListener('input', updateCount);
        updateCount();
    }
}

function updateAllCharacterCounts() {
    const fields = [
        { id: window.titleId, countId: 'title-count', max: 200 },
        { id: window.slugId, countId: 'slug-count', max: 255 },
        { id: window.summaryId, countId: 'summary-count', max: 500 }
    ];
    fields.forEach(field => {
        const input = document.getElementById(field.id);
        const counter = document.getElementById(field.countId);
        if (input && counter) {
            const length = input.value.length;
            counter.textContent = `${length} / ${field.max} characters`;
            counter.classList.remove('warning', 'error');
            if (length > field.max * 0.9) {
                counter.classList.add('warning');
            }
            if (length > field.max) {
                counter.classList.add('error');
            }
        }
    });
}

window.addEventListener('beforeunload', function(e) {
    if (easyMDE && easyMDE.value().trim()) {
        saveDraft();
    }
});

document.addEventListener('keydown', function(e) {
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        saveDraft();
        showAutosaveIndicator('saved');
    }
});