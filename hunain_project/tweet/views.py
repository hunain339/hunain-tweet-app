from django.shortcuts import render, get_object_or_404, redirect
from .models import Tweet, Comment
from .forms import TweetForm, UserRegistrationForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator

# Create your views here.


def index(request):
    return render(request, 'index.html')


def tweet_list(request):
    query = request.GET.get('q')
    
    # Optimization: Use select_related and prefetch_related for optimal query performance
    all_tweets = Tweet.objects.select_related('user').prefetch_related(
        'likes', 
        'comments__user'
    ).order_by('-created_at')

    if query:
        tweets_list = all_tweets.filter(
            Q(text__icontains=query) | Q(user__username__icontains=query)
        )
    else:
        tweets_list = all_tweets

    paginator = Paginator(tweets_list, 10)  # Show 10 tweets per page
    page_number = request.GET.get('page')
    tweets = paginator.get_page(page_number)
    
    return render(request, 'tweet_list.html', {'tweets': tweets})


@login_required
def tweet_create(request):
    if request.method == 'POST':
        form = TweetForm(request.POST, request.FILES)
        if form.is_valid():
            tweet = form.save(commit=False)
            tweet.user = request.user
            tweet.save()
            messages.success(request, 'Tweet posted successfully!')
            return redirect('tweet_list')
    else:
        form = TweetForm()

    return render(request, 'tweet_form.html', {'form': form})


@login_required
def edit_tweet(request, tweet_id):
    tweet = get_object_or_404(Tweet, pk=tweet_id, user=request.user)
    if request.method == 'POST':
        form = TweetForm(request.POST, request.FILES, instance=tweet)
        if form.is_valid():
            tweet = form.save(commit=False)
            tweet.user = request.user
            tweet.save()
            messages.success(request, 'Tweet updated successfully!')
            return redirect('tweet_list')
    else:
        form = TweetForm(instance=tweet)
    return render(request, 'tweet_form.html', {'form': form})


@login_required
def tweet_delete(request, tweet_id):
    tweet = get_object_or_404(Tweet, pk=tweet_id, user=request.user)
    if request.method == 'POST':
        tweet.delete()
        messages.success(request, 'Tweet deleted!')
        return redirect('tweet_list')
    return render(request, 'tweet_confirm_delete.html', {'tweet': tweet})


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'Welcome to Tweetbar, {user.username}!')
            return redirect('tweet_list')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def tweet_like(request, tweet_id):
    tweet = get_object_or_404(Tweet, id=tweet_id)
    if tweet.likes.filter(id=request.user.id).exists():
        tweet.likes.remove(request.user)
    else:
        tweet.likes.add(request.user)
    return redirect('tweet_list')


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
            messages.success(request, 'Comment added!')
    return redirect('tweet_list')


def user_profile(request, username):
    # Optimization: Use select_related and prefetch_related for profile view
    user = get_object_or_404(User, username=username)
    tweets_list = Tweet.objects.filter(user=user).select_related('user').prefetch_related(
        'likes', 
        'comments__user'
    ).order_by('-created_at')
    
    paginator = Paginator(tweets_list, 10)
    page_number = request.GET.get('page')
    tweets = paginator.get_page(page_number)
    
    return render(request, 'profile.html', {'profile_user': user, 'tweets': tweets})
