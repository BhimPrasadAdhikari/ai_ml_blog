document.addEventListener('DOMContentLoaded', function(){
    const postSlug = window.postSlug || '{{post.slug}}';
    const annotationLayer = document.getElementById('annotation-layer');
    const annotationForm = document.getElementById('annotation-form');
    const selectedTextDiv = document.getElementById('selected-text');
    const annotationContent = document.getElementById('annotation-content');
    const annotationPublic = document.getElementById('annotation-public');
    const submitBtn = document.getElementById('submit-annotation');
    const cancelBtn = document.getElementById('cancel-annotation');
    const annotationList = document.getElementById('annotations-list');

    let currentSelection = '';

    //Highlight and select text in post content
    const postContent = document.querySelector('.post-content');
    if(postContent && annotationForm){
        postContent.addEventListener('mouseup', function(e){
            const selection = window.getSelection();
            const text = selection.toString().trim();
            if(text.length > 0){
                currentSelection = text;
                selectedTextDiv.textContent = text;
                annotationForm.style.display = 'block';
                annotationContent.value = '';
                annotationContent.focus();
            }
        })
    }

    // Cancel annotation 
    if(cancelBtn) {
        cancelBtn.addEventListener('click', function(){
            annotationForm.style.display = 'none';
            selectedTextDiv.textContent = '';
            annotationContent.value = '';
            currentSelection = ''; 
        })
    }

    //submit annotation 
    if(submitBtn) {
        submitBtn.addEventListener('click', function(){
            const content = annotationContent.value.trim();
            const isPublic = annotationPublic.checked;
            if (!currentSelection || !content){
                alert('Please annotate some text and add your question or insights. ');
                return;
            }
            fetch(`/post/${postSlug}/annotations/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: new URLSearchParams({
                    selected_text: currentSelection,
                    content: content,
                    is_public: isPublic

                })
            })
            .then(response=>response.json())
            .then(data => {
                if (data.status === 'success' || data.result === 'success') {
                    annotationForm.style.display = 'none';
                    selectedTextDiv.textContent = '';
                    annotationContent.value = '';
                    currentSelection = '';
                    loadAnnotations();
                } else {
                    alert(data.message || 'Failed to add annotation.');
                }
            });

        });
    }

    //load and display annotations
    function loadAnnotations(){
        fetch(`/post/${postSlug}/annotations/`)
            .then(response=>response.json())
            .then(data => {
                annotationList.innerHTML = '';
                if(data.annotations && data.annotations.length > 0){
                    console.log(data.annotations);
                    data.annotations.forEach(ann => {
                        const isPostAuthor = window.currentUserEmail === window.postAuthorEmail;
                        const isOwner = ann.user === window.currentUsername;
                        const isPublic = ann.is_public;
                        const isResolved = ann.status === 'resolved';

                        let canShow = false;
                        if(isPostAuthor && isPublic) {
                            canShow = true;
                        } else if (isOwner && !isPublic){
                            canShow = true;
                        } else if (isOwner && isPublic && isResolved) {
                            canShow = true;
                        } else if (!isOwner && isPublic && isResolved) {
                            canShow = true;
                        }

                    if (canShow) { 
                        const annDiv = document.createElement('div');
                        annDiv.className = 'annotation-item';
                        annDiv.innerHTML = `
                            <div>
                                <strong>${ann.user || 'Anonymous'} </strong>
                                ${ann.is_public ? '<span> Public </span>':'<span> Private </span>' }
                                ${ann.status === 'resolved' ? '<span> Resolved </span>':'' }
                            </div>
                            <div><em>${ann.selected_text}</em></div>
                            <div>${ann.content}</div>
                            ${ann.status !== 'resolved' && isPostAuthor ? `<button data-resolve="${ann.id}">Mark as resolved`: ''}
                        `;
                        annotationList.appendChild(annDiv);

                        //Add resolve button handler
                        const resolveBtn = annDiv.querySelector('[data-resolve]');
                        if(resolveBtn) {
                            resolveBtn.addEventListener('click', function() {
                                fetch(`/post/${postSlug}/annotations/${ann.id}/resolve/`, {
                                    method: 'POST',
                                    headers: {
                                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                                    }
                                })
                                .then(response => response.json())
                                .then(res => {
                                    if (res.status === 'success') {
                                        loadAnnotations();
                                    } else {
                                        alert(res.message || 'Failed to resolve annotation.');
                                    }
                                });
                            });
                        } 
                    }
                    });
                } else {
                    annotationList.innerHTML = '<div>No annotions yet. Highlight text in the post to add one! </div>';
                }
            });
    }

    //initial load
    loadAnnotations();

})