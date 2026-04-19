from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from tweet import views as tweet_views
from rest_framework.routers import DefaultRouter

# API Router configuration
router = DefaultRouter()
router.register(r'tweets', tweet_views.TweetViewSet, basename='tweet')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', tweet_views.index, name='index'),
    path('tweet/', include('tweet.urls')),
    path('api/token/', tweet_views.obtain_auth_token, name='obtain_auth_token'),
    path('api/', include(router.urls)), # Root level API
    path('account/', include('django.contrib.auth.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
