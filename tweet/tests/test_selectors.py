from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Tweet
from ..selectors.tweet_selector import OptimizedTweetQueries


class TweetSelectorTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="seluser", password="pass")
        self.other = User.objects.create_user(username="other", password="pass")
        # create tweets
        Tweet.objects.create(user=self.user, text="First")
        t2 = Tweet.objects.create(user=self.other, text="Second")
        # like second tweet
        t2.likes.add(self.user)

    def test_get_list_queryset_annotations(self):
        qs = OptimizedTweetQueries.get_tweets_for_list(user=self.user)
        tweets = list(qs)
        self.assertTrue(hasattr(tweets[0], "likes_count"))
        # find the liked tweet and ensure is_liked_by_user shows True
        liked = [t for t in tweets if getattr(t, "is_liked_by_user", False)]
        self.assertTrue(len(liked) >= 1)
