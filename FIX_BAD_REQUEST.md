# FIX: Bad Request Error on Vercel Deployment

## Problem Identified
The deployment showed "bad request" error. Root causes were:
1. ALLOWED_HOSTS not properly configured
2. Missing Vercel API handler
3. Incorrect vercel.json routing configuration

## Solutions Applied ✅

### 1. Fixed ALLOWED_HOSTS in settings.py
- Changed from dynamic environment variable to hardcoded Vercel domain
- Added wildcard for all .vercel.app subdomains

### 2. Created Vercel API Handler
- New file: `api/index.py`
- Routes all requests to Django WSGI application
- Proper Python serverless function format

### 3. Updated vercel.json Configuration
- Added proper routing rules
- Set Python version to 3.11
- Configured function timeout (30s)
- Fixed build command with `--no-input` flags

### 4. Enhanced Security Settings
- Enabled SECURE_SSL_REDIRECT
- Enabled SESSION_COOKIE_SECURE
- Enabled CSRF_COOKIE_SECURE
- Added HSTS headers for security

## How to Re-deploy Now

### Step 1: Verify Environment Variables
Go to Vercel Dashboard → hunain-tweet-app → Settings → Environment Variables

Confirm these are set:
```
SECRET_KEY = [your-secret-key]
DEBUG = False
DATABASE_URL = [your-postgresql-url]
```

### Step 2: Push to GitHub
```bash
git add .
git commit -m "Fix: Bad request error - Update Vercel config and ALLOWED_HOSTS"
git push origin main
```

### Step 3: Monitor Deployment
- Go to Vercel Dashboard → Deployments
- Wait for deployment to complete (2-5 minutes)
- Should see green checkmark ✅

### Step 4: Test the App
Visit: https://hunain-tweet-app.vercel.app/

Should work without "bad request" error now!

## Files Changed
- ✅ `hunain_project/settings.py` - ALLOWED_HOSTS and security
- ✅ `vercel.json` - Routing and build config
- ✅ `api/index.py` - NEW - Vercel handler
- ✅ `build.sh` - Build script

## If Issues Persist

### Check Logs
1. Go to Vercel Dashboard
2. Click on latest deployment
3. View "Function Logs" tab
4. Look for Python error messages

### Common Issues

**Issue: Still showing bad request**
- Clear Vercel cache: Settings → Git → Disconnect and reconnect
- Force rebuild by pushing a change

**Issue: Database connection error**
- Ensure DATABASE_URL is set correctly in environment variables
- Verify PostgreSQL database is accessible from Vercel

**Issue: Static files not loading**
- WhiteNoise should handle this, but verify STATIC_ROOT is correct
- Check if CSS/images are loading (inspect page source)

## Contact Support
If issues persist:
1. Check Vercel deployment logs
2. Verify all environment variables are set
3. Try force rebuild by making a small code change and pushing

