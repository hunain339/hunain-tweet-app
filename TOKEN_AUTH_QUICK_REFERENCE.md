# Token Authentication Quick Reference

## Get Token
```bash
POST /api/token/
Content-Type: application/json

{
    "username": "your_username",
    "password": "your_password"
}
```

**Response:**
```json
{
    "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
    "user_id": 1,
    "username": "your_username"
}
```

## Use Token in Requests
```bash
GET /api/tweets/
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

## Public Endpoints (No Auth Required)
```
GET    /api/tweets/           # List tweets
GET    /api/tweets/{id}/      # View tweet
GET    /api/tweets/?search=q  # Search tweets
```

## Protected Endpoints (Token Required)
```
POST   /api/tweets/           # Create tweet (auth user)
PUT    /api/tweets/{id}/      # Update tweet (owner only)
PATCH  /api/tweets/{id}/      # Partial update (owner only)
DELETE /api/tweets/{id}/      # Delete tweet (owner only)
POST   /api/tweets/{id}/like/ # Like tweet (auth user)
```

## Response Codes
- `200 OK` - Request successful
- `201 Created` - Resource created (POST)
- `400 Bad Request` - Invalid credentials or malformed request
- `401 Unauthorized` - Missing or invalid token
- `403 Forbidden` - Authenticated but not authorized for action
- `404 Not Found` - Resource not found

## Python Example
```python
import requests

# 1. Get token
response = requests.post('http://localhost:8000/api/token/', json={
    'username': 'your_username',
    'password': 'your_password'
})
token = response.json()['token']

# 2. Use token to create tweet
headers = {'Authorization': f'Token {token}'}
response = requests.post('http://localhost:8000/api/tweets/', 
    headers=headers,
    json={'text': 'Hello World!'}
)
print(response.json())
```

## JavaScript Example
```javascript
// 1. Get token
const tokenResponse = await fetch('http://localhost:8000/api/token/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        username: 'your_username',
        password: 'your_password'
    })
});
const { token } = await tokenResponse.json();

// 2. Use token to fetch tweets
const tweetsResponse = await fetch('http://localhost:8000/api/tweets/', {
    headers: { 'Authorization': `Token ${token}` }
});
const tweets = await tweetsResponse.json();
```

## cURL Examples
```bash
# Get token
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"pass"}'

# List tweets (no auth)
curl http://localhost:8000/api/tweets/

# Create tweet (requires token)
curl -X POST http://localhost:8000/api/tweets/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello!"}'
```

## Environment Variables (from tests)
```python
# Test credentials
DEMO_USERNAME = 'testuser'
DEMO_PASSWORD = 'testpass123'
DEMO_TOKEN = '54e15f7702002d9c905048740df7e567ad68d490'
```

## Check Token in Database
```python
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

user = User.objects.get(username='testuser')
token = Token.objects.get(user=user)
print(f"Token: {token.key}")
```

## Regenerate Token
```python
from rest_framework.authtoken.models import Token

user = User.objects.get(username='testuser')
# Delete old token
Token.objects.filter(user=user).delete()
# New token created automatically on next login
```
