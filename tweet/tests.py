from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Tweet, Comment
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch

class TweetbarTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.other_user = User.objects.create_user(username='otheruser', password='password123')
        self.tweet = Tweet.objects.create(user=self.user, text='Original Tweet')

    def test_user_registration(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password1': 'password123!@#',
            'password2': 'password123!@#',
            'email': 'new@example.com'
        })
        self.assertEqual(User.objects.filter(username='newuser').count(), 1)

    @patch('tweet.views.upload_to_supabase')
    def test_tweet_creation_with_image(self, mock_upload):
        mock_upload.return_value = 'https://supabase.com/test.jpg'
        self.client.login(username='testuser', password='password123')
        
        image = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        response = self.client.post(reverse('tweet_create'), {
            'text': 'Tweet with image',
            'photo': image
        })
        
        self.assertEqual(Tweet.objects.filter(text='Tweet with image').count(), 1)
        tweet = Tweet.objects.get(text='Tweet with image')
        self.assertEqual(tweet.photo_url, 'https://supabase.com/test.jpg')

    def test_tweet_creation_without_image(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('tweet_create'), {
            'text': 'Tweet without image'
        })
        self.assertEqual(Tweet.objects.filter(text='Tweet without image').count(), 1)
        tweet = Tweet.objects.get(text='Tweet without image')
        self.assertIsNone(tweet.photo_url)

    def test_like_functionality(self):
        self.client.login(username='testuser', password='password123')
        # Like
        self.client.post(reverse('tweet_like', args=[self.tweet.id]))
        self.assertTrue(self.tweet.likes.filter(id=self.user.id).exists())
        # Unlike
        self.client.post(reverse('tweet_like', args=[self.tweet.id]))
        self.assertFalse(self.tweet.likes.filter(id=self.user.id).exists())

    def test_api_like_action(self):
        # Test the DRF ViewSet like action
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('tweet-like', args=[self.tweet.id]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('success'))
        self.assertTrue(data.get('liked'))
        self.assertEqual(data.get('count'), 1)
        # Toggle off
        response = self.client.post(reverse('tweet-like', args=[self.tweet.id]))
        data = response.json()
        self.assertFalse(data.get('liked'))
        self.assertEqual(data.get('count'), 0)

    def test_comment_creation(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('add_comment', args=[self.tweet.id]), {
            'text': 'Nice tweet!'
        })
        self.assertEqual(Comment.objects.filter(tweet=self.tweet, text='Nice tweet!').count(), 1)

    def test_authorization_edit_tweet(self):
        # other_user tries to edit testuser's tweet
        self.client.login(username='otheruser', password='password123')
        response = self.client.post(reverse('tweet_edit', args=[self.tweet.id]), {
            'text': 'Hacked text'
        })
        self.assertEqual(response.status_code, 404)
        self.tweet.refresh_from_db()
        self.assertEqual(self.tweet.text, 'Original Tweet')

    def test_authorization_delete_tweet(self):
        # other_user tries to delete testuser's tweet
        self.client.login(username='otheruser', password='password123')
        response = self.client.post(reverse('tweet_delete', args=[self.tweet.id]))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Tweet.objects.filter(id=self.tweet.id).count(), 1)

    def test_admin_user_delete_view(self):
        # Create a superuser and a regular user to delete
        admin = User.objects.create_superuser(username='admin', password='adminpass', email='admin@example.com')
        victim = User.objects.create_user(username='victim', password='victimpass')

        # Login as admin
        self.client.login(username='admin', password='adminpass')

        # Ensure victim exists
        self.assertTrue(User.objects.filter(username='victim').exists())

        # Post to admin_user_delete view
        response = self.client.post(reverse('admin_user_delete', args=[victim.id]))

        # After deletion, victim should be gone and we should be redirected to admin_users
        self.assertFalse(User.objects.filter(username='victim').exists())
        self.assertEqual(response.status_code, 302)
