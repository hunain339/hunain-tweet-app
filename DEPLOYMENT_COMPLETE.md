# Tweetbar - Django Tweet Application
## Complete Deployment & Verification Guide

This is a comprehensive guide to verify, test, and deploy your Tweetbar Django application to Vercel.

---

## 📋 PROJECT OVERVIEW

**Application Name:** Tweetbar - A Twitter-like Social Platform
**Built With:** Django 6.0, Bootstrap 5.3, PostgreSQL/SQLite
**Features:** User Auth, Tweets, Comments, Likes, User Profiles, Search

---

## ✅ PRE-DEPLOYMENT VERIFICATION

### 1. Code Quality Check
```bash
# Run linting
flake8 --exclude=migrations --max-line-length=100

# Check for common issues
python manage.py check

# Verify migrations
python manage.py showmigrations
```

### 2. Database Integrity
```bash
# Backup current database (if applicable)
python manage.py dumpdata > backup.json

# Run all migrations
python manage.py migrate

# Create superuser if needed
python manage.py createsuperuser
```

### 3. Static Files
```bash
# Collect all static files
python manage.py collectstatic --noinput

# Verify files in staticfiles/ directory
ls -la staticfiles/
```

---

## 🧪 COMPREHENSIVE TESTING CHECKLIST

### SECTION 1: Authentication & Authorization
**Expected:** Users can register, login, and logout securely

#### Test Case 1.1: User Registration
- [ ] Navigate to `/tweet/register/`
- [ ] **Expected Result:** Registration form loads with:
  - Username field
  - Email field
  - Password field
  - Confirm Password field
  - Terms checkbox (if applicable)
- [ ] Fill in form with:
  - Username: `testuser123`
  - Email: `test@example.com`
  - Password: `SecurePass123!`
  - Confirm: `SecurePass123!`
- [ ] **Expected Result:** Form submits, success message displays, redirected to `/tweet/`

#### Test Case 1.2: Duplicate Username Prevention
- [ ] Try registering again with same username
- [ ] **Expected Result:** Error message: "A user with that username already exists."

#### Test Case 1.3: Password Validation
- [ ] Try registering with weak password (e.g., "123456")
- [ ] **Expected Result:** Error message about password strength
- [ ] Try mismatched passwords
- [ ] **Expected Result:** Error message: "The two password fields didn't match."

#### Test Case 1.4: User Login
- [ ] Navigate to `/account/login/`
- [ ] **Expected Result:** Login form displays
- [ ] Enter valid credentials from 1.1
- [ ] **Expected Result:** Login succeeds, redirected to `/tweet/`, logged-in navbar shows

#### Test Case 1.5: Invalid Login
- [ ] Enter wrong username or password
- [ ] **Expected Result:** Error message: "Please enter a correct username and password."

#### Test Case 1.6: Logout
- [ ] Click Logout button in navbar
- [ ] **Expected Result:** Logged out page displays, confirms successful logout
- [ ] Click "Return Home"
- [ ] **Expected Result:** Redirected to home, navbar shows "Login" and "Get Started" again

---

### SECTION 2: Homepage & Navigation
**Expected:** Users can navigate the application easily

#### Test Case 2.1: Homepage for Anonymous Users
- [ ] Visit `/` or `/tweet/`
- [ ] **Expected Result:**
  - Welcome message displays
  - "Get Started" button visible
  - "Sign In" button visible
  - Features section displays (Share Ideas, Engage & Like, Connect)
  - Navigation bar visible at top

#### Test Case 2.2: Homepage for Authenticated Users
- [ ] Login as test user
- [ ] Visit `/`
- [ ] **Expected Result:**
  - Welcome message displays
  - "Explore Feed" button visible
  - "Post a Tweet" button visible
  - User profile link shows in navbar with username
  - Logout button visible

#### Test Case 2.3: Navbar Search
- [ ] Type "test" in search bar
- [ ] Press Enter or wait for results
- [ ] **Expected Result:** Tweets containing "test" display or redirect to filtered view
- [ ] Click X to clear search
- [ ] **Expected Result:** All tweets display again

#### Test Case 2.4: Navbar Links
- [ ] Click Home link
- [ ] **Expected Result:** Navigate to home page
- [ ] Click Explore link
- [ ] **Expected Result:** Navigate to tweet feed
- [ ] Click username in navbar
- [ ] **Expected Result:** Navigate to user profile page

---

### SECTION 3: Tweet Creation & Management
**Expected:** Users can create, edit, and delete their tweets

#### Test Case 3.1: Create Tweet - Text Only
- [ ] Click "Post a Tweet" button
- [ ] **Expected Result:** Tweet creation form loads with:
  - Text area (max 240 characters)
  - Image upload field
  - "Post Tweet" button
  - "Cancel" button
- [ ] Enter text: "Hello Tweetbar! This is my first tweet."
- [ ] Click "Post Tweet"
- [ ] **Expected Result:**
  - Success message displays
  - Redirected to feed
  - Tweet appears at top with username, text, timestamp, like/comment counts

#### Test Case 3.2: Create Tweet - With Image
- [ ] Click "Post a Tweet"
- [ ] Enter text: "Check out this image!"
- [ ] Click image upload field
- [ ] **Expected Result:** File picker opens
- [ ] Select a valid image file (JPG, PNG, etc.)
- [ ] **Expected Result:** Filename displays in field
- [ ] Click "Post Tweet"
- [ ] **Expected Result:**
  - Tweet appears in feed with image displayed
  - Image is visible in tweet card

#### Test Case 3.3: Character Limit
- [ ] Click "Post a Tweet"
- [ ] Try entering 300 characters (exceeds 240 limit)
- [ ] **Expected Result:** Text field prevents input or shows warning

#### Test Case 3.4: Empty Tweet Prevention
- [ ] Click "Post a Tweet"
- [ ] Leave text empty
- [ ] Click "Post Tweet"
- [ ] **Expected Result:** Error message: "This field is required." or similar

#### Test Case 3.5: Edit Own Tweet
- [ ] In feed, find your tweet
- [ ] Click edit icon (pencil icon)
- [ ] **Expected Result:** Edit form loads with:
  - Pre-filled text
  - Current image displayed (if any)
- [ ] Change text to: "Updated tweet!"
- [ ] Click "Update Tweet"
- [ ] **Expected Result:**
  - Success message displays
  - Redirected to feed
  - Tweet shows updated text

#### Test Case 3.6: Cannot Edit Others' Tweets
- [ ] View another user's tweet in feed
- [ ] **Expected Result:** No edit icon visible for that tweet
- [ ] Try accessing edit URL directly: `/tweet/{id}/edit/`
- [ ] **Expected Result:** 404 error or permission denied

#### Test Case 3.7: Delete Tweet Confirmation
- [ ] Find your tweet in feed
- [ ] Click delete icon (trash icon)
- [ ] **Expected Result:** Confirmation page displays with:
  - Warning message
  - "Yes, Delete Tweet" button (red)
  - "No, Go Back" button
- [ ] Click "No, Go Back"
- [ ] **Expected Result:** Redirected back to feed, tweet still exists

#### Test Case 3.8: Delete Tweet Confirmation (Confirmed)
- [ ] Find your tweet
- [ ] Click delete icon
- [ ] Click "Yes, Delete Tweet"
- [ ] **Expected Result:**
  - Success message displays
  - Redirected to feed
  - Tweet no longer visible

---

### SECTION 4: Like Functionality
**Expected:** Users can like/unlike tweets and counts update correctly

#### Test Case 4.1: Like Tweet
- [ ] In feed, find any tweet
- [ ] Click heart icon
- [ ] **Expected Result:**
  - Heart becomes filled/highlighted (orange)
  - Like count increases by 1
  - Change persists on page refresh

#### Test Case 4.2: Unlike Tweet
- [ ] Click heart icon on tweet you just liked
- [ ] **Expected Result:**
  - Heart becomes unfilled/outline only
  - Like count decreases by 1

#### Test Case 4.3: Multiple Likes
- [ ] Like several different tweets
- [ ] **Expected Result:** Heart icon filled for each liked tweet
- [ ] Reload page
- [ ] **Expected Result:** All liked tweets still show filled hearts

#### Test Case 4.4: Like Count Accuracy
- [ ] Check like count on tweet
- [ ] Like from another user account (if available)
- [ ] **Expected Result:** Like count increments
- [ ] Refresh first user's view
- [ ] **Expected Result:** Updated like count visible

#### Test Case 4.5: Unauthenticated Like
- [ ] Logout
- [ ] Try clicking like icon
- [ ] **Expected Result:** Redirected to login or message to login first

---

### SECTION 5: Comments System
**Expected:** Users can comment on tweets and view all comments

#### Test Case 5.1: Add Comment
- [ ] In feed, find any tweet
- [ ] Scroll to bottom of tweet card
- [ ] **Expected Result:** Comment input box visible with placeholder "Write a reply..."
- [ ] Type comment: "Great tweet!"
- [ ] Click send button (arrow icon)
- [ ] **Expected Result:**
  - Comment appears in tweet's comments section
  - Comment shows your username and text
  - Success message may display

#### Test Case 5.2: Multiple Comments View
- [ ] Find a tweet with 2+ comments
- [ ] **Expected Result:**
  - First 3 comments display in preview
  - If >3 comments: "...and X more" text shows
  - Scrollable comment section

#### Test Case 5.3: Comment Count
- [ ] Note comment count on tweet (e.g., "5")
- [ ] Add a comment
- [ ] **Expected Result:** Comment count increases to 6
- [ ] Reload page
- [ ] **Expected Result:** Comment count still shows 6

#### Test Case 5.4: Comment Display
- [ ] Add comment: "@username Awesome content!"
- [ ] **Expected Result:**
  - Comment displays with your username in orange/primary color
  - Comment text displays correctly
  - Special characters preserved (@ mentions, emojis)

#### Test Case 5.5: Unauthenticated Comments
- [ ] Logout
- [ ] Try clicking in comment box or submitting
- [ ] **Expected Result:** Redirected to login or comment field disabled

---

### SECTION 6: User Profiles
**Expected:** User profiles display correct stats and tweets

#### Test Case 6.1: Profile Page Loads
- [ ] Click on any username in feed
- [ ] **Expected Result:** Profile page loads with:
  - Large avatar with first letter
  - Username displayed
  - Join date shown
  - Tweet count displayed
  - Like count displayed
  - User's tweets displayed in grid below

#### Test Case 6.2: Profile Stats Accuracy
- [ ] Count user's tweets manually in feed
- [ ] Check Tweet count on profile
- [ ] **Expected Result:** Numbers match
- [ ] Add a new tweet
- [ ] Refresh profile
- [ ] **Expected Result:** Tweet count increments by 1

#### Test Case 6.3: Like Count on Profile
- [ ] Check profile's like count
- [ ] Like several tweets from that user
- [ ] Refresh profile
- [ ] **Expected Result:** Like count increases
- [ ] Unlike one
- [ ] **Expected Result:** Like count decreases

#### Test Case 6.4: Own Profile Edit/Delete Buttons
- [ ] Navigate to your own profile
- [ ] **Expected Result:** Your tweets show edit and delete icons
- [ ] Click edit icon
- [ ] **Expected Result:** Edit page loads

#### Test Case 6.5: Others' Profiles No Edit Buttons
- [ ] Navigate to another user's profile
- [ ] **Expected Result:** No edit/delete icons visible on their tweets

#### Test Case 6.6: Profile Pagination
- [ ] Find a user with 10+ tweets
- [ ] Go to their profile
- [ ] **Expected Result:** Pagination controls visible at bottom
- [ ] Click "Next"
- [ ] **Expected Result:** Next page of tweets loads (tweets 11-20)

---

### SECTION 7: Search Functionality
**Expected:** Users can search tweets and users effectively

#### Test Case 7.1: Search by Tweet Text
- [ ] Click search bar in navbar
- [ ] Type: "hello"
- [ ] Press Enter
- [ ] **Expected Result:**
  - Results page loads
  - Only tweets containing "hello" display
  - Page title shows: 'Results for "hello"'

#### Test Case 7.2: Search by Username
- [ ] Type in search: "@testuser123" or username without @
- [ ] Press Enter
- [ ] **Expected Result:**
  - Tweets from that user display
  - May include tweets mentioning that user

#### Test Case 7.3: Clear Search
- [ ] Perform a search
- [ ] Click X button in search bar
- [ ] **Expected Result:**
  - Search cleared
  - All tweets display
  - Feed returns to normal

#### Test Case 7.4: No Results
- [ ] Search for non-existent text: "xyzabc123nonexistent"
- [ ] **Expected Result:**
  - "No tweets found" message displays
  - "Clear search" button available
  - No tweets in results

#### Test Case 7.5: Search Pagination
- [ ] Search for common term that returns 10+ results
- [ ] **Expected Result:** Pagination controls visible
- [ ] Click "Next"
- [ ] **Expected Result:** Next page of search results loads

#### Test Case 7.6: Persistent Search Query
- [ ] Search for "test"
- [ ] Go to page 2
- [ ] **Expected Result:** URL shows query parameter: `?q=test&page=2`
- [ ] Refresh page
- [ ] **Expected Result:** Same search results display

---

### SECTION 8: Responsive Design
**Expected:** App works well on all screen sizes

#### Test Case 8.1: Desktop (1920px)
- [ ] Open browser at 1920px width
- [ ] **Expected Result:**
  - 3-column tweet grid
  - Full navbar with all items
  - No horizontal scrolling
  - Content well-spaced

#### Test Case 8.2: Tablet (768px)
- [ ] Resize to 768px or use tablet device view
- [ ] **Expected Result:**
  - 2-column tweet grid
  - Navbar adapts (some items may stack)
  - Forms readable
  - Buttons clickable
  - No horizontal scrolling

#### Test Case 8.3: Mobile (375px)
- [ ] Resize to 375px or use mobile device view
- [ ] **Expected Result:**
  - 1-column tweet grid (full width)
  - Hamburger menu visible
  - All text readable
  - Buttons large enough to tap
  - No horizontal scrolling

#### Test Case 8.4: Mobile Navigation
- [ ] Open hamburger menu
- [ ] **Expected Result:**
  - Menu expands showing all links
  - Search bar visible
  - Logout button visible
- [ ] Click a link
- [ ] **Expected Result:** Menu closes, navigates to page

#### Test Case 8.5: Mobile Form
- [ ] On mobile, click "Post a Tweet"
- [ ] **Expected Result:**
  - Form displays full width
  - All fields visible
  - Keyboard doesn't cover input
  - Send button accessible

#### Test Case 8.6: Mobile Profile
- [ ] On mobile, view user profile
- [ ] **Expected Result:**
  - Profile header displays correctly
  - Stats (tweets, likes) centered
  - Tweets display in single column
  - Profile image scales appropriately

---

### SECTION 9: Error Handling & Edge Cases
**Expected:** App handles errors gracefully

#### Test Case 9.1: Invalid Tweet ID
- [ ] Try accessing invalid tweet: `/tweet/999999/edit/`
- [ ] **Expected Result:** 404 error page or redirected

#### Test Case 9.2: Invalid Username
- [ ] Try accessing invalid user: `/tweet/profile/nonexistentuser123/`
- [ ] **Expected Result:** 404 error or user not found message

#### Test Case 9.3: Invalid Page Number
- [ ] Go to feed and try accessing `/tweet/?page=999`
- [ ] **Expected Result:** Last page shows or error message

#### Test Case 9.4: Database Timeout
- [ ] Simulate slow database response (or check logs)
- [ ] **Expected Result:** App doesn't crash, timeout message or spinner

#### Test Case 9.5: Missing Image File
- [ ] Create tweet with image
- [ ] Delete image file from media folder
- [ ] Reload page
- [ ] **Expected Result:** Broken image handled gracefully (alt text shows)

---

### SECTION 10: UI/UX & Visual Design
**Expected:** App looks polished and professional

#### Test Case 10.1: Color Scheme
- [ ] **Expected Result:**
  - Dark theme applied (dark background)
  - Orange accent color (#FF6A00) used for highlights
  - White text on dark background
  - Consistent colors throughout

#### Test Case 10.2: Typography
- [ ] **Expected Result:**
  - Headings use "Outfit" font family
  - Body text uses "Inter" font family
  - Text sizes hierarchical and readable
  - Line height comfortable (1.4-1.6)

#### Test Case 10.3: Spacing & Layout
- [ ] **Expected Result:**
  - Consistent padding and margins
  - Whitespace not cramped
  - Content centered appropriately
  - Grid layouts aligned

#### Test Case 10.4: Button Interactions
- [ ] Hover over any button
- [ ] **Expected Result:**
  - Button changes color or has shadow effect
  - Cursor changes to pointer
  - Animation smooth (not jerky)
- [ ] Click button
- [ ] **Expected Result:** Button has active/pressed state

#### Test Case 10.5: Card Hover Effects
- [ ] Hover over tweet card
- [ ] **Expected Result:**
  - Card lifts up slightly (translate transform)
  - Shadow becomes darker
  - Border or glow effect appears
  - Animation smooth

#### Test Case 10.6: Forms & Inputs
- [ ] Click in text input
- [ ] **Expected Result:**
  - Focus state visible (border color change)
  - Glow effect appears
  - Cursor visible
- [ ] Type text
- [ ] **Expected Result:** Text appears, placeholder disappears

#### Test Case 10.7: Messages & Alerts
- [ ] Create tweet successfully
- [ ] **Expected Result:**
  - Success message appears (green)
  - Message is dismissible
  - Auto-hides after few seconds
- [ ] Try invalid form
- [ ] **Expected Result:**
  - Error message appears (red)
  - Error is clear and helpful

---

### SECTION 11: Security
**Expected:** App is secure against common attacks

#### Test Case 11.1: CSRF Protection
- [ ] Submit any form
- [ ] **Expected Result:** Request includes CSRF token
- [ ] Open DevTools → Network → Check form submission
- [ ] **Expected Result:** `csrfmiddlewaretoken` present

#### Test Case 11.2: Cannot Access Others' Tweets to Edit
- [ ] Login as user A
- [ ] Try accessing user B's tweet edit URL directly
- [ ] **Expected Result:** 404 or permission denied

#### Test Case 11.3: Cannot Delete Others' Tweets
- [ ] Try deleting another user's tweet via URL
- [ ] **Expected Result:** Permission denied or 404

#### Test Case 11.4: Authentication Required
- [ ] Logout
- [ ] Try accessing `/tweet/create/`
- [ ] **Expected Result:** Redirected to login page

#### Test Case 11.5: Password Security
- [ ] Register with password: "password123"
- [ ] **Expected Result:** Password accepted (meets requirements)
- [ ] Try logging in with wrong password
- [ ] **Expected Result:** Login fails, generic error (doesn't reveal if username exists)

#### Test Case 11.6: No SQL Injection
- [ ] In search bar, try: `' OR '1'='1`
- [ ] **Expected Result:** Treated as literal search, no error or exploit
- [ ] Check database logs
- [ ] **Expected Result:** No SQL errors

---

## 🚀 DEPLOYMENT TO VERCEL

### Phase 1: Pre-Deployment Setup

#### 1.1 Environment Variables
```bash
# Create .env file locally (already have .env.example)
cp .env.example .env
```

Edit `.env` with:
```
SECRET_KEY=your-secure-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,hunain-tweet-app.vercel.app
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

#### 1.2 Verify Settings
```bash
# Check Django settings
python manage.py check --deploy

# Expected: No errors (only warnings acceptable)
```

#### 1.3 Git Preparation
```bash
# Stage all changes
git add .

# Commit with clear message
git commit -m "Fix all issues, add testing guide, prepare for Vercel deployment"

# Verify files to be pushed
git status
```

### Phase 2: Vercel Configuration

#### 2.1 Connect to Vercel
1. Go to https://vercel.com
2. Click "Add New" → "Project"
3. Select your GitHub repository: `hunain339/hunain-tweet-app`
4. Click "Import"

#### 2.2 Set Environment Variables
In Vercel Dashboard:
1. Go to Settings → Environment Variables
2. Add each variable:
   - **Name:** `SECRET_KEY` → **Value:** (Generate new or use existing)
   - **Name:** `DEBUG` → **Value:** `False`
   - **Name:** `ALLOWED_HOSTS` → **Value:** `hunain-tweet-app.vercel.app`
   - **Name:** `DATABASE_URL` → **Value:** (PostgreSQL/Supabase connection string)

#### 2.3 Verify Build Settings
- Build Command: `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`
- Output Directory: `staticfiles`
- Runtime: Python 3.11

### Phase 3: Deploy

#### 3.1 Push to Main Branch
```bash
git push origin main
```

Vercel will automatically:
- Detect changes
- Start build process
- Run migrations
- Collect static files
- Deploy to URL: https://hunain-tweet-app.vercel.app

#### 3.2 Monitor Deployment
1. Go to Vercel Dashboard
2. Click on your project
3. Watch build logs for errors
4. Expected build time: 2-5 minutes

#### 3.3 Check Deployment Status
- Green checkmark: Deployment successful
- Red X: Deployment failed (check logs)

### Phase 4: Post-Deployment Testing

#### 4.1 Basic Health Check
```bash
curl https://hunain-tweet-app.vercel.app/
# Should return HTML, not error
```

#### 4.2 Run Full Testing Checklist
- [ ] Test all sections above on production URL
- [ ] Check console for JavaScript errors (F12)
- [ ] Verify static files load (CSS, images)
- [ ] Test database operations (create/read/update/delete)

#### 4.3 Monitor Initial Errors
- Check Vercel logs for first hour
- Monitor error tracking if available
- Test all critical user flows

---

## 🔧 TROUBLESHOOTING DEPLOYMENT ISSUES

### Issue 1: 400 Bad Request
**Error:** Page returns 400 Bad Request
**Cause:** CSRF or ALLOWED_HOSTS issue

**Solution:**
```bash
# Check ALLOWED_HOSTS in settings.py
# Must include: hunain-tweet-app.vercel.app

# Check CSRF_TRUSTED_ORIGINS
# Must include: https://*.vercel.app

# Verify in Vercel environment variables
```

### Issue 2: Static Files Not Loading
**Error:** CSS/images missing, site looks broken
**Cause:** collectstatic didn't run or static files misconfigured

**Solution:**
```bash
# Locally verify:
python manage.py collectstatic --noinput

# Check vercel.json buildCommand includes collectstatic

# Verify STATIC_ROOT and STATIC_URL in settings.py
```

### Issue 3: Database Connection Error
**Error:** Application can't connect to database
**Cause:** DATABASE_URL missing or invalid

**Solution:**
```bash
# Verify DATABASE_URL in Vercel environment variables

# Test connection locally:
python manage.py dbshell

# For Supabase, check connection string format:
# postgresql://postgres:[PASSWORD]@[HOST]:[PORT]/[DB]

# Verify database is accessible from Vercel IP
```

### Issue 4: Images Not Displaying
**Error:** Image placeholders but no actual images
**Cause:** Media files not persisted or path incorrect

**Solution:**
```bash
# Check media upload folder permissions
chmod -R 755 media/

# Verify MEDIA_URL and MEDIA_ROOT in settings.py

# For Vercel, consider using external storage:
# - AWS S3
# - Cloudinary
# - Supabase Storage
```

### Issue 5: Migration Errors
**Error:** Database schema errors on deploy
**Cause:** Migrations not created or conflicting

**Solution:**
```bash
# Locally:
python manage.py makemigrations

# Check for conflicts:
python manage.py migrate --plan

# Ensure all migrations committed to git

# Push updated migrations:
git add tweet/migrations/
git commit -m "Add migrations"
git push origin main
```

### Issue 6: Build Timeout
**Error:** Build takes >15 minutes or fails
**Cause:** Dependencies taking too long to install

**Solution:**
```bash
# Optimize requirements.txt (remove unused packages)

# Try upgrading pip:
pip install --upgrade pip

# Test build locally:
pip install -r requirements.txt

# Check for large packages or consider caching
```

---

## 📊 MONITORING & MAINTENANCE

### Weekly Checks
- [ ] Check Vercel logs for errors
- [ ] Verify database backups
- [ ] Test critical user flows
- [ ] Monitor response times

### Monthly Tasks
- [ ] Review security logs
- [ ] Update dependencies
- [ ] Check for Django updates
- [ ] Performance optimization review

### Quarterly Reviews
- [ ] Full security audit
- [ ] Database optimization
- [ ] Feature evaluation
- [ ] User feedback analysis

---

## 🎯 SUCCESS CRITERIA

**Deployment is successful when:**
- ✅ All tests in checklist pass
- ✅ No 500 errors in logs
- ✅ Static files load (images, CSS visible)
- ✅ Database operations work (tweets create/load)
- ✅ Authentication flows work
- ✅ Responsive design works on mobile
- ✅ Average response time < 2 seconds
- ✅ No CSRF errors on form submission

---

## 📞 SUPPORT RESOURCES

**Official Docs:**
- Django: https://docs.djangoproject.com/
- Vercel: https://vercel.com/docs
- Bootstrap: https://getbootstrap.com/docs

**Community Help:**
- Stack Overflow: Tag [django] [vercel]
- Django Forum: https://forum.djangoproject.com
- Vercel Discord: https://vercel.com/support

---

**Last Updated:** April 2, 2026
**Status:** ✅ Ready for Production Deployment
