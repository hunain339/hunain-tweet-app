from django.db.models import QuerySet
from django.contrib.auth.models import User
from django.core.cache import cache
from ..models import Notification

class NotificationSelector:
    @staticmethod
    def get_notifications_for_user(user: User) -> QuerySet:
        return (
            Notification.objects.filter(user=user)
            .select_related("comment__user", "comment__tweet")
            .only(
                "id", "is_read", "notification_type", "created_at",
                "user_id", "comment__id", "comment__text", "comment__created_at",
                "comment__user__id", "comment__user__username",
                "comment__tweet__id", "comment__tweet__text"
            )
            .order_by("-created_at")
        )

    @staticmethod
    def get_unread_count(user: User) -> int:
        unread_cache_key = f"user_unread_count:{user.id}"
        count = cache.get(unread_cache_key)
        if count is None:
            count = Notification.objects.filter(user=user, is_read=False).count()
            cache.set(unread_cache_key, count, 300)  # Cache for 5 minutes
        return count
