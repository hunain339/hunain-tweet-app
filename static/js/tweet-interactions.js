document.addEventListener('DOMContentLoaded', () => {
    const likeButtons = document.querySelectorAll('.like-btn');
    
    likeButtons.forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            const tweetId = btn.dataset.tweetId;
            const isLiked = btn.dataset.liked === 'true';
            
            try {
                const response = await fetch(`/tweet/${tweetId}/like/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || getCookie('csrftoken') || '',
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });
                
                if (response.ok) {
                    const data = await response.json();
                    btn.dataset.liked = data.liked ? 'true' : 'false';
                    const heartIcon = btn.querySelector('.heart-icon');
                    if (heartIcon) heartIcon.textContent = data.liked ? '♥️' : '♡';
                    const countSpan = btn.querySelector('.like-count');
                    if (countSpan) countSpan.textContent = data.count || data.like_count;
                } else {
                    console.error('Like action failed');
                }
            } catch (err) {
                console.error('Error:', err);
            }
        });
    });

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
