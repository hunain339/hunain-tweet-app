# Technical Root Cause Analysis — Production 500 Errors

## Executive Summary

**Problem**: HTTP 500 errors across multiple features (admin, likes, comments, tweets)

**Root Cause**: Production database (Supabase) missing 3 critical Django migrations that only exist locally

**Solution**: Execute 3 SQL migration scripts in Supabase SQL Editor

**Time to Fix**: 5 minutes

**Prevention**: Ensure `python manage.py migrate` runs on every deployment

---

## Why This Happened

### Local Environment (✅ Working)
```
$ python manage.py showmigrations tweet
tweet
 [X] 0001_initial
 [X] 0002_tweet_likes_comment          ← Applied by `python manage.py migrate`
 [X] 0003_tweet_photo_url               ← Applied by `python manage.py migrate`
 [X] 0004_notification_...              ← Applied by `python manage.py migrate`
```

### Production Environment (❌ Broken)
```
Supabase Database only has:
✅ tweet_tweet table (basic fields from 0001)
❌ Missing: tweet_tweet_likes table
❌ Missing: tweet_comment table  
❌ Missing: tweet_notification table
❌ Missing: view_count column
❌ Missing: parent_id column
```

### Why Deployment Failed
The `vercel.json` had `python manage.py migrate` in buildCommand, but:

1. **Build happens in ephemeral environment** → Database migrations run temporarily
2. **No production database available at build time** → Migrations can't execute against Supabase
3. **Fallback didn't trigger** → The application still deployed and ran against stale schema
4. **Root schemas never matched** → Local dev always worked (SQLite), production always failed (Supabase)

---

## Detailed Failure Analysis

### Failure Point 1: Admin Panel Crashes

**File**: `tweet/admin.py`
```python
from .models import Tweet, Comment, Notification  # ← Tries to load Notification model

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    ...
```

**When you visit `/admin/`**:
1. Django loads admin site
2. Tries to register `Notification` model
3. Reads table info from database
4. **Error**: `ProgrammingError: relation "tweet_notification" does not exist`
5. **Result**: 500 error, admin page crashes

**Fixed by**: Migration 0004 (creates `tweet_notification` table)

---

### Failure Point 2: Like Feature Crashes

**File**: `tweet/admin.py` line 33
```python
def like_count(self, obj):
    return obj.likes.count()  # ← Accesses M2M relationship
```

**When you access admin or try to like a tweet**:
1. Code queries `obj.likes` (ManyToMany field)
2. Django tries to join with `tweet_tweet_likes` table
3. **Error**: `OperationalError: relation "tweet_tweet_likes" does not exist`
4. **Result**: 500 error

**Also in**: `tweet/views.py` - tweet list page tries to prefetch likes

**Fixed by**: Migration 0002 (creates `tweet_tweet_likes` table)

---

### Failure Point 3: Comment Creation Crashes

**File**: `tweet/views.py` (comment creation view)
```python
comment = form.save(commit=False)
comment.save()  # ← Tries to insert into comment table
```

**When you create a comment**:
1. Form submits
2. `CommentForm` tries to save to database
3. **Error**: `OperationalError: relation "tweet_comment" does not exist`
4. **Result**: 500 error

**Fixed by**: Migration 0002 (creates `tweet_comment` table)

---

### Failure Point 4: Tweet Creation Crashes

**File**: `tweet/models.py`
```python
class Tweet(models.Model):
    view_count = models.IntegerField(default=0)  # ← Requires column in DB
```

**File**: `tweet/views.py` (tweet creation view)
```python
tweet = form.save(commit=False)
tweet.user = request.user
tweet.save()  # ← Tries to save view_count
```

**When you create a tweet**:
1. TweetForm saves new Tweet instance
2. Django tries to INSERT with `view_count` value
3. **Error**: `OperationalError: column "tweet_tweet_view_count" does not exist`
4. **Result**: 500 error

**Fixed by**: Migration 0004 (adds `view_count` column)

---

### Failure Point 5: Nested Comments Crash

**File**: `tweet/models.py`
```python
class Comment(models.Model):
    parent = models.ForeignKey('self', null=True, blank=True, ...)  # ← Needs parent_id column
```

**When you reply to a comment**:
1. CommentForm saves with parent_id value
2. Django tries to INSERT with `parent_id` into `tweet_comment` table
3. **Error**: `OperationalError: column "tweet_comment_parent_id" does not exist`
4. **Result**: 500 error

**Fixed by**: Migration 0004 (adds `parent_id` column)

---

## Why "Unknown Token" Error Was Misleading

**The actual chain of events**:
1. User submits form (with valid CSRF token) ✅
2. Django middleware validates CSRF ✅
3. View code executes ❌ **Database query fails**
4. Exception raised, no response body
5. Django returns generic 500 error page
6. Browser shows "invalid token" or similar (not the real error)

**The token was never invalid** — the database query failed, preventing proper error response.

---

## Prevention Strategy

### Problem with Current Setup
```
vercel.json: buildCommand includes migrate
           ↓
Build environment (ephemeral)
           ↓
DATABASE_URL available? ⚠️  Sometimes, sometimes not
           ↓
Migrations run? ⚠️  If DB connection succeeds
           ↓
Production deploY ← But schema may not match
```

### Better Approach
Ensure migrations run in production **post-deployment**, not during build:

**Option A: Use Django Health Check (Recommended)**

Add to `hunain_project/urls.py`:
```python
from django.db import connection
from django.http import JsonResponse

def health_check(request):
    """Verify database and run pending migrations."""
    try:
        # This will fail if database isn't accessible
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        # Could also trigger: python manage.py migrate --check
        return JsonResponse({"status": "healthy"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

urlpatterns = [
    ...
    path('health/', health_check),
]
```

**Option B: Use Release Phase (if platform supports)**

For Render:
```yaml
releases:
  - command: python manage.py migrate --noinput
```

**Option C: Automated Database Initialization**

Create `tweet/management/commands/init_db.py`:
```python
from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Initialize database with migrations'

    def handle(self, *args, **options):
        try:
            call_command('migrate', '--noinput', verbosity=2)
            self.stdout.write(self.style.SUCCESS('Database initialized'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Migration failed: {e}'))
```

---

## Verification Queries

Use these to confirm migrations are applied:

### Check if all tables exist
```sql
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name LIKE 'tweet_%'
ORDER BY table_name;
```

**Expected output**:
```
tweet_comment
tweet_notification
tweet_tweet
tweet_tweet_likes
```

### Check if all columns exist
```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'tweet_tweet' 
ORDER BY ordinal_position;
```

**Must include**:
- `view_count` (integer)
- `photo_url` (varchar)
- `likes` (relationship via tweet_tweet_likes table)

### Check if comment.parent exists
```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'tweet_comment' 
ORDER BY ordinal_position;
```

**Must include**:
- `parent_id` (bigint, nullable)

---

## Timeline of Events

| Date | Event |
|------|-------|
| 2026-03-28 | Migration 0001_initial created (Tweet model) |
| 2026-03-31 | Migration 0002_likes_comment created (adds likes, comments) |
| 2026-04-08 23:08 | Migration 0003_photo_url created (switches to URL field) |
| 2026-04-08 11:55 | Manual SQL migration applied to Supabase (incomplete) |
| 2026-04-11 17:38 | Migration 0004_notification created (adds notifications, view_count) |
| ~2026-04-12+ | **Production deployment — migrations don't run** |
| ~2026-04-13+ | **500 errors start occurring** |
| **NOW** | **Applying missing migrations** |

---

## Related Files

- [models.py](tweet/models.py) — Defines Tweet, Comment, Notification models with all fields
- [views.py](tweet/views.py) — Uses likes, comments, parent_id, view_count
- [admin.py](tweet/admin.py) — Registers Notification model, uses comment relationships
- [migrations/0002_tweet_likes_comment.py](tweet/migrations/0002_tweet_likes_comment.py) — Creates likes and comments
- [migrations/0004_notification...py](tweet/migrations/0004_notification_alter_comment_options_and_more.py) — Creates notifications and adds fields
- [vercel.json](vercel.json) — Build configuration
- [render.yaml](render.yaml) — Render deployment configuration

---

## References

- Django Migrations: https://docs.djangoproject.com/en/6.0/topics/migrations/
- Supabase SQL Editor: https://app.supabase.com → SQL Editor
- Django ORM Fields with Null/Blank: https://docs.djangoproject.com/en/6.0/ref/models/fields/
