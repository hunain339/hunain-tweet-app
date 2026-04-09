from django.shortcuts import render, get_object_or_404, redirect
from .models import Tweet, Comment
from .forms import TweetForm, UserRegistrationForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from .utils.storage import upload_to_supabase, delete_from_supabase
from django.core.exceptions import ValidationError
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_POST
from ratelimit.decorators import ratelimit
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

    base_qs = Tweet.objects.select_related('user').prefetch_related(
        'likes',
        'comments__user',
    ).order_by('-created_at')

    if query:
        tweets_list = _full_text_search(base_qs, query)
    else:
        tweets_list = base_qs

    paginator = Paginator(tweets_list, 10)
    page_number = request.GET.get('page')
    tweets = paginator.get_page(page_number)

    return render(request, 'tweet_list.html', {
        'tweets': tweets,
        'query': query,
    })


# ─────────────────────────────────────────────────────────────
#  Tweet CRUD
# ─────────────────────────────────────────────────────────────

@ratelimit(key='user', rate='10/h', block=True)
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
                    messages.error(request, str(exc.message))
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
                    messages.error(request, str(exc.message))
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
    tweet = get_object_or_404(Tweet, id=tweet_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.tweet = tweet
            comment.user = request.user
            comment.save()
            messages.success(request, 'Comment added! 💬')

            # AJAX-friendly response
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'username': comment.user.username,
                    'text': comment.text,
                    'count': tweet.comments.count(),
                })
    return redirect('tweet_list')


# ─────────────────────────────────────────────────────────────
#  Profile
# ─────────────────────────────────────────────────────────────

def user_profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    tweets_list = (
        Tweet.objects
        .filter(user=profile_user)
        .select_related('user')
        .prefetch_related('likes', 'comments__user')
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

    stats = {
        'total_users':    User.objects.count(),
        'total_tweets':   Tweet.objects.count(),
        'total_comments': Comment.objects.count(),
        'total_likes':    Tweet.objects.aggregate(n=Count('likes'))['n'] or 0,
        # Extra sparkline data
        'active_users':   User.objects.filter(is_active=True).count(),
        'staff_users':    User.objects.filter(is_staff=True).count(),
    }

    recent_tweets = (
        Tweet.objects
        .select_related('user')
        .prefetch_related('likes', 'comments')
        .order_by('-created_at')[:10]
    )
    recent_users = User.objects.order_by('-date_joined')[:5]

    # Top tweeters
    top_users = (
        User.objects
        .annotate(tweet_count=Count('tweet'))
        .order_by('-tweet_count')[:5]
    )

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

    users_list = User.objects.annotate(tweet_count=Count('tweet')).order_by('-date_joined')

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
