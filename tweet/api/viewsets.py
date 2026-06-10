from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ..serializers import TweetSerializer, TweetListSerializer
from ..models import Tweet
from ..pagination import TweetPagination
from ..permissions import IsPublicReadOnlyOrAuthenticated
from ..query_optimizations import OptimizedTweetQueries
from ..services.tweet_service import TweetService


class TweetViewSet(viewsets.ModelViewSet):
    # Avoid evaluating querysets at import time (prevents DB access during checks)
    queryset = Tweet.objects.none()
    pagination_class = TweetPagination
    permission_classes = [IsPublicReadOnlyOrAuthenticated]

    def get_queryset(self):
        user = self.request.user if self.request else None
        if self.action == "list":
            return OptimizedTweetQueries.get_tweets_for_list(user=user)
        if self.action == "retrieve":
            # Use detail selector if needed
            return OptimizedTweetQueries.get_tweets_for_detail()
        return Tweet.objects.select_related("user").prefetch_related("likes")

    def get_serializer_class(self):
        if self.action == "list":
            return TweetListSerializer
        return TweetSerializer

    def perform_create(self, serializer):
        # Delegate business logic to service
        tweet = TweetService.create_tweet(
            user=self.request.user,
            text=serializer.validated_data.get("text", ""),
            photo_file=self.request.FILES.get("photo"),
        )
        serializer.instance = tweet

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        tweet = self.get_object()
        liked = TweetService.toggle_like(tweet, request.user)
        return Response({"success": True, "liked": liked, "count": tweet.likes.count()})
