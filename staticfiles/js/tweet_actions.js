/**
 * Tweetbar AJAX Actions
 * Handles optimistic UI for likes and subtle error notifications.
 */

(function() {
    'use strict';

    // Helper to get CSRF token from cookie if needed (standard Django way)
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

    // Toast Notification Helper
    function showToast(message, type = 'error') {
        const toastContainer = document.getElementById('toast-container');
        if (!toastContainer) return;

        const toastId = 'toast-' + Date.now();
        const bgClass = type === 'error' ? 'bg-danger' : 'bg-primary';
        
        const toastHTML = `
            <div id="${toastId}" class="toast align-items-center text-white ${bgClass} border-0 shadow-lg mb-2" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body fw-medium">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto shadow-none" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>
        `;

        toastContainer.insertAdjacentHTML('beforeend', toastHTML);
        const toastEl = document.getElementById(toastId);
        const toast = new bootstrap.Toast(toastEl, { delay: 4000 });
        toast.show();

        // Remove element after it's hidden
        toastEl.addEventListener('hidden.bs.toast', () => {
            toastEl.remove();
        });
    }

    // Event Delegation for Like Buttons
    document.addEventListener('click', async (e) => {
        const btn = e.target.closest('.like-btn');
        if (!btn) return;

        e.preventDefault();

        // 1. Extract data
        const { tweetId, likeUrl, csrf } = btn.dataset;
        const countEl = btn.querySelector('.like-count');
        const svgEl = btn.querySelector('svg');
        
        // 2. Optimistic Update
        const isLiked = btn.classList.contains('liked');
        const currentCount = parseInt(countEl.textContent) || 0;
        
        // Toggle UI state
        btn.classList.toggle('liked');
        countEl.textContent = isLiked ? Math.max(0, currentCount - 1) : currentCount + 1;
        
        if (!isLiked) {
            svgEl.setAttribute('fill', 'currentColor');
        } else {
            svgEl.setAttribute('fill', 'none');
        }

        // 3. Send AJAX Request
        try {
            const res = await fetch(likeUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrf || getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json'
                }
            });

            if (!res.ok) {
                throw new Error(`HTTP error! status: ${res.status}`);
            }

            const data = await res.json();
            
            if (data.success) {
                // Sync with server values just in case
                countEl.textContent = data.count;
                if (data.liked) {
                    btn.classList.add('liked');
                    svgEl.setAttribute('fill', 'currentColor');
                } else {
                    btn.classList.remove('liked');
                    svgEl.setAttribute('fill', 'none');
                }
            } else {
                throw new Error(data.error || 'Something went wrong');
            }
        } catch (err) {
            console.error('Like failed:', err);
            
            // 4. Rollback UI on Failure
            btn.classList.toggle('liked', isLiked);
            countEl.textContent = currentCount;
            svgEl.setAttribute('fill', isLiked ? 'currentColor' : 'none');
            
            // Show subtle error
            showToast('Unable to update like. Please try again.', 'error');
        }
    });

    // Optional: Event Delegation for Comments (Optimistic)
    document.addEventListener('submit', async (e) => {
        const form = e.target.closest('.quick-comment-form');
        if (!form) return;

        e.preventDefault();

        const input = form.querySelector('input[name="text"], textarea[name="text"]');
        const text = input.value.trim();
        if (!text) return;

        const { tweetId, csrf } = form.dataset;
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalBtnContent = submitBtn.innerHTML;

        // Visual feedback (disable button)
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';

        try {
            const formData = new FormData(form);
            const res = await fetch(form.action, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrf || getCookie('csrftoken'),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            });

            if (!res.ok) throw new Error('Failed to post comment');

            const data = await res.json();

            if (data.success) {
                // Update UI (Simple append for now, can be more complex)
                const list = document.getElementById(`comment-list-${tweetId}`);
                if (list) {
                    // Check for empty message and remove it
                    const emptyMsg = list.querySelector('.text-muted.text-center');
                    if (emptyMsg) emptyMsg.remove();

                    const newItem = document.createElement('div');
                    newItem.className = 'mb-3 d-flex gap-2 animate-fade-in';
                    newItem.innerHTML = `
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
                            <p class="text-white-50 small mb-2">${text}</p>
                        </div>
                    `;
                    list.prepend(newItem);
                }

                // Update comment count
                const countEls = document.querySelectorAll(`#tweet-${tweetId} .comment-count, #tweet-${tweetId} .comment-count-display`);
                countEls.forEach(el => {
                    el.textContent = data.count;
                });

                // Clear input
                input.value = '';
                
                // Clear parent_id if it was a reply
                const parentField = form.querySelector('input[name="parent_id"]');
                if (parentField) parentField.remove();
                
            } else {
                throw new Error(data.error || 'Failed to post comment');
            }
        } catch (err) {
            console.error('Comment failed:', err);
            showToast('Unable to post comment. Please try again.', 'error');
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalBtnContent;
        }
    });

})();
