"""
Query Optimization Module for Tweet API

This module provides optimized querysets that minimize database queries
using select_related, prefetch_related, only(), and annotations.

Performance improvements:
- Reduced N+1 queries through intelligent prefetching
- Limited field selection with .only() for list views
- Annotated aggregates instead of .count() method calls
- Organized by use case for clarity and maintainability
"""

from django.db.models import Prefetch, Count, Q, F, Exists, OuterRef
from django.db.models.functions import Coalesce
from .models import Tweet, Comment


class OptimizedTweetQueries:
    """
    High-performance querysets for Tweet retrieval.
    Each method is optimized for a specific use case.
    """

    @staticmethod
    def get_tweets_for_list(user=None):
        """
        Optimized queryset for tweet list view (paginated).
        
        Performance:
        - Uses select_related for user data (1 query)
        - Annotates is_liked status using Subquery (SQL level)
        - Annotates counts to avoid N+1 (no extra queries)
        - Only fetches necessary fields
        """
        queryset = Tweet.objects.select_related('user')
        
        if user and user.is_authenticated:
            is_liked = Exists(
                Tweet.objects.filter(id=OuterRef('pk'), likes=user)
            )
            queryset = queryset.annotate(is_liked_by_user=is_liked)
        else:
            queryset = queryset.annotate(is_liked_by_user=F('id') == -1) # False

        return (
            queryset
            .annotate(likes_count=Count('likes', distinct=True))
            .annotate(comments_count=Count('comments', distinct=True))
            .only(
                'id', 'text', 'photo_url', 'created_at', 'updated_at',
                'view_count', 'user__id', 'user__username', 'user__first_name',
                'user__last_name'
            )
            .order_by('-created_at')
        )

    @staticmethod
    def get_tweets_for_detail():
        """
        Optimized queryset for single tweet detail view.
        
        Performance:
        - Uses select_related for user (1 query)
        - Uses prefetch_related for likes (1 query)
        - Uses prefetch_related for nested comments with their users (1 query)
        - Fetches all necessary data including comments
        
        Typical query count: 3-4 queries per request
        """
        # Optimize comments query
        comments_queryset = (
            Comment.objects
            .select_related('user')
            .prefetch_related('replies__user')
            .order_by('created_at')
        )

        return (
            Tweet.objects
            .select_related('user')
            .prefetch_related(
                'likes',
                Prefetch('comments', queryset=comments_queryset)
            )
            .annotate(likes_count=Count('likes', distinct=True))
            .annotate(comments_count=Count('comments', distinct=True))
            .only(
                'id', 'text', 'photo_url', 'created_at', 'updated_at',
                'view_count', 'user__id', 'user__username', 'user__first_name',
                'user__last_name'
            )
        )

    @staticmethod
    def get_tweets_by_user(user_id):
        """
        Optimized queryset for tweets by specific user.
        
        Performance:
        - Filters at queryset level before fetching
        - Uses select_related and prefetch_related
        - Minimal field selection
        
        Args:
            user_id: Primary key of the user
            
        Typical query count: 2-3 queries per request (paginated)
        """
        return (
            Tweet.objects
            .filter(user_id=user_id)
            .select_related('user')
            .prefetch_related('likes')
            .annotate(likes_count=Count('likes', distinct=True))
            .annotate(comments_count=Count('comments', distinct=True))
            .only(
                'id', 'text', 'photo_url', 'created_at', 'updated_at',
                'view_count', 'user__id', 'user__username'
            )
            .order_by('-created_at')
        )

    @staticmethod
    def get_tweets_with_photos():
        """
        Optimized queryset for tweets that contain photos.
        
        Performance:
        - Filters at database level (excludes null photo_url)
        - Minimal queries through prefetch optimization
        
        Typical query count: 2-3 queries per request (paginated)
        """
        return (
            Tweet.objects
            .filter(photo_url__isnull=False)
            .select_related('user')
            .prefetch_related('likes')
            .annotate(likes_count=Count('likes', distinct=True))
            .annotate(comments_count=Count('comments', distinct=True))
            .only(
                'id', 'text', 'photo_url', 'created_at', 'updated_at',
                'view_count', 'user__id', 'user__username'
            )
            .order_by('-created_at')
        )

    @staticmethod
    def get_tweets_by_date_range(start_date, end_date):
        """
        Optimized queryset for tweets within a date range.
        
        Performance:
        - Date filtering at database level
        - Efficient prefetching
        
        Args:
            start_date: ISO format date string (e.g., '2026-01-01')
            end_date: ISO format date string (e.g., '2026-12-31')
            
        Typical query count: 2-3 queries per request (paginated)
        """
        return (
            Tweet.objects
            .filter(created_at__gte=start_date, created_at__lte=end_date)
            .select_related('user')
            .prefetch_related('likes')
            .annotate(likes_count=Count('likes', distinct=True))
            .annotate(comments_count=Count('comments', distinct=True))
            .only(
                'id', 'text', 'photo_url', 'created_at', 'updated_at',
                'view_count', 'user__id', 'user__username'
            )
            .order_by('-created_at')
        )


class OptimizedCommentQueries:
    """High-performance querysets for Comment retrieval."""

    @staticmethod
    def get_comments_for_tweet(tweet_id):
        """
        Optimized queryset for comments on a specific tweet.
        
        Performance:
        - Uses select_related for user data
        - Uses prefetch_related for nested replies
        
        Typical query count: 2 queries
        """
        replies_queryset = (
            Comment.objects
            .select_related('user')
            .order_by('created_at')
        )

        return (
            Comment.objects
            .filter(tweet_id=tweet_id, parent__isnull=True)
            .select_related('user')
            .prefetch_related(Prefetch('replies', queryset=replies_queryset))
            .only(
                'id', 'text', 'created_at', 'user__id', 'user__username',
                'tweet_id'
            )
            .order_by('created_at')
        )


# Aggregate statistics queries
class AggregateStatistics:
    """Database-level aggregate calculations for efficiency."""

    @staticmethod
    def get_tweet_stats(tweet_id):
        """
        Get all statistics for a tweet using single database query.
        
        Returns:
            Dictionary with likes_count, comments_count, total_engagement
        """
        stats = (
            Tweet.objects
            .filter(id=tweet_id)
            .annotate(
                likes_count=Count('likes', distinct=True),
                comments_count=Count('comments', distinct=True),
            )
            .annotate(
                total_engagement=F('likes_count') + F('comments_count') + F('view_count')
            )
            .values('likes_count', 'comments_count', 'total_engagement')
            .first()
        )
        return stats or {
            'likes_count': 0,
            'comments_count': 0,
            'total_engagement': 0
        }

    @staticmethod
    def get_popular_tweets(limit=10):
        """
        Get most engaged tweets using database-level aggregation.
        
        Performance:
        - Single query with annotation
        - Efficient sorting by engagement
        """
        return (
            Tweet.objects
            .annotate(
                likes_count=Count('likes', distinct=True),
                comments_count=Count('comments', distinct=True),
                total_engagement=F('view_count') + Count('likes') + Count('comments')
            )
            .select_related('user')
            .only(
                'id', 'text', 'photo_url', 'created_at', 'user__id',
                'user__username', 'view_count'
            )
            .filter(total_engagement__gt=0)
            .order_by('-total_engagement')[:limit]
        )
