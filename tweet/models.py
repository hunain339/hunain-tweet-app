from django.db import models
from django.contrib.auth.models import User
from django.core.validators import URLValidator

# Create your models here.


class Tweet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=240)
    photo_url = models.URLField(blank=True, null=True, validators=[URLValidator()])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    view_count = models.IntegerField(default=0)

    likes = models.ManyToManyField(User, related_name='liked_tweets', blank=True)

    def __str__(self):
        return f'{self.user.username} - {self.text[:10]}'

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['-created_at']),
        ]


class Comment(models.Model):
    tweet = models.ForeignKey(Tweet, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=240)
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    def __str__(self):
        return f'{self.user.username}: {self.text[:20]}'

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['tweet', '-created_at']),
        ]


class Notification(models.Model):
    """
    Track notifications for comments and replies on a user's tweets.
    """
    NOTIFICATION_TYPES = (
        ('comment', 'New Comment'),
        ('reply', 'New Reply'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES, default='comment')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Notification for {self.user.username} - {self.notification_type}'

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read']),
        ]
