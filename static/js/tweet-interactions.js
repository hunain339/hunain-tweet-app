document.addEventListener('DOMContentLoaded', () => {
    // ── Like Buttons (works on both feed cards and detail page) ──
    const likeButtons = document.querySelectorAll('.like-btn');

    likeButtons.forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            e.stopPropagation();

            const tweetId = btn.dataset.tweetId;
            if (!tweetId) return;

            const csrfToken =
                btn.dataset.csrf ||
                document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
                getCookie('csrftoken') ||
                '';

            // Optimistic visual feedback
            btn.style.opacity = '0.6';
            btn.style.pointerEvents = 'none';

            try {
                const response = await fetch(`/tweet/${tweetId}/like/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    const liked = data.liked;
                    const count = data.count ?? data.like_count ?? 0;

                    // Update data attribute
                    btn.dataset.liked = liked ? 'true' : 'false';

                    // Toggle .liked class (for detail page styling)
                    btn.classList.toggle('liked', liked);

                    // Update text-based heart icon (feed cards)
                    const heartIcon = btn.querySelector('.heart-icon');
                    if (heartIcon) {
                        heartIcon.textContent = liked ? '♥' : '♡';
                    }

                    // Update SVG-based heart icon (detail page)
                    const svgHeart = btn.querySelector('svg');
                    if (svgHeart && !heartIcon) {
                        svgHeart.setAttribute('fill', liked ? 'currentColor' : 'none');
                    }

                    // Update like count
                    const countSpan = btn.querySelector('.like-count');
                    if (countSpan) countSpan.textContent = count;

                    // Also update the stats row on detail page if present
                    updateDetailPageStats(tweetId, count);

                    // Pulse animation
                    btn.style.transform = 'scale(1.15)';
                    setTimeout(() => {
                        btn.style.transform = 'scale(1)';
                    }, 150);
                } else {
                    console.error('Like action failed:', response.status);
                }
            } catch (err) {
                console.error('Like error:', err);
            } finally {
                btn.style.opacity = '1';
                btn.style.pointerEvents = '';
            }
        });
    });

    // ── Async Comment Submission ──
    const commentForms = document.querySelectorAll('.quick-comment-form');

    commentForms.forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const tweetId = form.dataset.tweetId;
            const csrfToken =
                form.dataset.csrf ||
                form.querySelector('[name=csrfmiddlewaretoken]')?.value ||
                getCookie('csrftoken') ||
                '';

            const formData = new FormData(form);
            const text = formData.get('text')?.trim();
            if (!text) return;

            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.style.opacity = '0.6';
            }

            try {
                const response = await fetch(`/tweet/${tweetId}/comment/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: formData
                });

                if (response.ok) {
                    const data = await response.json();
                    if (data.success) {
                        // Append new comment to the list
                        const commentList = document.getElementById(`comment-list-${tweetId}`);
                        if (commentList) {
                            const emptyMsg = commentList.querySelector('.text-muted.text-center, .opacity-50');
                            if (emptyMsg) emptyMsg.remove();

                            const commentEl = document.createElement('div');
                            commentEl.className = 'mb-3 d-flex gap-2 animate-fade-in';
                            commentEl.innerHTML = `
                                <div class="flex-shrink-0">
                                    <div class="avatar-h" style="width: 28px; height: 28px; font-size: 0.75rem;">
                                        ${data.username.charAt(0).toUpperCase()}
                                    </div>
                                </div>
                                <div class="flex-grow-1">
                                    <div class="mb-1">
                                        <span class="text-primary fw-bold small">@${data.username}</span>
                                        <span class="text-muted small">• just now</span>
                                    </div>
                                    <p class="text-white-50 small mb-2">${escapeHtml(data.text)}</p>
                                </div>
                            `;
                            commentList.appendChild(commentEl);
                        }

                        // Update comment count badges
                        const countBadge = document.querySelector(`#tweet-${tweetId} .comment-count`);
                        if (countBadge) countBadge.textContent = data.count;

                        const detailCountBadge = document.querySelector('.comment-count-display');
                        if (detailCountBadge) detailCountBadge.textContent = data.count;

                        // Clear input
                        form.reset();
                    }
                } else {
                    console.error('Comment submission failed:', response.status);
                }
            } catch (err) {
                console.error('Comment error:', err);
            } finally {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.style.opacity = '1';
                }
            }
        });
    });

    // ── Helper: Update detail page stats row ──
    function updateDetailPageStats(tweetId, likeCount) {
        // Find the stats row on detail page and update Likes stat
        const statItems = document.querySelectorAll('.stat-item');
        statItems.forEach(item => {
            const label = item.querySelector('.stat-label');
            if (label && label.textContent.trim() === 'Likes') {
                const value = item.querySelector('.stat-value');
                if (value) value.textContent = likeCount;
            }
        });
    }

    // ── Helper: Get CSRF cookie ──
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

    // ── Helper: Escape HTML to prevent XSS in injected content ──
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.appendChild(document.createTextNode(text));
        return div.innerHTML;
    }
});
