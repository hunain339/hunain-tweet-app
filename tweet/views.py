from django.shortcuts import render, get_object_or_404, redirect
from .models import Tweet, Comment, Notification
from .forms import TweetForm, UserRegistrationForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import Q, Count, F, Prefetch
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from .utils.storage import upload_to_supabase, delete_from_supabase
from django.core.exceptions import ValidationError
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django_ratelimit.decorators import ratelimit
import secrets

# ─────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────


# ─────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────

def _full_text_search(queryset, query):
    """
    PostgreSQL Full-Text Search with ranking.
    Falls back gracefully to icontains when the DB doesn't support FTS
    (e.g. local SQLite during development).
    """
    try:
        from django.contrib.postgres.search import (
            SearchVector, SearchQuery, SearchRank
        )
        vector = SearchVector('text', weight='A') + SearchVector('user__username', weight='B')
        search_query = SearchQuery(query)
        return (
            queryset
            .annotate(rank=SearchRank(vector, search_query))
            .filter(rank__gt=0.01)
            .order_by('-rank')
        )
    except Exception:
        # Fallback for SQLite / missing pg extension
        return queryset.filter(
            Q(text__icontains=query) | Q(user__username__icontains=query)
        )


# ─────────────────────────────────────────────────────────────
#  Public views
# ─────────────────────────────────────────────────────────────

def index(request):
    return redirect('tweet_list')


def tweet_list(request):
    query = request.GET.get('q', '').strip()

    # ──────────────────────────────────────────────────────────
    # OPTIMIZE: Use select_related + prefetch_related for efficient loading
    # Fetch only needed fields with only() and defer() for further optimization
    # ──────────────────────────────────────────────────────────
    
    comments_qs = (
        Comment.objects
        .select_related('user')
        .prefetch_related('replies__user')
        .only('id', 'text', 'created_at', 'user__username', 'user__id', 'tweet_id')
    )
    
    base_qs = (
        Tweet.objects
        .select_related('user')
        .prefetch_related(
            'likes',
            Prefetch('comments', queryset=comments_qs),
        )
        .only('id', 'user__id', 'user__username', 'text', 'photo_url', 'created_at', 'view_count')
        .order_by('-created_at')
    )

    if query:
        tweets_list = _full_text_search(base_qs, query)
    else:
        tweets_list = base_qs

    paginator = Paginator(tweets_list, 10)
    page_number = request.GET.get('page')
    tweets = paginator.get_page(page_number)

    # ──────────────────────────────────────────────────────────
    # OPTIMIZE: Track views more efficiently using session + batch updates
    # Only increment views for authenticated users (prevents spam)
    # ──────────────────────────────────────────────────────────
    if request.user.is_authenticated:
        # Collect viewed tweets to minimize database writes
        tweet_ids_to_update = []
        for tweet in tweets:
            session_key = f'viewed_tweet_{tweet.id}'
            if not request.session.get(session_key, False):
                tweet_ids_to_update.append(tweet.id)
                request.session[session_key] = True
        
        # Batch update view counts with a single query
        if tweet_ids_to_update:
            Tweet.objects.filter(id__in=tweet_ids_to_update).update(
                view_count=F('view_count') + 1
            )

    return render(request, 'tweet_list.html', {
        'tweets': tweets,
        'query': query,
    })


# ─────────────────────────────────────────────────────────────
#  Tweet CRUD
# ─────────────────────────────────────────────────────────────

@ratelimit(key='user', rate='10/h', block=True)
@login_required
@login_required
def tweet_create(request):
    if request.method == 'POST':
        form = TweetForm(request.POST, request.FILES)
        if form.is_valid():
            tweet = form.save(commit=False)
            tweet.user = request.user

            photo = form.cleaned_data.get('photo')
            if photo:
                try:
                    tweet.photo_url = upload_to_supabase(photo)
                except ValidationError as exc:
                    # Handle Django ValidationError properly
                    if hasattr(exc, 'message'):
                        error_msg = exc.message
                    elif hasattr(exc, 'messages') and exc.messages:
                        error_msg = exc.messages[0] if isinstance(exc.messages, list) else str(exc.messages)
                    else:
                        error_msg = str(exc)
                    messages.error(request, error_msg)
                    return render(request, 'tweet_form.html', {'form': form, 'action': 'create'})
                except Exception:
                    messages.error(
                        request,
                        'Image upload failed due to a network error. Please try again.'
                    )
                    return render(request, 'tweet_form.html', {'form': form, 'action': 'create'})

            tweet.save()
            messages.success(request, 'Tweet posted successfully! 🎉')
            return redirect('tweet_list')
    else:
        form = TweetForm()

    return render(request, 'tweet_form.html', {'form': form, 'action': 'create'})


@login_required
def edit_tweet(request, tweet_id):
    tweet = get_object_or_404(Tweet, pk=tweet_id, user=request.user)

    if request.method == 'POST':
        form = TweetForm(request.POST, request.FILES, instance=tweet)
        if form.is_valid():
            updated_tweet = form.save(commit=False)

            photo = form.cleaned_data.get('photo')
            if photo:
                try:
                    # Delete the old image from Supabase before uploading the new one
                    if tweet.photo_url:
                        delete_from_supabase(tweet.photo_url)
                    updated_tweet.photo_url = upload_to_supabase(photo)
                except ValidationError as exc:
                    # Handle Django ValidationError properly
                    if hasattr(exc, 'message'):
                        error_msg = exc.message
                    elif hasattr(exc, 'messages') and exc.messages:
                        error_msg = exc.messages[0] if isinstance(exc.messages, list) else str(exc.messages)
                    else:
                        error_msg = str(exc)
                    messages.error(request, error_msg)
                    return render(request, 'tweet_form.html', {
                        'form': form,
                        'tweet': tweet,
                        'action': 'edit',
                    })
                except Exception:
                    messages.error(
                        request,
                        'Image upload failed due to a network error. The tweet text was not saved. Please try again.'
                    )
                    return render(request, 'tweet_form.html', {
                        'form': form,
                        'tweet': tweet,
                        'action': 'edit',
                    })

            updated_tweet.save()
            messages.success(request, 'Tweet updated successfully! ✅')
            return redirect('tweet_list')
    else:
        form = TweetForm(instance=tweet)

    return render(request, 'tweet_form.html', {
        'form': form,
        'tweet': tweet,
        'action': 'edit',
    })


@login_required
def tweet_delete(request, tweet_id):
    tweet = get_object_or_404(Tweet, pk=tweet_id, user=request.user)

    if request.method == 'POST':
        if tweet.photo_url:
            try:
                delete_from_supabase(tweet.photo_url)
            except Exception:
                pass  # Don't block deletion even if Storage cleanup fails
        tweet.delete()
        messages.success(request, 'Tweet deleted.')
        return redirect('tweet_list')

    return render(request, 'tweet_confirm_delete.html', {'tweet': tweet})


# ─────────────────────────────────────────────────────────────
#  Auth
# ─────────────────────────────────────────────────────────────

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'Welcome to Tweetbar, @{user.username}! 🚀')
            return redirect('tweet_list')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


# ─────────────────────────────────────────────────────────────
#  Social interactions
# ─────────────────────────────────────────────────────────────

@ratelimit(key='user', rate='30/h', block=True)
@login_required
def tweet_like(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id)
    if tweet.likes.filter(id=request.user.id).exists():
        tweet.likes.remove(request.user)
    else:
        tweet.likes.add(request.user)

    # AJAX-friendly: return JSON when request expects it
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'liked': tweet.likes.filter(id=request.user.id).exists(),
            'count': tweet.likes.count(),
        })
    return redirect('tweet_list')


@ratelimit(key='user', rate='20/h', block=True)
@login_required
def add_comment(request, tweet_id):
    """
    Add a comment to a tweet with support for nested replies.
    Creates notifications for the tweet author.
    """
    tweet = get_object_or_404(Tweet, id=tweet_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.tweet = tweet
            comment.user = request.user
            
            # Handle replies (nested comments)
            parent_id = request.POST.get('parent_id')
            if parent_id:
                try:
                    parent = Comment.objects.get(id=parent_id, tweet=tweet)
                    comment.parent = parent
                except Comment.DoesNotExist:
                    pass
            
            comment.save()
            messages.success(request, 'Comment added! 💬')

            # Create notification for tweet author if comment is by another user
            if request.user != tweet.user:
                notification_type = 'reply' if comment.parent else 'comment'
                Notification.objects.create(
                    user=tweet.user,
                    comment=comment,
                    notification_type=notification_type,
                )
            
            # Create notification for parent comment author (if reply)
            if comment.parent and request.user != comment.parent.user:
                Notification.objects.create(
                    user=comment.parent.user,
                    comment=comment,
                    notification_type='reply',
                )

            # AJAX-friendly response
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'username': comment.user.username,
                    'text': comment.text,
                    'count': tweet.comments.count(),
                    'comment_id': comment.id,
                })
    return redirect('tweet_list')


# ─────────────────────────────────────────────────────────────
#  Profile
# ─────────────────────────────────────────────────────────────

def user_profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    
    # OPTIMIZE: Use select_related + prefetch_related efficiently
    tweets_list = (
        Tweet.objects
        .filter(user=profile_user)
        .select_related('user')
        .prefetch_related(
            Prefetch(
                'comments',
                queryset=Comment.objects.select_related('user').prefetch_related('replies__user')
            ),
            'likes'
        )
        .only('id', 'user_id', 'user__username', 'text', 'photo_url', 
              'created_at', 'view_count', 'updated_at')
        .order_by('-created_at')
    )
    paginator = Paginator(tweets_list, 10)
    tweets = paginator.get_page(request.GET.get('page'))

    return render(request, 'profile.html', {
        'profile_user': profile_user,
        'tweets': tweets,
    })


# ─────────────────────────────────────────────────────────────
#  Admin Dashboard (superuser only)
# ─────────────────────────────────────────────────────────────

@staff_member_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden('Access denied.')

    # OPTIMIZE: Cache expensive statistics for 1 hour
    cache_key = 'admin_dashboard_stats'
    stats = cache.get(cache_key)
    
    if stats is None:
        stats = {
            'total_users':    User.objects.count(),
            'total_tweets':   Tweet.objects.count(),
            'total_comments': Comment.objects.count(),
            'total_likes':    Tweet.objects.aggregate(n=Count('likes', distinct=True))['n'] or 0,
            'active_users':   User.objects.filter(is_active=True).count(),
            'staff_users':    User.objects.filter(is_staff=True).count(),
        }
        # Cache for 1 hour (3600 seconds)
        cache.set(cache_key, stats, 3600)

    # OPTIMIZE: Cache top users for 30 minutes (less frequently accessed)
    top_users_cache_key = 'admin_dashboard_top_users'
    top_users = cache.get(top_users_cache_key)
    
    if top_users is None:
        top_users = (
            User.objects
            .annotate(tweet_count=Count('tweet_set'))
            .only('id', 'username', 'email')
            .order_by('-tweet_count')[:5]
        )
        # Convert to list to cache properly
        top_users = list(top_users)
        cache.set(top_users_cache_key, top_users, 1800)  # 30 minutes

    # Recent data is not cached (always fresh)
    recent_tweets = (
        Tweet.objects
        .select_related('user')
        .prefetch_related('likes', 'comments')
        .only('id', 'user_id', 'user__username', 'text', 'created_at', 'view_count')
        .order_by('-created_at')[:10]
    )
    recent_users = User.objects.only('id', 'username', 'email', 'date_joined').order_by('-date_joined')[:5]

    return render(request, 'admin_dashboard.html', {
        'stats':         stats,
        'recent_tweets': recent_tweets,
        'recent_users':  recent_users,
        'top_users':     top_users,
    })


@staff_member_required
def admin_users(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden('Access denied.')

    query = request.GET.get('q', '').strip()
    role_filter = request.GET.get('role', '')

    # OPTIMIZE: Use only() to select specific fields
    users_list = (
        User.objects
        .annotate(tweet_count=Count('tweet_set'))
        .only('id', 'username', 'email', 'is_superuser', 'is_staff', 'is_active', 'date_joined')
        .order_by('-date_joined')
    )

    if query:
        users_list = users_list.filter(
            Q(username__icontains=query) | Q(email__icontains=query)
        )

    if role_filter == 'superuser':
        users_list = users_list.filter(is_superuser=True)
    elif role_filter == 'staff':
        users_list = users_list.filter(is_staff=True, is_superuser=False)
    elif role_filter == 'user':
        users_list = users_list.filter(is_staff=False, is_superuser=False)

    paginator = Paginator(users_list, 20)
    users = paginator.get_page(request.GET.get('page'))

    return render(request, 'admin_users.html', {
        'users':       users,
        'query':       query,
        'role_filter': role_filter,
        'total_count': users_list.count(),
    })


@staff_member_required
def admin_user_delete(request, user_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden('Access denied.')

    if request.method == 'POST':
        user_to_delete = get_object_or_404(User, pk=user_id)
        if user_to_delete.is_superuser:
            messages.error(request, 'Cannot delete a superuser account.')
        else:
            username = user_to_delete.username
            user_to_delete.delete()
            messages.success(request, f'User @{username} has been permanently deleted.')
    return redirect('admin_users')


@staff_member_required
def admin_reset_password(request, user_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden('Access denied.')

    user_to_reset = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        new_password = secrets.token_urlsafe(12)
        user_to_reset.set_password(new_password)
        user_to_reset.save()
        messages.success(
            request,
            f'Password reset for @{user_to_reset.username}. '
            f'New temporary password: {new_password}'
        )
        return redirect('admin_users')

    return render(request, 'admin_reset_password_confirm.html', {
        'user_to_reset': user_to_reset,
    })


# ─────────────────────────────────────────────────────────────
#  Notifications
# ─────────────────────────────────────────────────────────────

@login_required
def notifications(request):
    """
    Display user notifications for comments and replies on their tweets.
    OPTIMIZED: Uses select_related for efficient loading + caching for unread count.
    """
    # OPTIMIZE: select_related instead of multiple queries
    notifications_list = (
        Notification.objects
        .filter(user=request.user)
        .select_related('comment__user', 'comment__tweet__user')
        .only('id', 'user_id', 'comment_id', 'notification_type', 'is_read', 'created_at',
              'comment__id', 'comment__text', 'comment__user__username',
              'comment__tweet__id', 'comment__tweet__text')
        .order_by('-created_at')
    )
    
    paginator = Paginator(notifications_list, 15)
    page_number = request.GET.get('page')
    notifications_page = paginator.get_page(page_number)
    
    # OPTIMIZE: Cache unread count for this user (invalidated when marking as read)
    unread_cache_key = f'notifications_unread_{request.user.id}'
    unread_count = cache.get(unread_cache_key)
    
    if unread_count is None:
        unread_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        cache.set(unread_cache_key, unread_count, 300)  # Cache for 5 minutes
    
    return render(request, 'notifications.html', {
        'notifications': notifications_page,
        'unread_count': unread_count,
    })


@login_required
def mark_notification_as_read(request, notification_id):
    """
    Mark a single notification as read (AJAX endpoint).
    Invalidates cache for unread count.
    """
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    
    # OPTIMIZE: Invalidate cache when notification is marked as read
    unread_cache_key = f'notifications_unread_{request.user.id}'
    cache.delete(unread_cache_key)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'unread_count': Notification.objects.filter(
                user=request.user,
                is_read=False
            ).count(),
        })
    return redirect('notifications')


@login_required
def mark_all_notifications_as_read(request):
    """
    Mark all notifications as read (AJAX endpoint).
    Invalidates cache for unread count.
    """
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    
    # OPTIMIZE: Invalidate cache when notifications are marked as read
    unread_cache_key = f'notifications_unread_{request.user.id}'
    cache.delete(unread_cache_key)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    return redirect('notifications')


@login_required
def unread_notification_count(request):
    """
    Get unread notification count via AJAX (for navbar updates).
    Uses cache for performance.
    """
    # OPTIMIZE: Use cache for frequently accessed unread count
    unread_cache_key = f'notifications_unread_{request.user.id}'
    count = cache.get(unread_cache_key)
    
    if count is None:
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        cache.set(unread_cache_key, count, 300)  # Cache for 5 minutes
    
    return JsonResponse({'count': count})
