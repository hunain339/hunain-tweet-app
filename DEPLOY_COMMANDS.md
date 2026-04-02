# QUICK COMMAND REFERENCE - Deploy Now!

## Copy & Paste These Commands (1 minute total)

```bash
# Command 1: Stage all changes
git add .

# Command 2: Create commit
git commit -m "Fix: Bad request error - Vercel config and ALLOWED_HOSTS updated"

# Command 3: Push to GitHub
git push origin main
```

That's it! Vercel will automatically:
1. Detect the push
2. Install dependencies
3. Run database migrations
4. Collect static files
5. Deploy your app

## Monitor Deployment

Go to: **https://vercel.com/hunain339/hunain-tweet-app/deployments**

Wait for green checkmark ✅ (usually 3-5 minutes)

## Test Your App

Once deployed, visit: **https://hunain-tweet-app.vercel.app/**

Should work perfectly now! 🎉

---

## What Was Fixed

✅ ALLOWED_HOSTS - Now includes hunain-tweet-app.vercel.app
✅ API Handler - Created api/index.py for Vercel routing
✅ vercel.json - Updated routing configuration
✅ Security - Enhanced SSL and cookie settings

## Files Changed
- hunain_project/settings.py (ALLOWED_HOSTS + security)
- vercel.json (routing + build config)
- api/index.py (NEW - Vercel handler)
- build.sh (build script)

