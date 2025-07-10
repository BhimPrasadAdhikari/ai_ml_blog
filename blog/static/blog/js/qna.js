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
                qnaList.innerHTML = '';
                if (data.qna && data.qna.length > 0) {
                    data.qna.forEach(q => {
                        const qDiv = document.createElement('div');
                        qDiv.className = 'qna-item';
                        qDiv.innerHTML = `
                            <div><strong>${q.user}</strong> asked:</div>
                            <div>${q.question}</div>
                            <div>
                                ${q.is_answered ? `<strong>Author:</strong> ${q.answer}` :
                                    (currentUsername === postAuthorname ?
                                        `<textarea rows="2" class="qna-answer" data-qid="${q.id}" placeholder="Write your answer..."></textarea>
                                         <button class="qna-answer-btn" data-qid="${q.id}">Submit Answer</button>`
                                        : '<em>Awaiting author response...</em>')}
                            </div>
                            <hr>
                        `;
                        qnaList.appendChild(qDiv);
                    });

                    // Add answer button listeners
                    document.querySelectorAll('.qna-answer-btn').forEach(btn => {
                        btn.addEventListener('click', function() {
                            const qid = this.getAttribute('data-qid');
                            const answer = document.querySelector(`.qna-answer[data-qid="${qid}"]`).value;
                            fetch(`/post/${postSlug}/qna/${qid}/answer/`, {
                                method: 'POST',
                                headers: {
                                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                                },
                                body: new URLSearchParams({ answer: answer })
                            })
                            .then(response => response.json())
                            .then(res => {
                                if (res.status === 'success') {
                                    loadQnA();
                                } else {
                                    alert(res.message || 'Failed to submit answer.');
                                }
                            });
                        });
                    });
                } else {
                    qnaList.innerHTML = '<div>No questions yet. Be the first to ask!</div>';
                }
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
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
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