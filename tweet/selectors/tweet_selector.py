"""
Query Optimization Module (selectors.tweet_selector)

This module provides optimized querysets that minimize database queries
using select_related, prefetch_related, only(), and annotations.

Selectors are the single place for read/query logic. Services should call
these functions/classes to obtain QuerySets or annotated values.
"""

from django.db.models import Prefetch, Count, F, Exists, OuterRef, Value, BooleanField
from ..models import Tweet, Comment


class OptimizedTweetQueries:
    """
    High-performance querysets for Tweet retrieval.
    """

    @staticmethod
    def get_tweets_for_list(user=None):
        queryset = Tweet.objects.select_related("user")

        if user and user.is_authenticated:
            is_liked = Exists(Tweet.objects.filter(id=OuterRef("pk"), likes=user))
            queryset = queryset.annotate(is_liked_by_user=is_liked)
        else:
            # Annotate a constant False using a database expression
            queryset = queryset.annotate(
                is_liked_by_user=Value(False, output_field=BooleanField())
            )

        return (
            queryset.annotate(likes_count=Count("likes", distinct=True))
            .annotate(comments_count=Count("comments", distinct=True))
            .only(
                "id",
                "text",
                "photo_url",
                "created_at",
                "updated_at",
                "view_count",
                "user__id",
                "user__username",
                "user__first_name",
                "user__last_name",
            )
            .order_by("-created_at")
        )

    @staticmethod
    def get_tweets_for_detail():
        comments_queryset = (
            Comment.objects.select_related("user")
            .prefetch_related("replies__user")
            .order_by("created_at")
        )

        return (
            Tweet.objects.select_related("user")
            .prefetch_related("likes", Prefetch("comments", queryset=comments_queryset))
            .annotate(likes_count=Count("likes", distinct=True))
            .annotate(comments_count=Count("comments", distinct=True))
            .only(
                "id",
                "text",
                "photo_url",
                "created_at",
                "updated_at",
                "view_count",
                "user__id",
                "user__username",
                "user__first_name",
                "user__last_name",
            )
        )

    @staticmethod
    def get_tweets_by_user(user_id):
        return (
            Tweet.objects.filter(user_id=user_id)
            .select_related("user")
            .prefetch_related("likes")
            .annotate(likes_count=Count("likes", distinct=True))
            .annotate(comments_count=Count("comments", distinct=True))
            .only(
                "id",
                "text",
                "photo_url",
                "created_at",
                "updated_at",
                "view_count",
                "user__id",
                "user__username",
            )
            .order_by("-created_at")
        )

    @staticmethod
    def get_tweets_with_photos():
        return (
            Tweet.objects.filter(photo_url__isnull=False)
            .select_related("user")
            .prefetch_related("likes")
            .annotate(likes_count=Count("likes", distinct=True))
            .annotate(comments_count=Count("comments", distinct=True))
            .only(
                "id",
                "text",
                "photo_url",
                "created_at",
                "updated_at",
                "view_count",
                "user__id",
                "user__username",
            )
            .order_by("-created_at")
        )

    @staticmethod
    def get_tweets_by_date_range(start_date, end_date):
        return (
            Tweet.objects.filter(created_at__gte=start_date, created_at__lte=end_date)
            .select_related("user")
            .prefetch_related("likes")
            .annotate(likes_count=Count("likes", distinct=True))
            .annotate(comments_count=Count("comments", distinct=True))
            .only(
                "id",
                "text",
                "photo_url",
                "created_at",
                "updated_at",
                "view_count",
                "user__id",
                "user__username",
            )
            .order_by("-created_at")
        )


class OptimizedCommentQueries:
    @staticmethod
    def get_comments_for_tweet(tweet_id):
        replies_queryset = Comment.objects.select_related("user").order_by("created_at")

        return (
            Comment.objects.filter(tweet_id=tweet_id, parent__isnull=True)
            .select_related("user")
            .prefetch_related(Prefetch("replies", queryset=replies_queryset))
            .only("id", "text", "created_at", "user__id", "user__username", "tweet_id")
            .order_by("created_at")
        )


class AggregateStatistics:
    @staticmethod
    def get_tweet_stats(tweet_id):
        stats = (
            Tweet.objects.filter(id=tweet_id)
            .annotate(
                likes_count=Count("likes", distinct=True),
                comments_count=Count("comments", distinct=True),
            )
            .annotate(
                total_engagement=F("likes_count")
                + F("comments_count")
                + F("view_count")
            )
            .values("likes_count", "comments_count", "total_engagement")
            .first()
        )
        return stats or {"likes_count": 0, "comments_count": 0, "total_engagement": 0}

    @staticmethod
    def get_popular_tweets(limit=10):
        return (
            Tweet.objects.annotate(
                likes_count=Count("likes", distinct=True),
                comments_count=Count("comments", distinct=True),
                total_engagement=F("view_count") + Count("likes") + Count("comments"),
            )
            .select_related("user")
            .only(
                "id",
                "text",
                "photo_url",
                "created_at",
                "user__id",
                "user__username",
                "view_count",
            )
            .filter(total_engagement__gt=0)
            .order_by("-total_engagement")[:limit]
        )
