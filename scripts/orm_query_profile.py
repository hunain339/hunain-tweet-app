#!/usr/bin/env python3
"""Measure DB queries for key selectors to detect N+1 issues."""
import os
import django
import sys

# ensure repo root is on PYTHONPATH so `hunain_project` is importable
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hunain_project.settings")
django.setup()

from django.test.utils import CaptureQueriesContext
from django.db import connection
from tweet.selectors.tweet_selector import (
    OptimizedTweetQueries,
    OptimizedCommentQueries,
    AggregateStatistics,
)
from django.contrib.auth import get_user_model

User = get_user_model()


def profile_query(name, fn):
    with CaptureQueriesContext(connection) as ctx:
        result = fn()
        # force evaluation
        if hasattr(result, "__iter__") and not isinstance(result, dict):
            _ = list(result[:10]) if hasattr(result, '__getitem__') else list(result)
        elif hasattr(result, "items"):
            _ = result
    print(f"{name}: {len(ctx)} queries")
    for q in ctx.captured_queries[:10]:
        print("  ->", q['sql'].replace('\n', ' ')[:300])
    print()


def run():
    # pick a user if exists
    user = User.objects.first()

    profile_query("get_tweets_for_list", lambda: OptimizedTweetQueries.get_tweets_for_list(user))
    profile_query("get_tweets_for_detail", lambda: OptimizedTweetQueries.get_tweets_for_detail())
    if user:
        profile_query("get_tweets_by_user", lambda: OptimizedTweetQueries.get_tweets_by_user(user.id))
    # pick a tweet id
    from tweet.models import Tweet

    tweet = Tweet.objects.first()
    if tweet:
        profile_query("get_comments_for_tweet", lambda: OptimizedCommentQueries.get_comments_for_tweet(tweet.id))
        profile_query("get_tweet_stats", lambda: AggregateStatistics.get_tweet_stats(tweet.id))
    profile_query("get_popular_tweets", lambda: AggregateStatistics.get_popular_tweets(5))

    # additional: iterate over multiple tweets and access related attrs
    def iterate_and_touch():
        qs = OptimizedTweetQueries.get_tweets_for_list(user)
        tweets = list(qs[:20])
        out = []
        for t in tweets:
            # access user, comments, likes existence
            u = t.user.username if hasattr(t, 'user') else None
            comments = list(t.comments.all()[:5])
            out.append((t.id, u, len(comments)))
        return out

    profile_query("iterate_and_touch_20", iterate_and_touch)


if __name__ == "__main__":
    run()
