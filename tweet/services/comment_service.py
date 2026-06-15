from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from ..models import Tweet, Comment, Notification
from ..cache_utils import invalidate_tweet_cache, invalidate_user_cache, invalidate_user_unread_count

class CommentService:
    @staticmethod
    @transaction.atomic
    def create_comment(user: User, tweet: Tweet, text: str, parent_id=None) -> Comment:
        text = text.strip()
        if not text:
            raise ValidationError("Comment text cannot be empty.")

        parent = None
        if parent_id:
            try:
                parent = Comment.objects.get(id=parent_id, tweet=tweet)
            except Comment.DoesNotExist:
                raise ValidationError("Parent comment does not exist in this tweet context.")

        comment = Comment.objects.create(
            user=user,
            tweet=tweet,
            text=text,
            parent=parent
        )

        # Triggers side effects - Create Notifications
        notifications = []
        if user != tweet.user:
            notifications.append(
                Notification(
                    user=tweet.user,
                    comment=comment,
                    notification_type="reply" if parent else "comment"
                )
            )

        # Notify parent comment author if reply is not by the parent author themselves
        if parent and parent.user != user and parent.user != tweet.user:
            notifications.append(
                Notification(
                    user=parent.user,
                    comment=comment,
                    notification_type="reply"
                )
            )

        if notifications:
            Notification.objects.bulk_create(notifications)
            for notif in notifications:
                try:
                    invalidate_user_unread_count(notif.user.id)
                except Exception:
                    pass

        # Invalidate related caches
        try:
            invalidate_tweet_cache(tweet.id)
            invalidate_user_cache(tweet.user.id)
        except Exception:
            pass

        return comment
