from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import connection
from django.test.utils import CaptureQueriesContext

from ..models import Tweet, Comment
from ..selectors.tweet_selector import OptimizedTweetQueries


class QueryCountTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="qauser", password="pass")

        # create 20 tweets with a few comments each
        self.tweets = []
        for i in range(20):
            t = Tweet.objects.create(user=self.user, text=f"tweet {i}")
            self.tweets.append(t)
            # add 0-3 comments
            for j in range(i % 4):
                Comment.objects.create(tweet=t, user=self.user, text=f"c{j}")

    def test_tweets_for_list_query_count(self):
        # measure queries when fetching list and touching comments/users
        with CaptureQueriesContext(connection) as ctx:
            qs = OptimizedTweetQueries.get_tweets_for_list(self.user)
            items = list(qs[:20])
            # access tweet.user and tweet.comments
            for t in items:
                _ = t.user.username
                _ = list(t.comments.all()[:5])

        # expect 2 queries: one for tweets with annotations, one for prefetched comments+users
        self.assertLessEqual(len(ctx.captured_queries), 3)
