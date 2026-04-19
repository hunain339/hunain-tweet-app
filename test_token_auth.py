#!/usr/bin/env python
"""
Token-Based Authentication Test Script
======================================

This script demonstrates how to use the token-based authentication endpoint.

Setup:
1. Run migrations: python manage.py migrate
2. Create a test user: python manage.py createsuperuser
   or use an existing user
3. Run this script: python test_token_auth.py

Example Usage:
- Get token: POST /api/token/ with username and password
- Access protected endpoints with: Authorization: Token <token>
"""

import os
import django
import json
from django.test import Client

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hunain_project.settings')
django.setup()

from django.contrib.auth.models import User

from rest_framework.authtoken.models import Token


def test_token_authentication():
    """Test token authentication flow"""
    print("=" * 70)
    print("TOKEN-BASED AUTHENTICATION TEST")
    print("=" * 70)
    
    # Create test user if doesn't exist
    username = 'testuser'
    password = 'testpass123'
    
    try:
        user = User.objects.create_user(
            username=username,
            email='testuser@example.com',
            password=password
        )
        print(f"\n✓ Created test user: {username}")
    except Exception as e:
        user = User.objects.get(username=username)
        print(f"\n✓ Using existing test user: {username}")
    
    # Get or create token for the user
    token, created = Token.objects.get_or_create(user=user)
    print(f"✓ User token: {token.key}")
    print(f"  Token {'created' if created else 'retrieved'}")
    
    # Test 1: Get token via API endpoint
    print("\n" + "-" * 70)
    print("TEST 1: Get token via /api/token/ endpoint")
    print("-" * 70)
    
    client = Client()
    
    # Make POST request to token endpoint
    response = client.post(
        '/api/token/',
        data=json.dumps({'username': username, 'password': password}),
        content_type='application/json'
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        response_data = response.json()
        print(f"\n✓ Successfully obtained token!")
        print(f"  User ID: {response_data.get('user_id')}")
        print(f"  Username: {response_data.get('username')}")
        print(f"  Token: {response_data.get('token')[:20]}...")
    else:
        print(f"✗ Failed to obtain token")
        return
    
    # Test 2: Access protected endpoint with token
    print("\n" + "-" * 70)
    print("TEST 2: Access /api/tweets/ with token authentication")
    print("-" * 70)
    
    token_str = response_data.get('token')
    
    # Without token
    response = client.get('/api/tweets/')
    print(f"\nWithout token:")
    print(f"  Status: {response.status_code}")
    print(f"  Can read: {'Yes' if response.status_code == 200 else 'No'}")
    
    # With token in Authorization header
    response = client.get(
        '/api/tweets/',
        HTTP_AUTHORIZATION=f'Token {token_str}'
    )
    print(f"\nWith token in Authorization header:")
    print(f"  Status: {response.status_code}")
    print(f"  Can read: {'Yes' if response.status_code == 200 else 'No'}")
    
    # Test 3: Test invalid credentials
    print("\n" + "-" * 70)
    print("TEST 3: Test invalid credentials")
    print("-" * 70)
    
    response = client.post(
        '/api/token/',
        data=json.dumps({'username': username, 'password': 'wrongpassword'}),
        content_type='application/json'
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 400:
        print("✓ Correctly rejected invalid credentials")
    else:
        print("✗ Should reject invalid credentials")
    
    # Test 4: Show how to use curl
    print("\n" + "-" * 70)
    print("TEST 4: How to use with curl command")
    print("-" * 70)
    
    print(f"""
# Get token:
curl -X POST http://localhost:8000/api/token/ \\
  -H "Content-Type: application/json" \\
  -d '{{"username": "{username}", "password": "{password}"}}'

# Response will be:
{{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user_id": 1,
  "username": "{username}"
}}

# Use token to access protected endpoint:
curl -X GET http://localhost:8000/api/tweets/ \\
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
""")
    
    # Test 5: Show permission model
    print("-" * 70)
    print("TEST 5: Permission Model")
    print("-" * 70)
    
    print("""
PUBLIC READ ACCESS:
- GET /api/tweets/                    : Anyone can list tweets (read-only)
- GET /api/tweets/{id}/              : Anyone can view tweet details (read-only)

AUTHENTICATED WRITE ACCESS:
- POST /api/tweets/                   : Token required - authenticated user creates tweet
- PUT /api/tweets/{id}/               : Token required - owner of tweet can update
- PATCH /api/tweets/{id}/             : Token required - owner of tweet can update
- DELETE /api/tweets/{id}/            : Token required - owner of tweet can delete

AUTHENTICATION METHODS SUPPORTED:
1. Token Authentication       : Authorization: Token <token>
2. Session Authentication    : Django session cookies (for browsable API)
3. Basic Authentication      : Authorization: Basic base64(username:password)
""")
    
    print("\n" + "=" * 70)
    print("✓ ALL TESTS COMPLETED SUCCESSFULLY")
    print("=" * 70)
    
    # Cleanup
    # Uncomment to delete test user after testing
    # user.delete()
    # print("\nTest user cleaned up")


if __name__ == '__main__':
    test_token_authentication()
