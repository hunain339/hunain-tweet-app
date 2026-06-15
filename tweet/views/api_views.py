from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.db.models import F
from django_ratelimit.decorators import ratelimit

from ..models import Tweet
from ..serializers import TokenAuthenticationSerializer, TweetListSerializer, TweetSerializer
from ..selectors.tweet_selector import OptimizedTweetQueries
from ..cache_utils import CacheConfig

@ratelimit(key="ip", rate="5/m", block=True)
@api_view(["POST"])
@permission_classes([AllowAny])
def obtain_auth_token(request):
    """
    Token authentication endpoint.
    POST /api/token/
    """
    serializer = TokenAuthenticationSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        token_data = serializer.save()
        return Response(token_data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([AllowAny])
@cache_page(CacheConfig.SEARCH_CACHE_TIME)
@vary_on_headers("Authorization")
def tweets_list_api(request):
    """
    API endpoint to list tweets.
    """
    queryset = OptimizedTweetQueries.get_tweets_for_list()

    # Handle search parameter
    search = request.query_params.get("search", "").strip()
    if search:
        try:
            from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
            vector = SearchVector("text", weight="A") + SearchVector("user__username", weight="B")
            search_query = SearchQuery(search)
            queryset = queryset.annotate(rank=SearchRank(vector, search_query)).filter(rank__gt=0.01).order_by("-rank")
        except Exception:
            from django.db.models import Q
            queryset = queryset.filter(Q(text__icontains=search) | Q(user__username__icontains=search))

    from ..pagination import TweetPagination
    paginator = TweetPagination()
    page = paginator.paginate_queryset(queryset, request)

    if page is not None:
        serializer = TweetListSerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)

    serializer = TweetListSerializer(queryset, many=True, context={"request": request})
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
@cache_page(CacheConfig.PUBLIC_DETAIL_CACHE_TIME)
@vary_on_headers("Authorization")
def tweet_detail_api(request, tweet_id):
    """
    API endpoint to retrieve a specific tweet with comments.
    """
    try:
        queryset = OptimizedTweetQueries.get_tweets_for_detail()
        tweet = queryset.get(pk=tweet_id)
    except Tweet.DoesNotExist:
        return Response(
            {"detail": "Tweet not found."}, status=status.HTTP_404_NOT_FOUND
        )

    if request.user.is_authenticated:
        session_key = f"viewed_tweet_{tweet.id}"
        if not request.session.get(session_key, False):
            Tweet.objects.filter(id=tweet.id).update(view_count=F("view_count") + 1)
            request.session[session_key] = True

    serializer = TweetSerializer(tweet, context={"request": request})
    return Response(serializer.data)
