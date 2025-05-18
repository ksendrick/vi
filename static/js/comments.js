document.addEventListener('DOMContentLoaded', function () {
    const replyLinks = document.querySelectorAll('.reply-link');
    replyLinks.forEach(link => {
        link.addEventListener('click', function (event) {
            event.preventDefault();
            const commentId = this.dataset.commentId;
            const replyForm = document.getElementById(`reply-form-${commentId}`);
            replyForm.style.display = replyForm.style.display === 'none' ? 'block' : 'none';
        });
    });

    const viewRepliesButtons = document.querySelectorAll('.view-replies-button');
    viewRepliesButtons.forEach(button => {
        button.addEventListener('click', function () {
            const commentId = this.dataset.commentId;
            const repliesDiv = document.getElementById(`replies-${commentId}`);
            repliesDiv.style.display = repliesDiv.style.display === 'none' ? 'block' : 'none';
            this.textContent = repliesDiv.style.display === 'none' ? `Просмотреть ${comment.replies.count} ответ(ов)` : 'Скрыть ответы';
        });
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const replyLinks = document.querySelectorAll('.reply-link');

    replyLinks.forEach(link => {
        link.addEventListener('click', function (event) {
            event.preventDefault();
            const commentId = this.dataset.commentId;
            const replyForm = document.getElementById(`reply-form-${commentId}`);

            if (replyForm.style.display === 'none') {
                replyForm.style.display = 'block';
            } else {
                replyForm.style.display = 'none';
            }
        });
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const replyLinks = document.querySelectorAll('.reply-link');

    replyLinks.forEach(link => {
        link.addEventListener('click', function (event) {
            event.preventDefault();
            const commentId = this.dataset.commentId;
            const replyForm = document.getElementById(`reply-form-${commentId}`);

            // Toggle the display of the reply form
            if (replyForm.style.display === 'none') {
                replyForm.style.display = 'block';
            } else {
                replyForm.style.display = 'none';
            }
        });
    });
});


 function likeComment(commentId) {
            fetch(`/news/like_comment/${commentId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': '{{ csrf_token }}',
                    'Content-Type': 'application/json'
                },
            })
                .then(response => response.json())
                .then(data => {
                    document.getElementById(`likes-count-${commentId}`).textContent = data.likes_count;
                });
        }