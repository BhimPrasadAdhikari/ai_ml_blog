document.addEventListener('DOMContentLoaded', function() {
    const qnaList = document.getElementById('qna-list');
    const qnaForm = document.getElementById('qna-form');
    const qnaQuestion = document.getElementById('qna-question');
    const qnaSubmit = document.getElementById('qna-submit');
    const postSlug = window.postSlug;
    const currentUsername = window.currentUsername;
    const postAuthorname = window.postAuthorname;

    function loadQnA() {
        fetch(`/post/${postSlug}/qna/`)
            .then(response => response.json())
            .then(data => {
                if (data.qnas && data.qnas.length > 0) {
                    qnaList.innerHTML = ''; 
                    
                    data.qnas.forEach(q => {
                        const qDiv = document.createElement('div');
                        qDiv.className = 'qna-item';
                        qDiv.id = `qna-item-${q.id}`;
                        
                        const isAsker = currentUsername === q.user;
                        const isAuthor = currentUsername === postAuthorname;
                        
                        // Generate Action Buttons
                        let actions = '';
                        if (isAsker) {
                            actions += `<button class="btn-link btn-sm edit-qna-btn" data-qid="${q.id}">Edit</button>`;
                        }
                        if (isAsker || isAuthor) {
                            actions += `<button class="btn-link btn-sm text-danger delete-qna-btn" data-qid="${q.id}">Delete</button>`;
                        }

                        qDiv.innerHTML = `
                            <div class="qna-header d-flex justify-content-between align-items-start">
                                <div>
                                    <strong>${q.user || 'Anonymous'}</strong> asked:
                                </div>
                                <div class="qna-actions">
                                    ${actions}
                                </div>
                            </div>
                            
                            <div class="mt-1 qna-question-text" id="question-text-${q.id}">${q.question}</div>
                            
                            <div class="mt-1 qna-edit-form" id="edit-form-${q.id}" style="display:none;">
                                <div class="input-group">
                                    <input type="text" class="form-control form-control-sm" id="edit-input-${q.id}" value="${q.question}">
                                    <button class="btn btn-sm btn-success save-edit-btn" data-qid="${q.id}">Save</button>
                                    <button class="btn btn-sm btn-secondary cancel-edit-btn" data-qid="${q.id}">Cancel</button>
                                </div>
                            </div>

                            <div class="mt-2">
                                ${q.is_answered ? 
                                    `<div class="qna-answer">
                                        <strong>Author:</strong> ${q.answer}
                                     </div>` :
                                    (currentUsername === postAuthorname ?
                                        `<textarea rows="2" class="qna-answer form-control" data-qid="${q.id}" placeholder="Write your answer..."></textarea>
                                         <button class="qna-answer-btn btn btn-sm btn-success mt-2" data-qid="${q.id}">Submit Answer</button>`
                                        : '<p class="text-muted"><em>Awaiting author response...</em></p>')}
                            </div>
                        `;
                        qnaList.appendChild(qDiv);
                    });

                    attachListeners();
                } else {
                    qnaList.innerHTML = '<p class="text-muted">No questions yet. Be the first to ask!</p>';
                }
            });
    }

    function attachListeners() {
        // Answer logic (Existing)
        document.querySelectorAll('.qna-answer-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const qid = this.getAttribute('data-qid');
                const answer = document.querySelector(`.qna-answer[data-qid="${qid}"]`).value;
                
                fetch(`/post/${postSlug}/qna/${qid}/answer/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    body: new URLSearchParams({ answer: answer })
                })
                .then(response => response.json())
                .then(res => {
                    if (res.status === 'success') loadQnA();
                    else alert(res.message || 'Failed to submit answer.');
                });
            });
        });

        // DELETE Logic
        document.querySelectorAll('.delete-qna-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                if(!confirm("Are you sure you want to delete this question?")) return;
                const qid = this.getAttribute('data-qid');
                
                fetch(`/post/${postSlug}/qna/${qid}/delete/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    }
                })
                .then(res => res.json())
                .then(data => {
                    if (data.status === 'success') loadQnA();
                    else alert(data.message);
                });
            });
        });

        // EDIT Toggle Logic
        document.querySelectorAll('.edit-qna-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const qid = this.getAttribute('data-qid');
                document.getElementById(`question-text-${qid}`).style.display = 'none';
                document.getElementById(`edit-form-${qid}`).style.display = 'block';
            });
        });

        // CANCEL Edit Logic
        document.querySelectorAll('.cancel-edit-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const qid = this.getAttribute('data-qid');
                document.getElementById(`question-text-${qid}`).style.display = 'block';
                document.getElementById(`edit-form-${qid}`).style.display = 'none';
            });
        });

        // SAVE Edit Logic
        document.querySelectorAll('.save-edit-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const qid = this.getAttribute('data-qid');
                const newQuestion = document.getElementById(`edit-input-${qid}`).value;
                
                fetch(`/post/${postSlug}/qna/${qid}/edit/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    body: new URLSearchParams({ question: newQuestion })
                })
                .then(res => res.json())
                .then(data => {
                    if (data.status === 'success') loadQnA();
                    else alert(data.message);
                });
            });
        });
    }

    if (qnaSubmit) {
        qnaSubmit.addEventListener('click', function() {
            const question = qnaQuestion.value.trim();
            if (!question) {
                alert('Please enter a question.');
                return;
            }
            fetch(`/post/${postSlug}/qna/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: new URLSearchParams({ question: question })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    qnaQuestion.value = '';
                    loadQnA();
                } else {
                    alert(data.message || 'Failed to submit question.');
                }
            });
        });
    }

    loadQnA();
});