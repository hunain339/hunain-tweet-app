from . import views
from django.urls import path

urlpatterns = [
    path('', views.tweet_list, name='tweet_list'),
    path('create/', views.tweet_create, name='tweet_create'),
    path('<int:tweet_id>/edit/', views.edit_tweet, name='tweet_edit'),
    path('<int:tweet_id>/delete/', views.tweet_delete, name='tweet_delete'),
    path('register/', views.register, name='register'),
    path('<int:tweet_id>/like/', views.tweet_like, name='tweet_like'),
    path('<int:tweet_id>/comment/', views.add_comment, name='add_comment'),
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
]
