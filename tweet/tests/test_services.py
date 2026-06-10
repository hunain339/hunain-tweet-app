from django.test import TestCase
from django.contrib.auth.models import User
from ..services.tweet_service import TweetService
from ..models import Tweet


class TweetServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="svcuser", password="pass")

    def test_create_tweet_simple(self):
        tweet = TweetService.create_tweet(self.user, "Service created tweet")
        self.assertIsInstance(tweet, Tweet)
        self.assertEqual(tweet.text, "Service created tweet")
        self.assertEqual(tweet.user, self.user)
