from . import views
from django.urls import path

urlpatterns = [
    # Web Views
    path("", views.TweetListView.as_view(), name="tweet_list"),
    path("create/", views.TweetCreateView.as_view(), name="tweet_create"),
    path("<int:pk>/edit/", views.TweetUpdateView.as_view(), name="tweet_edit"),
    path("<int:pk>/delete/", views.TweetDeleteView.as_view(), name="tweet_delete"),
    path("register/", views.UserRegisterView.as_view(), name="register"),
    path("<int:tweet_id>/like/", views.TweetLikeView.as_view(), name="tweet_like"),
    path("<int:tweet_id>/comment/", views.CommentCreateView.as_view(), name="add_comment"),
    path("profile/<str:username>/", views.UserProfileView.as_view(), name="user_profile"),
    
    # Notifications
    path("notifications/", views.NotificationListView.as_view(), name="notifications"),
    path(
        "notifications/<int:notification_id>/read/",
        views.NotificationMarkReadView.as_view(),
        name="mark_notification_as_read",
    ),
    path(
        "notifications/read-all/",
        views.NotificationMarkAllReadView.as_view(),
        name="mark_all_notifications_as_read",
    ),
    path(
        "api/notifications/unread/",
        views.NotificationUnreadCountView.as_view(),
        name="unread_notification_count",
    ),
    
    # Admin Dashboard
    path("admin/dashboard/", views.AdminDashboardView.as_view(), name="admin_dashboard"),
    path("admin/users/", views.AdminUserListView.as_view(), name="admin_users"),
    path(
        "admin/users/<int:user_id>/delete/",
        views.AdminUserDeleteView.as_view(),
        name="admin_user_delete",
    ),
    path(
        "admin/users/<int:user_id>/reset-password/",
        views.AdminUserPasswordResetView.as_view(),
        name="admin_reset_password",
    ),
    
    # Details
    path("<int:pk>/", views.TweetDetailView.as_view(), name="tweet_detail"),
]
