AJAX Interactions & CSRF Strategy
--------------------------------

Recommendations
- Use Django's built-in CSRF middleware. For AJAX, include CSRF token in `X-CSRFToken` header.
- Frontend (vanilla JS or fetch): read CSRF token from cookie `csrftoken` and include in requests.
- For long-polling/Realtime endpoints, use secure WebSocket auth via signed tokens.

Example (fetch):

    fetch('/api/tweets/', {
      method: 'POST',
      headers: { 'X-CSRFToken': getCookie('csrftoken'), 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })

Notes
- Ensure `SESSION_COOKIE_SECURE` and `CSRF_COOKIE_SECURE` are set in production.
