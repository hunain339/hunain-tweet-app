"""
Service layer for Tweet domain logic.

All write operations and side-effects should live here. Services are
transactional and responsible for cache invalidation and calling
external systems (storage, notifications).
"""

from django.db import transaction
from django.db.models import F
from ..models import Tweet
from ..utils.storage import delete_from_supabase
from ..cache_utils import invalidate_tweet_cache, invalidate_user_cache


class TweetService:
    @staticmethod
    @transaction.atomic
    def create_tweet(user, text, photo_file=None):
        tweet = Tweet.objects.create(user=user, text=text)
        if photo_file:
            # Resolve uploader dynamically so tests can patch `tweet.views.upload_to_supabase`
            try:
                from importlib import import_module

                tweet_views = import_module("tweet.views")
                uploader = getattr(tweet_views, "upload_to_supabase", None)
            except Exception:
                uploader = None
            if not uploader:
                from ..utils.storage import upload_to_supabase as uploader
            url = uploader(photo_file)
            tweet.photo_url = url
            tweet.save(update_fields=["photo_url"])

        # Invalidate caches dependent on tweets
        invalidate_tweet_cache(tweet.id)
        invalidate_user_cache(user.id)
        return tweet

    @staticmethod
    @transaction.atomic
    def update_tweet(tweet, user, text=None, photo_file=None):
        if tweet.user != user:
            raise PermissionError("Not the owner")

        changed = False
        if text is not None and text != tweet.text:
            tweet.text = text
            changed = True

        if photo_file:
            # Replace photo atomically
            if tweet.photo_url:
                try:
                    delete_from_supabase(tweet.photo_url)
                except Exception:
                    pass
            # Resolve uploader dynamically so tests can patch `tweet.views.upload_to_supabase`
            try:
                from importlib import import_module

                tweet_views = import_module("tweet.views")
                uploader = getattr(tweet_views, "upload_to_supabase", None)
            except Exception:
                uploader = None
            if not uploader:
                from ..utils.storage import upload_to_supabase as uploader
            url = uploader(photo_file)
            tweet.photo_url = url
            changed = True

        if changed:
            tweet.save()
            invalidate_tweet_cache(tweet.id)

        return tweet

    @staticmethod
    @transaction.atomic
    def delete_tweet(tweet, user):
        if tweet.user != user:
            raise PermissionError("Not the owner")

        # Attempt to delete storage but don't block
        if tweet.photo_url:
            try:
                delete_from_supabase(tweet.photo_url)
            except Exception:
                pass

        tweet_id = tweet.id
        user_id = tweet.user.id
        tweet.delete()
        invalidate_tweet_cache(tweet_id)
        invalidate_user_cache(user_id)

    @staticmethod
    @transaction.atomic
    def toggle_like(tweet, user):
        if tweet.likes.filter(pk=user.pk).exists():
            tweet.likes.remove(user)
            liked = False
        else:
            tweet.likes.add(user)
            liked = True

        # Update like counts via annotation; invalidate caches
        invalidate_tweet_cache(tweet.id)
        return liked

    @staticmethod
    def increment_views_batch(user, tweet_ids):
        # Only increment for authenticated users; batch update
        if not user or not user.is_authenticated:
            return
        if not tweet_ids:
            return
        Tweet.objects.filter(id__in=tweet_ids).update(view_count=F("view_count") + 1)
        for tid in tweet_ids:
            invalidate_tweet_cache(tid)
