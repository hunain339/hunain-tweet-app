from . import views
from .views_web import (
    TweetListView,
    TweetCreateView,
    TweetDetailView,
    TweetUpdateView,
    TweetDeleteView,
)
from django.urls import path

urlpatterns = [
    # Web Views
    path("", TweetListView.as_view(), name="tweet_list"),
    path("create/", TweetCreateView.as_view(), name="tweet_create"),
    path("<int:pk>/edit/", TweetUpdateView.as_view(), name="tweet_edit"),
    path("<int:pk>/delete/", TweetDeleteView.as_view(), name="tweet_delete"),
    path("register/", views.register, name="register"),
    path("<int:tweet_id>/like/", views.tweet_like, name="tweet_like"),
    path("<int:tweet_id>/comment/", views.add_comment, name="add_comment"),
    path("profile/<str:username>/", views.user_profile, name="user_profile"),
    # Notifications
    path("notifications/", views.notifications, name="notifications"),
    path(
        "notifications/<int:notification_id>/read/",
        views.mark_notification_as_read,
        name="mark_notification_as_read",
    ),
    path(
        "notifications/read-all/",
        views.mark_all_notifications_as_read,
        name="mark_all_notifications_as_read",
    ),
    path(
        "api/notifications/unread/",
        views.unread_notification_count,
        name="unread_notification_count",
    ),
    # Admin Dashboard
    path("admin/dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin/users/", views.admin_users, name="admin_users"),
    path(
        "admin/users/<int:user_id>/delete/",
        views.admin_user_delete,
        name="admin_user_delete",
    ),
    path(
        "admin/users/<int:user_id>/reset-password/",
        views.admin_reset_password,
        name="admin_reset_password",
    ),
    # Details
    path("<int:pk>/", TweetDetailView.as_view(), name="tweet_detail"),
]
