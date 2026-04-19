**Purpose:** Controls app security, debugging, and which domains can access your app

#### 3. **Local HTTPS Development**
```python
USE_HTTPS_LOCAL = config('USE_HTTPS_LOCAL', default=True, cast=bool)
if USE_HTTPS_LOCAL:
    SSL_CERT_FILE = BASE_DIR / 'certs' / '127.0.0.1+localhost.pem'
    SSL_KEY_FILE = BASE_DIR / 'certs' / '127.0.0.1+localhost-key.pem'
```

**Purpose:** Enables HTTPS locally for secure testing (matching production environment)

#### 4. **CSRF Protection**
```python
CSRF_TRUSTED_ORIGINS = [...]  # Trust Vercel domains
CSRF_COOKIE_HTTPONLY = False  # Allow JavaScript access (for SPAs)
CSRF_COOKIE_SAMESITE = 'Lax'  # Balance security & usability
```

**Purpose:** Cross-Site Request Forgery protection on form submissions

#### 5. **Installed Applications**
```python
INSTALLED_APPS = [
    'django.contrib.admin',        # Admin panel
    'django.contrib.auth',         # User authentication
    'django.contrib.contenttypes', # Content type framework
    'django.contrib.sessions',     # Session management
    'django.contrib.messages',     # Flash messages
    'django.contrib.staticfiles',  # Static files serving
    'django_extensions',           # Extra Django utilities
    'tweet',                       # Your custom app
]
```

**Purpose:** Registers all Django apps (built-in and custom)

#### 6. **Middleware Stack** (Request/Response Processing Pipeline)
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',     # Serve static files efficiently
    'django.contrib.sessions.middleware.SessionMiddleware',        # Session handling
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',      # CSRF token validation
    'django.contrib.auth.middleware.AuthenticationMiddleware',     # User authentication
    'django.contrib.messages.middleware.MessageMiddleware',        # Flash messages
    'django.middleware.clickjacking.XFrameOptionsMiddleware',      # Clickjacking protection
]
```

**Purpose:** Processes every request in order before reaching views

#### 7. **Templates Configuration**
```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],        # Base templates location
        'APP_DIRS': True,                        # Look in app templates/ folders
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'tweet.context_processors.search_query',  # Custom search query context
            ],
        },
    },
]
```

**Purpose:** Defines template engine and passes variables to all templates

#### 8. **Database Configuration** (Smart Multi-Environment Setup)
```python
# Environment logic:
DATABASE_URL = os.environ.get("DATABASE_URL") or config("DATABASE_URL", default=None)

if IS_VERCEL:
    if not DATABASE_URL:
        # Fallback for build time
        DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3'}}
    else:
        # Production: Use PostgreSQL via Supabase
        DATABASES = {
            'default': dj_database_url.config(
                default=DATABASE_URL,
                conn_max_age=600,
                ssl_require=True
            )
        }
elif DATABASE_URL:
    # Local with PostgreSQL specified
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=True
        )
    }
else:
    # Local development fallback: SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
```

**Purpose:** Seamlessly transitions between SQLite (local dev) and PostgreSQL (production) based on the environment.

#### 9. **Supabase Integration**
```python
from supabase import create_client, Client
SUPABASE_URL = config('SUPABASE_URL', default='')
SUPABASE_KEY = config('SUPABASE_SERVICE_ROLE_KEY', default='')

if SUPABASE_URL and SUPABASE_KEY:
    SUPABASE: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
```
**Purpose:** Initializes the Supabase client for cloud storage operations.

#### 9. **Authentication Configuration**
```python
AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend']
LOGIN_URL = '/account/login/'              # Redirect unauthenticated users here
LOGIN_REDIRECT_URL = '/tweet/'             # After successful login, go to feed
LOGOUT_REDIRECT_URL = '/tweet/'            # After logout, go to feed
```

**Purpose:** Controls user authentication and redirect behavior

#### 10. **Password Validation**
```python
AUTH_PASSWORD_VALIDATORS = [
    'UserAttributeSimilarityValidator',    # Not too similar to username
    'MinimumLengthValidator',              # Minimum 8 characters
    'CommonPasswordValidator',             # Not a common password
    'NumericPasswordValidator',            # Can't be all numbers
]
```

**Purpose:** Enforces strong passwords during registration

#### 11. **Internationalization & Localization**
```python
LANGUAGE_CODE = 'en-us'       # English (United States)
TIME_ZONE = 'UTC'             # Universal Time
USE_I18N = True               # Enable internationalization
USE_TZ = True                 # Enable timezone support
```

**Purpose:** Timestamp handling and language support

#### 12. **Static Files Configuration** (CSS, JS, Images)
```python
STATIC_URL = '/static/'                              # Web URL for serving
STATICFILES_DIRS = [BASE_DIR / 'static']             # Collect from here
STATIC_ROOT = BASE_DIR / 'staticfiles'               # Collected to here
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

**Purpose:** Tells Django how to serve CSS, JavaScript, and other static assets

#### 13. **Media Files Configuration** (User Uploads)
```python
MEDIA_URL = '/media/'                  # Web URL for media
MEDIA_ROOT = BASE_DIR / 'media'        # Store uploads here
```

**Purpose:** Configuration for user-uploaded photos in tweets

#### 14. **Production Security** (Only when not DEBUG or on Vercel)
```python
SECURE_SSL_REDIRECT = True              # Force HTTPS
SESSION_COOKIE_SECURE = True            # Only send cookies over HTTPS
SECURE_HSTS_SECONDS = 31536000          # Enable HSTS for 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True   # Include subdomains
SECURE_HSTS_PRELOAD = True              # Include in browser preload list
```

**Purpose:** Production security hardening

---

## URL ROUTING SYSTEM

### Main URL Configuration: `hunain_project/urls.py`

This file is the entry point for all URLs in your application.

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from tweet import views as tweet_views

urlpatterns = [
    path('admin/', admin.site.urls),           # Django admin panel
    path('', tweet_views.index, name='index'), # Homepage redirect
    path('tweet/', include('tweet.urls')),     # Include tweet app URLs
    path('account/', include('django.contrib.auth.urls')),  # Auth URLs (login, logout)
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### Complete URL Map:

| URL Pattern | View Name | HTTP Method | Purpose |
|-------------|-----------|-------------|---------|
| `/` | `index` | GET | Homepage (redirects to tweet_list) |
| `/tweet/` | `tweet_list` | GET | Display all tweets (with search & pagination) |
| `/tweet/create/` | `tweet_create` | POST | Create new tweet |
| `/tweet/<id>/edit/` | `edit_tweet` | POST | Edit existing tweet |
| `/tweet/<id>/delete/` | `tweet_delete` | POST | Delete tweet with confirmation |
| `/tweet/register/` | `register` | POST | User registration |
| `/tweet/<id>/like/` | `tweet_like` | GET | Like/unlike toggle |
| `/tweet/<id>/comment/` | `add_comment` | POST | Add comment to tweet |
| `/tweet/profile/<username>/` | `user_profile` | GET | View user's profile & tweets |
| `/account/login/` | `login` | POST | User login (Django built-in) |
| `/account/logout/` | `logout` | POST | User logout (Django built-in) |
| `/admin/` | `admin` | GET/POST | Django default admin panel |
| `/tweet/admin/dashboard/` | `admin_dashboard` | GET | Custom Admin Dashboard (Stats) |
| `/tweet/admin/users/` | `admin_users` | GET | User Management (Dashboard) |
| `/tweet/admin/users/<id>/delete/` | `admin_user_delete` | POST | Delete User (Admin action) |
| `/tweet/admin/users/<id>/reset-password/` | `admin_reset_password` | POST | Reset User Password (Admin action) |

### App URL Configuration: `tweet/urls.py`

```python
from . import views
from django.urls import path

urlpatterns = [
    path('', views.tweet_list, name='tweet_list'),
    path('create/', views.tweet_create, name='tweet_create'),
    path('<int:tweet_id>/edit/', views.edit_tweet, name='tweet_edit'),
    path('<int:tweet_id>/delete/', views.tweet_delete, name='tweet_delete'),
    path('register/', views.register, name='register'),
    path('<int:tweet_id>/like/', views.tweet_like, name='tweet_like'),
    path('<int:tweet_id>/comment/', views.add_comment, name='add_comment'),
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
]
```

**Key Concepts:**
- `<int:tweet_id>` - Dynamic URL parameter (integer)
- `<str:username>` - String parameter for usernames
- `name='...'` - URL name for `{% url %}` template tag usage

---

## MODELS (DATA LAYER)

### File: `tweet/models.py`

Models define the database structure and how data is stored and retrieved.

### Model 1: Tweet

```python
from django.db import models
from django.contrib.auth.models import User

class Tweet(models.Model):
    """
    Represents a user's tweet/post on the platform.
    
    Fields:
        user: ForeignKey to User - Who posted this tweet
        text: TextField - The tweet content (max 240 characters)
        photo: ImageField - Optional image attached to tweet
        created_at: DateTimeField - When tweet was created
        updated_at: DateTimeField - When tweet was last modified
        likes: ManyToManyField - Users who liked this tweet
    """
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # ForeignKey: One user creates many tweets
    # CASCADE: If user deleted, delete all their tweets
    
    text = models.TextField(max_length=240)
    # TextField with max length of 240 characters (Twitter-like limit)
    
    photo_url = models.URLField(blank=True, null=True, validators=[URLValidator()])
    # photo_url: Stores the public URL of the image stored in Supabase Storage
    # blank=True: Not required when creating
    # null=True: Can be NULL in database
    
    created_at = models.DateTimeField(auto_now_add=True)
    # auto_now_add: Automatically set to current time on creation
    # Never changes after creation
    
    updated_at = models.DateTimeField(auto_now=True)
    # auto_now: Automatically update to current time on every save
    
    likes = models.ManyToManyField(
        User,
        related_name='liked_tweets',
        blank=True
    )
    # ManyToMany: Many users can like many tweets
    # related_name='liked_tweets': Access likes from user: user.liked_tweets.all()
    # blank=True: Not required, can have zero likes
    
    def __str__(self):
        """String representation in Django admin"""
        return f'{self.user.username} - {self.text[:10]}'
        # Example: "hunain - Hello wor"

    class Meta:
        """Model metadata"""
        ordering = ['-created_at']  # Newest tweets first
        verbose_name_plural = "Tweets"
```

### Model 2: Comment

```python
class Comment(models.Model):
    """
    Represents a comment/reply on a tweet.
    
    Fields:
        tweet: ForeignKey to Tweet - Which tweet this comments on
        user: ForeignKey to User - Who wrote this comment
        text: TextField - The comment content
        created_at: DateTimeField - When comment was created
    """
    
    tweet = models.ForeignKey(
        Tweet,
        related_name='comments',
        on_delete=models.CASCADE
    )
    # ForeignKey: One tweet has many comments
    # related_name='comments': Access via tweet.comments.all()
    # CASCADE: Delete comment if parent tweet is deleted
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # ForeignKey: One user creates many comments
    # CASCADE: Delete comments if user is deleted
    
    text = models.TextField(max_length=240)
    # Max 240 characters for consistency
    
    created_at = models.DateTimeField(auto_now_add=True)
    # Automatically set on creation, never changes
    
    def __str__(self):
        """String representation"""
        return f'{self.user.username}: {self.text[:20]}'
        # Example: "hunain: Hey, great tweet..."

    class Meta:
        """Model metadata"""
        ordering = ['-created_at']  # Newest comments first
        verbose_name_plural = "Comments"
```

### Query Examples:

```python
# Get all tweets by a user
tweets = Tweet.objects.filter(user=user)

# Get tweets with eager loading (optimization)
tweets = Tweet.objects.select_related('user').prefetch_related('likes', 'comments__user')

# Count likes on a tweet
like_count = tweet.likes.count()

# Check if user liked a tweet
is_liked = tweet.likes.filter(id=request.user.id).exists()

# Get all comments on a tweet
comments = tweet.comments.all()

# Get user's liked tweets
liked = user.liked_tweets.all()
```

---

## FORMS (INPUT VALIDATION)

### File: `tweet/forms.py`

Forms validate user input before saving to the database.

### Form 1: TweetForm

```python
from django import forms
from .models import Tweet
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class TweetForm(forms.ModelForm):
    """
    Form for creating and editing tweets.
    
    Includes a FileField for image uploads (to Supabase) and character limit metadata.
    """
    
    photo = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control form-control-custom',
            'accept': 'image/jpeg,image/png,image/webp,image/gif',
            'id': 'id_photo',
            'aria-label': 'Attach an image (optional)',
        }),
        help_text='JPEG, PNG, WebP or GIF — max 5 MB',
    )

    class Meta:
        model = Tweet
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control form-control-custom',
                'placeholder': "What's happening?",
                'rows': 4,
                'maxlength': '240',
                'id': 'id_text',
                'aria-label': 'Tweet content',
                'aria-describedby': 'char-counter',
            }),
        }

    def clean_photo(self):
        """Custom validation for file size and content type"""
        photo = self.cleaned_data.get('photo')
        if photo:
            if photo.size > 5 * 1024 * 1024:
                raise forms.ValidationError('File too large. Maximum size is 5 MB.')
            if photo.content_type not in ['image/jpeg', 'image/png', 'image/webp', 'image/gif']:
                raise forms.ValidationError('Unsupported file type. Please upload a JPEG, PNG, WebP, or GIF.')
        return photo
```

### Form 2: UserRegistrationForm

```python
class UserRegistrationForm(UserCreationForm):
    """
    Form for user registration with email.
    
    Extends Django's built-in UserCreationForm to add email field.
    """
    
    email = forms.EmailField(required=True)
    # Add email field (not in default UserCreationForm)
    
    def __init__(self, *args, **kwargs):
        """Customize form widget rendering"""
        super().__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            # Add Bootstrap CSS classes to all form fields
            field.widget.attrs.update({
                'class': 'form-control form-control-custom',
                'placeholder': field.label
            })
            
            # Simplify password help text
            if field.help_text and 'password' in field_name.lower():
                field.help_text = "Standard password requirements apply."
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)
        # Default fields: username, password1, password2
        # Added: email
    
    # Automatic validations from UserCreationForm:
    # - username: unique, alphanumeric
    # - password1: minimum 8 chars, not common
    # - password2: must match password1
    # - email: valid email format
```

### Form 3: CommentForm

```python
class CommentForm(forms.ModelForm):
    """
    Form for adding comments to tweets.
    """
    
    class Meta:
        model = Comment  # Link to Comment model
        
        fields = ['text']
        # Only text field is editable
        # (tweet_id and user_id are set by the view)
        
        widgets = {
            'text': forms.TextInput(attrs={
                'placeholder': 'Add a comment...',
                'class': 'form-control form-control-custom shadow-none'
            })
        }
    
    # Automatic validations:
    # - text: max_length=240, required
```

### Form Usage in Views:

```python
# GET request: Display empty form
form = TweetForm()

# POST request: Validate user input
form = TweetForm(request.POST, request.FILES)
if form.is_valid():
    tweet = form.save(commit=False)  # Don't save yet
    tweet.user = request.user        # Add user
    tweet.save()                      # Now save to database
```

---

## VIEWS (BUSINESS LOGIC)

### File: `tweet/views.py`

Views handle the request-response cycle and contain business logic.

```python
from django_ratelimit.decorators import ratelimit
from django.contrib.auth.decorators import login_required
# ... other standard imports
```

### View 1: index

```python
def index(request):
    """
    Homepage view that redirects to tweet list.
    
    Purpose: Landing page that immediately redirects authenticated users to the feed
    and shows homepage to anonymous users.
    
    URL: GET /
    Returns: Redirect to tweet_list
    """
    return redirect('tweet_list')
```

**Flow:** User → / → Redirects to /tweet/

---

### View 2: tweet_list (Main Feed)

```python
def tweet_list(request):
    """
    Display all tweets with pagination and PG Full-Text Search.
    
    Features:
    - PostgreSQL SearchVector/SearchRank (or icontains fallback)
    - select_related/prefetch_related optimizations
    """
    query = request.GET.get('q', '').strip()
    
    # Optimized base queryset
    base_qs = Tweet.objects.select_related('user').prefetch_related(
        'likes', 'comments__user'
    ).order_by('-created_at')

    if query:
        # Full-Text Search logic implemented in view
        tweets_list = _full_text_search(base_qs, query)
    else:
        tweets_list = base_qs
    
    paginator = Paginator(tweets_list, 10)
    tweets = paginator.get_page(request.GET.get('page'))
    
    return render(request, 'tweet_list.html', {
        'tweets': tweets,
        'query': query
    })
```

**Flow:**
1. User visits /tweet/
2. All tweets fetched with optimized queries
3. Optional search applied
4. Results paginated (10 per page)
5. Rendered in tweet_list.html

**Optimization Techniques:**
- `select_related('user')` - Joins User table, 1 query instead of N
- `prefetch_related('likes', 'comments__user')` - Smart caching in Python
- Result: ~3 queries instead of 100+ queries

---

### View 3: tweet_create (Create New Tweet)

```python
@ratelimit(key='user', rate='10/h', block=True)
@login_required
def tweet_create(request):
    """
    Handle new tweet creation with Supabase image upload and rate limiting.
    """
    if request.method == 'POST':
        form = TweetForm(request.POST, request.FILES)
        if form.is_valid():
            tweet = form.save(commit=False)
            tweet.user = request.user
            
            photo = form.cleaned_data.get('photo')
            if photo:
                # Utility handles upload to Supabase bucket and returns public URL
                tweet.photo_url = upload_to_supabase(photo)
                
            tweet.save()
            messages.success(request, 'Tweet posted successfully!')
            return redirect('tweet_list')
    else:
        form = TweetForm()
        
    return render(request, 'tweet_form.html', {'form': form, 'action': 'create'})
```

**Flow:**
1. Unauthenticated user → Redirected to login
2. Authenticated user GETs /tweet/create/ → Shows empty form
3. User fills form and POSTs → Server validates
4. Valid → Tweet saved, user redirected to feed
5. Invalid → Form re-displayed with error messages

---

### View 4: edit_tweet (Edit Existing Tweet)

```python
@login_required
def edit_tweet(request, tweet_id):
    """
    Edit an existing tweet.
    
    URL: GET/POST /tweet/<id>/edit/
    
    Path Parameters:
        tweet_id: ID of tweet to edit
    
    Authorization: Only tweet owner can edit
    Template: tweet_form.html
    """
    
    # Get tweet, 404 if not found or not owner
    tweet = get_object_or_404(Tweet, pk=tweet_id, user=request.user)
    # Queries: "Give me tweet with id=tweet_id AND user=request.user"
    # If not found or wrong user: 404 error
    
    if request.method == 'POST':
        form = TweetForm(request.POST, instance=tweet)
        
        if form.is_valid():
            updated_tweet = form.save(commit=False)
            
            # SUPABASE STORAGE LOGIC:
            if 'photo' in request.FILES:
                try:
                    # Delete old photo from Supabase if it exists
                    if tweet.photo_url:
                        delete_from_supabase(tweet.photo_url)
                    # Upload new photo
                    updated_tweet.photo_url = upload_to_supabase(request.FILES['photo'])
                except ValidationError as e:
                    form.add_error(None, e)
                    return render(request, 'tweet_form.html', {'form': form})
            
            updated_tweet.save()
            messages.success(request, 'Tweet updated successfully!')
            return redirect('tweet_list')
    else:
        form = TweetForm(instance=tweet)
    
    return render(request, 'tweet_form.html', {'form': form})
```

**Key Difference from tweet_create:**
- Instance parameter: `TweetForm(instance=tweet)` pre-fills all fields
- Authorization check: `user=request.user` ensures only owner can edit

---

### View 5: tweet_delete (Delete Tweet)

```python
@login_required
def tweet_delete(request, tweet_id):
    """
    Delete a tweet with confirmation.
    
    URL: GET/POST /tweet/<id>/delete/
    
    Path Parameters:
        tweet_id: ID of tweet to delete
    
    GET: Show confirmation page
    POST: Delete tweet
    
    Authorization: Only tweet owner can delete
    Template: tweet_confirm_delete.html
    """
    
    # Security: Only allow tweet owner to access
    tweet = get_object_or_404(Tweet, pk=tweet_id, user=request.user)
    
    if request.method == 'POST':
        # SUPABASE STORAGE LOGIC:
        # Delete photo from Supabase if it exists
        if tweet.photo_url:
            delete_from_supabase(tweet.photo_url)
            
        tweet.delete()
        messages.success(request, 'Tweet deleted!')
        return redirect('tweet_list')
    
    return render(request, 'tweet_confirm_delete.html', {'tweet': tweet})
```

**Flow:**
1. User clicks delete button → Gets /tweet/<id>/delete/
2. Confirmation page shown
3. User confirms (POST) → Tweet deleted → Redirected to feed

---

### View 6: register (User Registration)

```python
def register(request):
    """
    Display registration form and handle new user creation.
    
    URL: GET/POST /tweet/register/
    
    GET: Display empty registration form
    POST: Process registration and create user
    
    Template: registration/register.html
    Redirects: Auto-login and redirect to tweet_list
    """
    
    if request.method == 'POST':
        # Form submission
        form = UserRegistrationForm(request.POST)
        
        if form.is_valid():
            # Data passed validation
            user = form.save()
            # Creates: User object with username, email, hashed password
            
            # Auto-login the new user
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            # Sets session cookie automatically
            
            messages.success(request, f'Welcome to Tweetbar, {user.username}!')
            return redirect('tweet_list')
    else:
        # GET: display empty form
        form = UserRegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})
```

**Flow:**
1. User visits /tweet/register/ → Empty form shown
2. Fills form and submits → Server validates
3. Valid → User account created, auto-logged in, redirected to feed
4. Invalid → Form re-displayed with error messages

**Validation Checks:**
- Username: Unique, alphanumeric
- Email: Valid format (email field validation)
- Password: Min 8 chars, not common, not numeric
- Password confirmation: Must match

---

### View 7: tweet_like (Like/Unlike Toggle)

```python
@ratelimit(key='user', rate='30/h', block=True)
@login_required
def tweet_like(request, tweet_id):
    """Toggle like on a tweet using AJAX or standard redirect"""
    tweet = get_object_or_404(Tweet, id=tweet_id)
    
    if tweet.likes.filter(id=request.user.id).exists():
        tweet.likes.remove(request.user)
    else:
        tweet.likes.add(request.user)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'liked': tweet.likes.filter(id=request.user.id).exists(),
            'count': tweet.likes.count()
        })
    return redirect('tweet_list')
```

**Logic:**
```
Check: Is user in tweet.likes?
  - YES: Remove (unlike)
  - NO: Add (like)
Redirect: Go back to feed
```

**Database:**
```sql
-- When user likes tweet (likes table)
INSERT INTO tweet_tweet_likes (tweet_id, user_id) VALUES (5, 2)

-- When user unlikes (removes like)
DELETE FROM tweet_tweet_likes WHERE tweet_id=5 AND user_id=2
```

---

### View 8: add_comment (Post Comment)

```python
@login_required
def add_comment(request, tweet_id):
    """
    Add a comment to a tweet.
    
    URL: POST /tweet/<id>/comment/
    
    Path Parameters:
        tweet_id: ID of tweet to comment on
    
    Form Data:
        text: Comment text
    
    Authentication: Required
    Returns: Redirect back to tweet_list
    """
    
    # Get tweet (404 if not found)
    tweet = get_object_or_404(Tweet, id=tweet_id)
    
    if request.method == 'POST':
        # User submitted comment form
        form = CommentForm(request.POST)
        
        if form.is_valid():
            # Data passed validation
            comment = form.save(commit=False)        # Create but don't save
            comment.tweet = tweet                   # Link to parent tweet
            comment.user = request.user             # Set comment author
            comment.save()                          # Save to database
            
            messages.success(request, 'Comment added!')
    
    return redirect('tweet_list')
```

**Flow:**
1. User submits comment form (inline on tweet card)
2. POST to /tweet/<id>/comment/
3. Create Comment object and link to tweet
4. Save to database
5. Redirect back to feed

---

### View 9: user_profile (User Profile Page)

```python
def user_profile(request, username):
    """
    Display user's profile and their tweets.
    
    URL: GET /tweet/profile/<username>/
    
    Path Parameters:
        username: Username(string) of the profile to view
    
    Template: profile.html
    Context Variables:
        profile_user: The user object being viewed
        tweets: Their tweets, paginated
    
    Database Optimization: Uses select_related and prefetch_related
    """
    
    # Get user by username (404 if not found)
    user = get_object_or_404(User, username=username)
    
    # Get all tweets by this user with optimizations
    tweets_list = Tweet.objects.filter(user=user).select_related(
        'user'
    ).prefetch_related(
        'likes',
        'comments__user'
    ).order_by('-created_at')
    
    # Pagination: 10 tweets per page
    paginator = Paginator(tweets_list, 10)
    page_number = request.GET.get('page')
    tweets = paginator.get_page(page_number)
    
    return render(request, 'profile.html', {
        'profile_user': user,
        'tweets': tweets
    })
```

**Flow:**
1. User visits /tweet/profile/hunain/
2. App fetches @hunain user and their tweets
3. Shows profile with stats (tweet count, like count)
4. Displays paginated tweets (10 per page)
5. Visitor can like/comment (if authenticated) or just view

**Database Usage:**
- Fetched User object
- Fetched tweets with like/comment info
- Single page: ~3 queries total

---

### View 10: admin_dashboard (Superuser Only)

```python
@staff_member_required
def admin_dashboard(request):
    """
    Display overall application statistics for administrators.
    """
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    
    stats = {
        'total_users': User.objects.count(),
        'total_tweets': Tweet.objects.count(),
        'total_comments': Comment.objects.count(),
        'total_likes': Tweet.objects.aggregate(Count('likes'))['likes__count'] or 0,
    }
    
    recent_tweets = Tweet.objects.select_related('user').order_by('-created_at')[:5]
    recent_users = User.objects.order_by('-date_joined')[:5]
    
    return render(request, 'admin_dashboard.html', {
        'stats': stats,
        'recent_tweets': recent_tweets,
        'recent_users': recent_users
    })
```

### View 11: admin_users (User Management)

```python
@staff_member_required
def admin_users(request):
    """
    Manage users: list, search, and access admin actions.
    """
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    
    query = request.GET.get('q', '')
    users_list = User.objects.annotate(tweet_count=Count('tweet')).order_by('-date_joined')
    
    if query:
        users_list = users_list.filter(
            Q(username__icontains=query) | Q(email__icontains=query)
        )
    
    paginator = Paginator(users_list, 20)
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)
    
    return render(request, 'admin_users.html', {'users': users, 'query': query})
```

---

## TEMPLATES (UI LAYER)

### Base Template: `templates/layout.html`

This template wraps all pages. Every page extends this base.

```html
{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Tweetbar{% endblock %}</title>
    
    <!-- Bootstrap CSS (from CDN) -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">
    
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@500;600;700;800">
    
    <!-- Custom CSS -->
    <link rel="stylesheet" href="{% static 'css/style.css' %}">
</head>
<body>
    <!-- Fixed Background Decorative Elements -->
    <div style="position: fixed; background: radial-gradient(...); z-index: -1;"></div>
    
    <!-- NAVIGATION BAR -->
    <nav class="navbar navbar-expand-lg sticky-top">
        <!-- Brand/Logo -->
        <a class="navbar-brand" href="{% url 'index' %}">
            <svg><!-- Tweetbar logo SVG --></svg>
            <span>Tweetbar</span>
        </a>
        
        <!-- Mobile Toggle Button -->
        <button class="navbar-toggler" data-bs-toggle="collapse" data-bs-target="#navbarNav">
            <!-- Toggle icon -->
        </button>
        
        <!-- Navigation Links -->
        <div class="collapse navbar-collapse" id="navbarNav">
            <ul class="navbar-nav me-auto">
                <li><a class="nav-link" href="{% url 'index' %}">Home</a></li>
                <li><a class="nav-link" href="{% url 'tweet_list' %}">Explore</a></li>
            </ul>
            
            <!-- Search Bar -->
            <form class="d-flex mx-lg-auto" method="GET" action="{% url 'tweet_list' %}">
                <input class="form-control" type="search" name="q" placeholder="Search tweets or users..." value="{{ query }}">
                <!-- Clear button if search active -->
            </form>
            
            <!-- Right-side Auth Links -->
            {% if user.is_authenticated %}
                <!-- Authenticated User -->
                <li>
                    <a href="{% url 'user_profile' user.username %}">
                        <div style="background-color: var(--primary); color: white;">
                            {{ user.username|first|upper }}
                        </div>
                        @{{ user.username }}
                    </a>
                </li>
                <li>
                    <form method="post" action="{% url 'logout' %}">
                        {% csrf_token %}
                        <button type="submit" class="btn btn-outline-light btn-sm">Logout</button>
                    </form>
                </li>
            {% else %}
                <!-- Anonymous User -->
                <li><a class="nav-link" href="{% url 'login' %}">Login</a></li>
                <li><a class="btn btn-primary" href="{% url 'register' %}">Get Started</a></li>
            {% endif %}
        </div>
    </nav>
    
    <!-- FLASH MESSAGES -->
    {% if messages %}
        <div class="row justify-content-center">
            <div class="col-md-8">
                {% for message in messages %}
                    <div class="alert alert-{{ message.tags }}">
                        {{ message }}
                    </div>
                {% endfor %}
            </div>
        </div>
    {% endif %}
    
    <!-- PAGE CONTENT BLOCK (Different for each page) -->
    <main class="container py-5">
        {% block content %}{% endblock %}
    </main>
    
    <!-- Bootstrap JS (for navbar toggle, etc.) -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

### Key Template Features:

1. **Block System:** `{% block title %}` and `{% block content %}` - Each page overwrites
2. **Conditional Rendering:** `{% if user.is_authenticated %}` - Shows different nav for logged-in users
3. **URL Generation:** `{% url 'tweet_list' %}` - Generates correct URL from URL name
4. **Static Files:** `{% static 'css/style.css' %}` - Serves CSS/JS files
5. **CSRF Token:** `{% csrf_token %}` - Security for form submissions
6. **Search Bar:** Passes `q` parameter to tweet_list view

---

### Tweet List Template: `tweet/templates/tweet_list.html`

Main feed showing all tweets with interactions.

**Key Sections:**

1. **Header with Search Results**
   ```html
   <h1>{% if query %}Results for "{{ query }}"{% else %}Explore Feed{% endif %}</h1>
   <a class="btn btn-primary-custom" href="{% url 'tweet_create' %}">
       <svg><!-- Plus icon --></svg> Post a Tweet
   </a>
   ```

2. **Tweet Cards Grid** (3-column layout)
   ```html
   <div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4">
       {% for tweet in tweets %}
       <div class="col">
           <article class="tweet-card">
               <!-- Tweet image if exists -->
               {% if tweet.photo %}<img src="{{ tweet.photo.url }}" />{% endif %}
               
               <!-- Tweet content -->
               <div class="p-4">
                   <!-- Author header -->
                   <div class="d-flex justify-content-between">
                       <div class="bg-primary rounded-circle">
                           {{ tweet.user.username|first|upper }}
                       </div>
                       <a href="{% url 'user_profile' tweet.user.username %}">
                           @{{ tweet.user.username }}
                       </a>
                   </div>
                   
                   <!-- Tweet text -->
                   <p>{{ tweet.text }}</p>
                   
                   <!-- Interactions -->
                   <div class="d-flex gap-2">
                       <!-- Like button -->
                       <a href="{% url 'tweet_like' tweet.id %}">
                           <svg><!-- Heart icon --></svg>
                           <span>{{ tweet.likes.count }}</span>
                       </a>
                       
                       <!-- Comment count -->
                       <div>
                           <svg><!-- Comment icon --></svg>
                           <span>{{ tweet.comments.count }}</span>
                       </div>
                       
                       <!-- Edit/Delete (if owner) -->
                       {% if tweet.user == request.user %}
                           <a href="{% url 'tweet_edit' tweet.id %}">Edit</a>
                           <a href="{% url 'tweet_delete' tweet.id %}">Delete</a>
                       {% endif %}
                   </div>
                   
                   <!-- Comments preview -->
                   {% if tweet.comments.all %}
                   <div class="mt-3 p-3">
                       {% for comment in tweet.comments.all|slice:":3" %}
                       <div class="mb-2">
                           <span class="text-primary fw-bold">@{{ comment.user.username }}</span>
                           <span>{{ comment.text }}</span>
                       </div>
                       {% endfor %}
                       {% if tweet.comments.count > 3 %}
                           <small>...and {{ tweet.comments.count|add:"-3" }} more</small>
                       {% endif %}
                   </div>
                   {% endif %}
                   
                   <!-- Quick comment form (authenticated only) -->
                   {% if user.is_authenticated %}
                   <form method="POST" action="{% url 'add_comment' tweet.id %}" class="mt-3">
                       {% csrf_token %}
                       <input type="text" name="text" placeholder="Write a reply..." required>
                       <button type="submit" class="btn btn-sm btn-primary">Send</button>
                   </form>
                   {% endif %}
               </div>
           </article>
       </div>
       {% empty %}
       <!-- No tweets found -->
       <div class="col-12 text-center">
           <h3>No tweets found</h3>
           <a href="{% url 'tweet_list' %}">Clear search</a>
       </div>
       {% endfor %}
   </div>
   ```

3. **Pagination**
   ```html
   {% if tweets.has_other_pages %}
   <nav class="mt-5">
       <ul class="pagination">
           {% if tweets.has_previous %}
           <li><a href="?page={{ tweets.previous_page_number }}{% if query %}&q={{ query }}{% endif %}">Previous</a></li>
           {% endif %}
           
           <li><span>{{ tweets.number }} of {{ tweets.paginator.num_pages }}</span></li>
           
           {% if tweets.has_next %}
           <li><a href="?page={{ tweets.next_page_number }}{% if query %}&q={{ query }}{% endif %}">Next</a></li>
           {% endif %}
       </ul>
   </nav>
   {% endif %}
   ```

---

### Registration Template: `templates/registration/register.html`

User account creation form.

```html
{% extends "layout.html" %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-8 col-lg-6">
        <div class="tweet-card p-5">
            <h2>Join Tweetbar</h2>
            <p class="text-muted">Create your account and start sharing</p>
            
            <form method="post">
                {% csrf_token %}
                
                <!-- Display form errors -->
                {% if form.non_field_errors %}
                <div class="alert alert-danger">
                    {{ form.non_field_errors }}
                </div>
                {% endif %}
                
                <!-- Form fields -->
                {% for field in form %}
                <div class="mb-4">
                    <label class="form-label">{{ field.label }}</label>
                    {{ field }}
                    
                    <!-- Field errors -->
                    {% if field.errors %}
                    <div class="text-danger small mt-1">
                        {% for error in field.errors %}
                            <p>{{ error }}</p>
                        {% endfor %}
                    </div>
                    {% endif %}
                    
                    <!-- Help text (password requirements) -->
                    {% if field.help_text %}
                    <div class="text-muted small mt-2">
                        {{ field.help_text|safe }}
                    </div>
                    {% endif %}
                </div>
                {% endfor %}
                
                <!-- Submit button -->
                <button type="submit" class="btn btn-primary-custom btn-block">
                    Create Account
                </button>
                
                <!-- Link to login -->
                <p class="text-center mt-3">
                    Already have an account? <a href="{% url 'login' %}">Log in</a>
                </p>
            </form>
        </div>
    </div>
</div>
{% endblock %}
```

---

### Profile Template: `tweet/templates/profile.html`

User profile with statistics and tweet history.

```html
{% extends 'layout.html' %}

{% block content %}
<!-- Profile Header Card -->
<div class="row justify-content-center mb-5">
    <div class="col-lg-10">
        <div class="tweet-card p-5 text-center">
            <!-- Large profile letter avatar -->
            <div class="mx-auto bg-primary rounded-circle" style="width: 140px; height: 140px;">
                {{ profile_user.username|first|upper }}
            </div>
            
            <!-- Username -->
            <h1>@{{ profile_user.username }}</h1>
            
            <!-- Join date -->
            <p class="text-muted">
                <svg><!-- Calendar icon --></svg>
                Joined {{ profile_user.date_joined|date:"F Y" }}
            </p>
            
            <!-- Statistics -->
            <div class="d-flex justify-content-center gap-4 mt-4 pt-4">
                <div>
                    <h2 class="text-primary">{{ profile_user.tweet_set.count }}</h2>
                    <small class="text-muted">Tweets</small>
                </div>
                <div class="vr"></div>
                <div>
                    <h2 class="text-primary">{{ profile_user.liked_tweets.count }}</h2>
                    <small class="text-muted">Likes</small>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Tweets Section -->
<h3>Latest Tweets</h3>

<!-- Tweets Grid (same as tweet_list) -->
<div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4">
    {% for tweet in tweets %}
        <!-- Tweet card (similar to tweet_list.html) -->
    {% empty %}
    <p>No tweets yet.</p>
    {% endfor %}
</div>

<!-- Pagination (same as tweet_list) -->
```

---

### Tweet Form Template: `tweet/templates/tweet_form.html`

Create and edit tweet form.

```html
{% extends 'layout.html' %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-lg-6">
        <div class="tweet-card p-5">
            <h2>
                {% if form.instance.pk %}Edit Tweet{% else %}New Tweet{% endif %}
            </h2>
            
            <form method="post" enctype="multipart/form-data">
                {% csrf_token %}
                
                <!-- Text field -->
                <div class="mb-4">
                    <label class="form-label">What's on your mind?</label>
                    {{ form.text }}
                    {% if form.text.errors %}
                    <div class="text-danger small">
                        {{ form.text.errors }}
                    </div>
                    {% endif %}
                </div>
                
                <!-- Photo field -->
                <div class="mb-4">
                    <label class="form-label">Attach an image (optional)</label>
                    {{ form.photo }}
                    {% if form.photo.errors %}
                    <div class="text-danger small">
                        {{ form.photo.errors }}
                    </div>
                    {% endif %}
                </div>
                
                <!-- Buttons -->
                <button type="submit" class="btn btn-primary-custom btn-block">
                    {% if form.instance.pk %}Update Tweet{% else %}Post Tweet{% endif %}
                </button>
                <a href="{% url 'tweet_list' %}" class="btn btn-link text-center">
                    Cancel
                </a>
            </form>
        </div>
    </div>
</div>
{% endblock %}
```

---

### Delete Confirmation Template: `tweet/templates/tweet_confirm_delete.html`

Confirmation page before deleting tweet.

```html
{% extends 'layout.html' %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6 col-lg-5">
        <div class="tweet-card p-5 text-center">
            <!-- Warning icon -->
            <div class="bg-danger bg-opacity-10 text-danger rounded-circle" style="width: 80px; height: 80px;">
                <svg><!-- Trash icon --></svg>
            </div>
            
            <h2>Delete Tweet?</h2>
            <p class="text-muted">This action cannot be undone.</p>
            
            <!-- Confirmation form -->
            <form method="post">
                {% csrf_token %}
                <button type="submit" class="btn btn-danger py-3">
                    Yes, Delete Tweet
                </button>
                <a href="{% url 'tweet_list' %}" class="btn btn-outline-light py-3">
                    No, Go Back
                </a>
            </form>
        </div>
    </div>
</div>
{% endblock %}
```

---

### Homepage Template: `tweet/templates/index.html`

Landing page/hero section.

```html
{% extends 'layout.html' %}

{% block content %}
<div class="row justify-content-center align-items-center py-5">
    <div class="col-lg-8 text-center">
        <!-- Badge -->
        <span class="badge">
            ✨ Introducing Tweetbar v2.0
        </span>
        
        <!-- Hero Title -->
        <h1 class="display-3 fw-bold mb-4">
            Share your thoughts, <br>
            <span class="text-primary">connect with the world.</span>
        </h1>
        
        <!-- Description -->
        <p class="lead text-muted">
            A modern, fast platform to express yourself and discover what's happening.
        </p>
        
        <!-- CTA Buttons -->
        <div class="d-flex flex-column flex-sm-row justify-content-center gap-3">
            <a href="{% url 'tweet_list' %}" class="btn btn-primary-custom px-5 py-3">
                Explore Feed
            </a>
            {% if not user.is_authenticated %}
            <a href="{% url 'register' %}" class="btn btn-outline-light px-5 py-3">
                Join Now
            </a>
            {% endif %}
        </div>
        
        <!-- Mockup card -->
        <div class="mt-5 pt-5">
            <div class="tweet-card p-2">
                <!-- Skeleton loading effect -->
                <div class="p-4">
                    <div class="bg-white rounded-pill" style="height: 10px; width: 120px;"></div>
                    <div class="bg-white rounded-pill mt-2" style="height: 8px; width: 80px;"></div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

---

## COMPLETE USER FLOWS

### Flow 1: User Registration & First Tweet

```
START
  ↓
User visits / (index)
  ↓
Redirects to /tweet/ (tweet_list)
  ↓
Sees unauthenticated feed (all tweets)
  ↓
Clicks "Get Started" button → /tweet/register/
  ↓
Fills registration form (username, email, password, password confirm)
  ↓
Validates:
  ✓ Username unique
  ✓ Email valid format
  ✓ Password >= 8 chars
  ✓ Password matches confirm
  ✓ Password not common
  ↓
POSTs form → Server creates User
  ↓
Auto-login (session cookie set)
  ↓
Redirect to /tweet/ (feed)
  ↓
Clicks "Post a Tweet" → /tweet/create/
  ↓
Fills tweet form (text, optional image)
  ↓
Validates: text <= 240 chars, image is valid file
  ↓
POSTs form → Server creates Tweet
  ↓
Redirect to /tweet/ (feed)
  ↓
Tweet now visible in feed
END
```

---

### Flow 2: Like & Comment

```
START
User sees tweet on /tweet/ feed
  ↓
Clicks heart icon → /tweet/<id>/like/ (GET)
  ↓
Server checks: Is user already in tweet.likes?
  ├─ YES: Remove user from likes
  └─ NO: Add user to likes
  ↓
Redirect to /tweet/ (feed)
  ↓
User sees like count updated instantly (needs page reload)
  ↓
User clicks reply field, enters comment
  ↓
POSTs to /tweet/<id>/comment/ with text
  ↓
Server validates: text <= 240 chars
  ↓
Creates Comment(tweet, user, text)
  ↓
Redirect to /tweet/
  ↓
Comment now visible in tweet's comment section
END
```

---

### Flow 3: Search

```
START
User on tweet feed /tweet/
  ↓
Types search query in navbar search box
  ↓
Presses Enter (submits form GET to /tweet/)
  ↓
URL becomes /tweet/?q=django
  ↓
Server receives query parameter
  ↓
Filters tweets:
  - WHERE text ILIKE '%django%'
  - OR username ILIKE '%django%'
  ↓
Shows filtered results (paginated 10 per page)
  ↓
If no results found, shows "No tweets found"
  ↓
User can paginate through results or clear search
END
```

---

### Flow 4: User Profile Visit

```
START
User on feed sees another user's post
  ↓
Clicks on username/avatar → /tweet/profile/<username>/
  ↓
Server fetches User object by username
  ↓
Fetches all tweets by that user (ordered newest first)
  ↓
Calculates stats:
  - Tweet count: user.tweet_set.count()
  - Like count: user.liked_tweets.count()
  ↓
Shows profile card with user info, stats, joined date
  ↓
Shows paginated tweets (10 per page)
  ↓
Visitor can:
  - Like tweets
  - Comment on tweets
  - Paginate
  ↓
If visitor clicks on own profile: can also edit/delete own tweets
END
```

---

### Flow 5: Edit Tweet

```
START
User sees their tweet on feed
  ↓
Clicks edit icon → /tweet/<id>/edit/
  ↓
Server checks: Is tweet.user == request.user?
  ├─ NO: 404 error
  └─ YES: Continue
  ↓
Form pre-populated with existing tweet data
  ↓
User modifies text/image
  ↓
POSTs form to /tweet/<id>/edit/
  ↓
Validates: text <= 240 chars
  ↓
Updates tweet in database
  ↓
Redirect to /tweet/
  ↓
Updated tweet now shows in feed
END
```

---

### Flow 6: Delete Tweet

```
START
User sees their tweet on feed
  ↓
Clicks delete icon → /tweet/<id>/delete/
  ↓
Server checks: Is tweet.user == request.user?
  ├─ NO: 404 error
  └─ YES: Show confirmation page
  ↓
Shows "Delete Tweet?" confirmation
  ↓
User confirms (clicks "Yes, Delete Tweet")
  ↓
POSTs to /tweet/<id>/delete/
  ↓
Server deletes tweet from database
  ├─ Cascades: All comments on this tweet are also deleted
  └─ Cascades: All likes on this tweet are also deleted
  ↓
Redirect to /tweet/
  ↓
Tweet is now gone from feed
END
```

---

## KEY FEATURES EXPLAINED

### 1. Authentication System

**Django's Built-in Auth Module**
- Password hashing: PBKDF2 algorithm
- Session management: Server-side sessions in database
- Login decorators: `@login_required` redirects to login page
- View access control: Authorization checks in each view

```python
@login_required
def tweet_create(request):
    # If not logged in: Redirects to /account/login/
    # If logged in: Allows access
```

---

### 2. Cloud Media Handling (Supabase Storage)

**Storage Logic:**
```python
# Models
photo_url = models.URLField(blank=True, null=True)

# Utils (tweet/utils/storage.py)
def upload_to_supabase(file):
    # UUID-renamed file upload to 'tweet-photos' bucket
    # Returns public URL
```

- **Infrastructure:** Moved from local disk storage to cloud-based Supabase Storage.
- **Security:** Files are stored in a dedicated bucket with defined RLS policies.
- **Performance:** Public URLs allow for faster CDN delivery of images.
- **Cleanup:** `delete_from_supabase` is called during tweet deletion or modification to ensure no orphaned files remain.

---

### 11. Admin Panel & User Management (New!)

**Features:**
- **Dashboard:** Real-time stats (Total Users, Tweets, Comments, Likes).
- **User Management:** Searchable list of all registered users with their account status.
- **Security Controls:** Superusers can delete non-admin accounts or reset passwords directly from the dashboard.
- **Authorization:** Protected by `staff_member_required` and explicit `is_superuser` checks.

### 3. Search Functionality

**Query Filtering:**
```python
# Case-insensitive search in text AND username
tweets_list = all_tweets.filter(
    Q(text__icontains=query) |              # icontains = case-insensitive contains
    Q(user__username__icontains=query)      # __ = related field lookup
)
```

- Uses `Q` objects for OR logic (alternative: use pipe `|`)
- `icontains`: Case-insensitive substring search
- `user__username`: Follow foreign key relationship

---

### 4. Pagination

**Batching Results:**
```python
paginator = Paginator(tweets_list, 10)   # 10 items per page
tweets = paginator.get_page(page_number)

# In template:
{% if tweets.has_previous %}
    <a href="?page={{ tweets.previous_page_number }}">Previous</a>
{% endif %}
```

- Pagination prevents loading entire database into memory
- Improves page load time
- Reduces bandwidth usage

---

### 5. Many-to-Many Relationships (Likes)

**M2M via .add() and .remove():**
```python
# Like a tweet
tweet.likes.add(request.user)

# Unlike a tweet
tweet.likes.remove(request.user)

# Check if liked
is_liked = tweet.likes.filter(id=request.user.id).exists()

# Count likes
like_count = tweet.likes.count()
```

- Creates junction table automatically (`tweet_tweet_likes`)
- No explicit model needed
- `related_name='liked_tweets'`: Reverse lookup from user

---

### 6. Database Optimization

**Problem:** N+1 Query Problem
```python
# BAD: Causes many queries
tweets = Tweet.objects.all()
for tweet in tweets:
    print(tweet.user.username)  # 1 query per tweet!
```

**Solution: select_related() & prefetch_related()**
```python
# GOOD: Minimal queries
tweets = Tweet.objects.select_related('user').prefetch_related('likes', 'comments__user')
for tweet in tweets:
    print(tweet.user.username)  # Already loaded
```

- `select_related()`: SQL JOIN (one-to-one, foreign key)
- `prefetch_related()`: Separate queries + Python caching (many-to-many)

---

### 7. Form Validation

**Two-Level Validation:**

**Level 1: Client-Side (HTML)**
```html
<input required type="email" />
<textarea maxlength="240"></textarea>
```

**Level 2: Server-Side (Python)**
```python
class TweetForm(forms.ModelForm):
    # Auto-validates from model
    # text: max_length=240
    # photo: ImageField validation
```

- Client validation: Quick UX feedback
- Server validation: Security (prevent tampering)

---

### 8. CSRF Protection

**Cross-Site Request Forgery Attack:**
- Hacker posts fake form on their site targeting your app
- If user visits, form auto-submits and makes unwanted action

**Django's Protection:**
```html
<form method="post">
    {% csrf_token %}  <!-- Adds hidden token -->
    ...
</form>
```

```python
MIDDLEWARE = [
    'django.middleware.csrf.CsrfViewMiddleware',  # Validates token
]
```

---

### 9. Cascade Deletion

**Automatic Cleanup:**
```python
# When user deleted:
user = models.ForeignKey(User, on_delete=models.CASCADE)
# Delete all their tweets & comments

# When tweet deleted:
tweet = models.ForeignKey(Tweet, ..., on_delete=models.CASCADE)
# Delete all comments on that tweet
```

- Prevents orphaned data
- Maintains referential integrity

---

### 10. Flash Messages

**Temporary User Notifications:**
```python
from django.contrib import messages

messages.success(request, 'Tweet posted successfully!')
```

```html
{% if messages %}
    {% for message in messages %}
        <div class="alert alert-{{ message.tags }}">
            {{ message }}
        </div>
    {% endfor %}
{% endif %}
```

- Stored in session
- Display once, then deleted
- Types: success, error, warning, info

---

## DEPENDENCIES & LIBRARIES

### File: `requirements.txt`

**Core Framework:**
- `Django==6.0` - Web framework
- `asgiref==3.11.1` - ASGI server interface

**Database:**
- `psycopg2-binary==2.9.10` - PostgreSQL adapter
- `dj-database-url==2.3.0` - Parse DATABASE_URL

**Static Files & Web Server:**
- `gunicorn==25.3.0` - Production web server
- `whitenoise==6.9.0` - Serve static files efficiently
- `Werkzeug==3.1.8` - WSGI utilities

**Image Processing:**
- `Pillow==12.1.1` - Image processing library (for ImageField)

**Configuration & Environment:**
- `python-decouple==3.8` - Load environment variables
- `python-dotenv==1.2.2` - Load .env files
- `cryptography==46.0.6` - Cryptographic recipes

**Code Quality:**
- `autopep8==2.3.2` - Auto-format Python code
- `flake8==7.3.0` - Style guide enforcement
- `pycodestyle==2.14.0` - PEP 8 compliance
- `pyflakes==3.4.0` - Logical error detector

**Development Tools:**
- `django-extensions==4.1` - Extra Django command utilities
- `sqlparse==0.5.5` - SQL parser
- `typing_extensions==4.15.0` - Type hint backports

**Security (HTTPS):**
- `pyOpenSSL==26.0.0` - OpenSSL wrapper
- `cffi==2.0.0` - C Foreign Function Interface

---

## CLOUD CONFIGURATION

### Supabase Setup:
1. **Database:** PostgreSQL connection string for Vercel.
2. **Storage:** `tweet-photos` bucket (Public) for user uploads.

### Environment Variables (.env):
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
DATABASE_URL=postgres://...
```

---

## DEPLOYMENT CONFIGURATION

### Vercel Deployment: `vercel.yaml`

```yaml
buildCommand: pip install -r requirements.txt && python manage.py collectstatic --noinput
env:
  SECRET_KEY: @SECRET_KEY
  DATABASE_URL: @DATABASE_URL
  DEBUG: false
```

### Render Deployment: `render.yaml`

Production-ready configuration for Render hosting.

### Heroku/Procfile:

```
web: gunicorn hunain_project.wsgi --log-file -
release: python manage.py migrate
```

---

## ENVIRONMENT VARIABLES

**Required for production (.env file):**
```
SECRET_KEY=your-secret-key-here
DEBUG=False
DATABASE_URL=postgresql://user:pass@host:5432/dbname
ALLOWED_HOSTS=yoursite.com,www.yoursite.com
```

**Optional:**
```
USE_HTTPS_LOCAL=True
VERCEL_URL=https://your-project.vercel.app
```

---

## DATABASE MIGRATIONS

### What are Migrations?

Django tracks database schema changes:

```python
# Migration 0001: Initial schema
python manage.py makemigrations  # Create migration file
python manage.py migrate         # Apply to database

# Migration 0002: Add likes & comments
python manage.py makemigrations
python manage.py migrate
```

### Migration Files:

**0001_initial.py** - Created Tweet table
```python
operations = [
    migrations.CreateModel(
        name='Tweet',
        fields=[
            ('id', models.BigAutoField(primary_key=True)),
            ('text', models.TextFields(max_length=240)),
            ('photo', models.ImageField(upload_to='photos/', blank=True, null=True)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('updated_at', models.DateTimeField(auto_now=True)),
            ('user', models.ForeignKey(to='auth.User', on_delete='CASCADE')),
        ],
    ),
]
```

**0002_tweet_likes_comment.py** - Added likes & comments
```python
operations = [
    migrations.AddField(
        model_name='tweet',
        name='likes',
        field=models.ManyToManyField(to='auth.User', ...),
    ),
    migrations.CreateModel(
        name='Comment',
        fields=[...],
    ),
]
```

---

## SECURITY BEST PRACTICES

✅ **What's Implemented:**
- Password hashing (PBKDF2)
- CSRF tokens on all forms
- SQL injection prevention (ORM)
- XSS protection (Django template auto-escaping)
- Authorization checks (`@login_required`)
- HTTPS support
- Session security
- User input validation on client & server

⚠️ **What's Missing (For Production):**
- Rate limiting on API endpoints
- Logging & monitoring
- Two-factor authentication (2FA)
- API key management for external services
- DDoS protection
- Security headers (CSP, X-Frame-Options)
- File upload virus scanning

---

## QUICK REFERENCE

### Running Locally:
```bash
# Activate virtual environment
source sandbox_venv/bin/activate

# Run development server
python manage.py runserver

# Access at http://localhost:8000
```

### Creating Superuser:
```bash
python manage.py createsuperuser
# Access admin at http://localhost:8000/admin/
```

### Database Commands:
```bash
# Create migrations from model changes
python manage.py makemigrations

# Apply migrations to database
python manage.py migrate

# View migration status
python manage.py showmigrations
```

### Collecting Static Files (Production):
```bash
python manage.py collectstatic --noinput
# Collects CSS/JS to staticfiles/ folder
```

---

## TESTING SUITE

### File: `tweet/tests.py`

Comprehensive unit tests to ensure application stability and security.

**Categories:**
- **Auth:** Registration flow and login requirements.
- **CRUD:** Tweet creation (with/without images), editing, and deletion.
- **Interactions:** Like/unlike toggles and comment posting.
- **Authorization:** Verification that only owners can edit/delete their tweets.
- **Storage:** Mocked Supabase integration to test URL handling.

---

## KEY FEATURES EXPLAINED

### 1. PostgreSQL Full-Text Search
- **Technology:** uses Django's `SearchVector`, `SearchQuery`, and `SearchRank`.
- **Logic:** Searches both tweet text (weighted higher) and usernames.
- **Fallback:** Gracefully falls back to `icontains` for local development on SQLite.

### 2. Rate Limiting (Anti-Spam)
- **Library:** `django-ratelimit`
- **Rules:**
  - Tweet Creation: 10 per hour
  - Liking: 30 per hour
  - Commenting: 20 per hour
- **Benefit:** Prevents bot spam and infrastructure abuse.

### 3. Real-time Interactions
- **Mechanism:** Hybrid AJAX system for immediate UI feedback.
- **Implementation:** Custom JavaScript handles "Likes" and "Comments" without reloading the feed.
- **Future Growth:** Template prepared for **Supabase Realtime** Postgres Change listeners.

### 4. Image Upload Logic
- **UI:** Client-side image preview with removal option.
- **Validation:** Type (JPEG/PNG/WebP/GIF) and Size (5MB) enforcement.
- **Cleanup:** Orphaned file deletion on tweet modification or removal.

---

## END OF DOCUMENTATION

This document covers every aspect of your Tweetbar project with detailed explanations of:
- ✅ Architecture and project structure
- ✅ Complete database schema with relationships
- ✅ Every Django setting and what it does
- ✅ All URL routes and their purposes
- ✅ Model definitions and field choices
- ✅ Form validation logic
- ✅ View functions with flow explanation
- ✅ Template rendering and template tags
- ✅ Complete user flows and workflows
- ✅ Key features with code examples
- ✅ Dependencies and what each does

You now have a complete reference guide to understand and maintain this application!

---

**Merged Addendum — Improvements & Quick Tests (April 12, 2026)**

The following sections consolidate recent improvement notes, the fix report, and the quick test checklist into this single canonical documentation file. The standalone files `IMPROVEMENTS_SUMMARY.md`, `DELETE_BUTTONS_FIX_REPORT.md`, and `QUICK_TEST_CHECKLIST.md` were merged here and removed from the repository to avoid duplication.

- **Critical fixes included:** Admin delete modal buttons made clickable (z-index and button CSS fixes), comprehensive white-text visibility rules, styled and optimized tweet view-counts, DB query optimizations (select_related/prefetch/only), and caching for admin stats and notification counts.
- **Primary files changed during fixes:** `static/css/style.css`, `tweet/views.py`, `tweet/templates/tweet_list.html`.
- **How to run quick verification (local):**
    1. Activate venv: `source sandbox_venv/bin/activate`
    2. Run system check: `python manage.py check` (should report no issues)
    3. Start dev server with local certs: `python manage.py runserver_plus --cert-file certs/127.0.0.1+localhost.pem --key-file certs/127.0.0.1+localhost-key.pem 8004`
    4. Open: `https://127.0.0.1:8004/tweet/admin/users/` and exercise the Delete modal per checklist.

If you need separate exported copies of the change reports or the quick checklist, I can recreate them on demand, but keeping a single source of truth avoids fragmentation.

---

Generated/Merged: April 12, 2026

