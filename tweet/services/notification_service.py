from django.db import transaction
from django.contrib.auth.models import User
from ..models import Notification
from ..cache_utils import invalidate_user_unread_count

class NotificationService:
    @staticmethod
    @transaction.atomic
    def mark_as_read(user: User, notification_id: int) -> Notification:
        from django.shortcuts import get_object_or_404
        notification = get_object_or_404(Notification, id=notification_id, user=user)
        if not notification.is_read:
            notification.is_read = True
            notification.save(update_fields=["is_read"])
            invalidate_user_unread_count(user.id)
        return notification

    @staticmethod
    @transaction.atomic
    def mark_all_as_read(user: User):
        Notification.objects.filter(user=user, is_read=False).update(is_read=True)
        invalidate_user_unread_count(user.id)
