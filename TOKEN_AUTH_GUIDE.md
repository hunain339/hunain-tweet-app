# Token-Based Authentication in Django REST Framework

## Overview

Your Django REST Framework API has been successfully configured with **stateless token-based authentication**. This replaces the session-based authentication dependency, making your API suitable for mobile applications, SPAs, and microservices that need independent authentication.

## What Was Configured

### 1. **Django REST Framework Setup** (`settings.py`)

✅ Added `rest_framework.authtoken` to `INSTALLED_APPS`
✅ Configured `TokenAuthentication` as the default authentication class
✅ Kept `SessionAuthentication` and `BasicAuthentication` as fallback options

```python
INSTALLED_APPS = [
    ...
    'rest_framework.authtoken',  # ← Added for token support
    ...
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',  # ← Token auth (primary)
        'rest_framework.authentication.SessionAuthentication',  # ← Session auth (fallback)
        'rest_framework.authentication.BasicAuthentication',   # ← Basic auth (fallback)
    ],
    # ... other settings
}
```

### 2. **Token Generation Endpoint** (`/api/token/`)

A new endpoint was created to exchange username and password credentials for an authentication token.

**Endpoint:** `POST /api/token/`

**Request:**
```json
{
    "username": "your_username",
    "password": "your_password"
}
```

**Response (Success - 200 OK):**
```json
{
    "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
    "user_id": 1,
    "username": "your_username"
}
```

**Response (Error - 400 Bad Request):**
```json
{
    "non_field_errors": ["Unable to log in with provided credentials."]
}
```

### 3. **Updated API Routes** (`hunain_project/urls.py`)

```python
urlpatterns = [
    ...
    path('api/token/', tweet_views.obtain_auth_token, name='obtain_auth_token'),  # ← Token endpoint
    path('api/', include(router.urls)),  # ← Protected API routes
    ...
]
```

### 4. **Database Migrations** (authtoken tables)

✅ Ran migrations to create Token model and associated tables
- `authtoken_token`: Stores tokens for authenticated users

```bash
python manage.py migrate
```

---

## How to Use Token Authentication

### Step 1: Get an Authentication Token

**Using cURL:**
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

**Using Python:**
```python
import requests

response = requests.post(
    'http://localhost:8000/api/token/',
    json={
        'username': 'your_username',
        'password': 'your_password'
    }
)

token = response.json()['token']
print(f"Your token: {token}")
```

**Using JavaScript/Fetch:**
```javascript
const response = await fetch('http://localhost:8000/api/token/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        username: 'your_username',
        password: 'your_password'
    })
});

const data = await response.json();
console.log(data.token);
```

### Step 2: Include Token in API Requests

Once you have a token, include it in the `Authorization` header for all protected requests.

**Using cURL:**
```bash
curl -X GET http://localhost:8000/api/tweets/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

**Using Python:**
```python
import requests

headers = {
    'Authorization': f'Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b'
}

response = requests.get('http://localhost:8000/api/tweets/', headers=headers)
tweets = response.json()
```

**Using JavaScript/Fetch:**
```javascript
const token = 'your_token_here';

const response = await fetch('http://localhost:8000/api/tweets/', {
    method: 'GET',
    headers: {
        'Authorization': `Token ${token}`
    }
});

const tweets = await response.json();
```

---

## API Permission Model

### Public Read Access
Anyone can read tweets without authentication:

| Method | Endpoint | Auth Required | Example |
|--------|----------|---|---------|
| GET | `/api/tweets/` | ❌ No | List all tweets |
| GET | `/api/tweets/{id}/` | ❌ No | View tweet details |
| GET | `/api/tweets/?search=query` | ❌ No | Search tweets |

### Authenticated Write Access
Only authenticated users can create/modify/delete tweets:

| Method | Endpoint | Auth Required | Permission |
|--------|----------|---|---------|
| POST | `/api/tweets/` | ✅ Token | Creates new tweet (auth user) |
| PUT | `/api/tweets/{id}/` | ✅ Token | Update tweet (owner only) |
| PATCH | `/api/tweets/{id}/` | ✅ Token | Partial update (owner only) |
| DELETE | `/api/tweets/{id}/` | ✅ Token | Delete tweet (owner only) |
| POST | `/api/tweets/{id}/like/` | ✅ Token | Like/unlike tweet (auth user) |

### Response Examples

**Unauthenticated GET (allowed):**
```bash
curl http://localhost:8000/api/tweets/
# Returns: 200 OK with tweet list
```

**Unauthenticated POST (denied):**
```bash
curl -X POST http://localhost:8000/api/tweets/ \
  -H "Content-Type: application/json" \
  -d '{"text": "New tweet"}'
# Returns: 403 Forbidden or 401 Unauthorized
```

**Authenticated POST (allowed):**
```bash
curl -X POST http://localhost:8000/api/tweets/ \
  -H "Authorization: Token your_token" \
  -H "Content-Type: application/json" \
  -d '{"text": "New tweet"}'
# Returns: 201 Created with tweet data
```

---

## Authentication Methods Supported

Your API supports multiple authentication methods for flexibility:

### 1. **Token Authentication** (Recommended for APIs)
- Best for: Mobile apps, SPAs, external services
- Format: `Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b`
- Stateless: Each request is independent

### 2. **Session Authentication** (Backward Compatible)
- Best for: Web browsers, form submissions
- Format: Uses Django session cookies
- Maintains session state on server

### 3. **Basic Authentication** (Simple but Less Secure)
- Best for: Development, testing
- Format: `Authorization: Basic base64(username:password)`
- ⚠️ Only use over HTTPS in production

---

## Token Management

### View User's Token
```python
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

user = User.objects.get(username='your_username')
token = Token.objects.get(user=user)
print(token.key)
```

### Regenerate Token
```python
from rest_framework.authtoken.models import Token

user = User.objects.get(username='your_username')
token = Token.objects.get(user=user)
token.delete()  # Delete old token

# New token will be auto-created on next login
```

### Create Token Manually
```python
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

user = User.objects.get(username='your_username')
token, created = Token.objects.get_or_create(user=user)
print(f"Token: {token.key} (created: {created})")
```

---

## Testing Your Implementation

Run the token authentication test:

```bash
python test_token_auth.py
```

This will:
1. Create a test user
2. Request a token
3. Verify public read access
4. Verify authenticated write permissions
5. Test invalid credentials
6. Display usage examples

---

## Security Best Practices

### ✅ DO:
- **Use HTTPS**: Always transmit tokens over encrypted connections
- **Store tokens securely**: Use secure storage mechanisms (httpOnly cookies, secure device storage)
- **Rotate tokens**: Regenerate tokens periodically or after password changes
- **Validate tokens**: DRF handles this automatically
- **Use short expiry**: Consider implementing token expiry (if needed)
- **Log token usage**: Monitor token activity for security

### ❌ DON'T:
- ⛔ Send tokens in URLs (use headers instead)
- ⛔ Store tokens in plain text
- ⛔ Log full tokens in application logs
- ⛔ Share tokens between users
- ⛔ Use tokens without HTTPS in production

---

## Advanced Configuration

### Token Expiry (Optional)

To implement token expiration, install and configure Django REST Framework Token Expiry:

```bash
pip install rest_framework-simplejwt
```

Or use a custom authentication class. Contact support for implementation details.

### Rate Limiting

Protect your `/api/token/` endpoint from brute force attacks:

```python
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='5/m')  # 5 attempts per minute
@api_view(['POST'])
def obtain_auth_token(request):
    ...
```

### Swagger/OpenAPI Documentation

Your token endpoint is automatically documented in the API schema:

```bash
http://localhost:8000/api/schema/
```

---

## Troubleshooting

### Issue: "Invalid token" error when accessing protected endpoints

**Solution:** Ensure the token is included in the Authorization header:
```bash
# Correct format
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b

# Incorrect formats (will fail):
Authorization: 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b  # Missing "Token"
Authroization: Token ...  # Typo in header name
Authorization token ...  # Wrong case
```

### Issue: "Invalid credentials" when getting token

**Solution:** Verify username and password are correct:
```bash
# Test with admin/superuser account if unsure
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin_password"}'
```

### Issue: Token works but permissions denied for POST/PUT/DELETE

**Solution:** The user must be authenticated. The token is valid, but your permissions class requires authentication:

```python
# This is already configured in your API
'DEFAULT_PERMISSION_CLASSES': [
    'rest_framework.permissions.IsAuthenticatedOrReadOnly'
]
```

---

## Migration from Session-Based to Token-Based

Your API now supports both session and token authentication. Existing session-based clients will continue to work while you migrate to token-based auth:

1. **Legacy clients** continue using session cookies
2. **New clients** use tokens via `/api/token/`
3. **Gradual migration** - no breaking changes

---

## API Contracts

### Token Response Schema
```json
{
    "token": "string (40 chars, hex)",
    "user_id": "integer",
    "username": "string"
}
```

### Error Response Schema
```json
{
    "non_field_errors": ["string (error message)"]
}
```

---

## Next Steps

1. ✅ Test the `/api/token/` endpoint with a test user
2. ✅ Update your frontend/mobile app to use token authentication
3. ✅ Remove session-based auth from protected endpoints (optional)
4. ✅ Implement token refresh/expiry logic if needed
5. ✅ Add rate limiting to token endpoint

---

## Reference

- [Django REST Framework TokenAuthentication](https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication)
- [Django REST Framework Permissions](https://www.django-rest-framework.org/api-guide/permissions/)
- [RFC 7235: HTTP Authentication](https://tools.ietf.org/html/rfc7235)

---

**Last Updated:** April 19, 2026
**Status:** ✅ Fully Implemented and Tested
