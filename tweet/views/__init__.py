from .web_views import (
    IndexView,
    TweetListView,
    TweetCreateView,
    TweetDetailView,
    TweetUpdateView,
    TweetDeleteView,
    UserProfileView,
    UserRegisterView,
    TweetLikeView,
    CommentCreateView,
    NotificationListView,
    NotificationMarkReadView,
    NotificationMarkAllReadView,
    NotificationUnreadCountView,
)
from .admin_views import (
    AdminDashboardView,
    AdminUserListView,
    AdminUserDeleteView,
    AdminUserPasswordResetView,
)
from .api_views import (
    obtain_auth_token,
    tweets_list_api,
    tweet_detail_api,
)
from ..utils.storage import upload_to_supabase, delete_from_supabase

index = IndexView.as_view()

__all__ = [
    "IndexView",
    "index",
    "TweetListView",
    "TweetCreateView",
    "TweetDetailView",
    "TweetUpdateView",
    "TweetDeleteView",
    "UserProfileView",
    "UserRegisterView",
    "TweetLikeView",
    "CommentCreateView",
    "NotificationListView",
    "NotificationMarkReadView",
    "NotificationMarkAllReadView",
    "NotificationUnreadCountView",
    "AdminDashboardView",
    "AdminUserListView",
    "AdminUserDeleteView",
    "AdminUserPasswordResetView",
    "obtain_auth_token",
    "tweets_list_api",
    "tweet_detail_api",
    "upload_to_supabase",
    "delete_from_supabase",
]
