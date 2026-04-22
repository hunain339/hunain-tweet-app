from rest_framework import serializers
from .models import Tweet, Comment
from django.contrib.auth.models import User
from .utils.storage import get_signed_url


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model - used for tweet author info"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']
        read_only_fields = ['id', 'username', 'first_name', 'last_name']


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment model"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'user', 'text', 'created_at', 'parent']
        read_only_fields = ['id', 'user', 'created_at']


class TweetSerializer(serializers.ModelSerializer):
    """
    Serializer for Tweet model with related data (detail view).
    
    Uses annotated fields for efficient status checks:
    - likes_count: Annotated from queryset
    - comments_count: Annotated from queryset
    - is_liked_by_user: Annotated via Subquery (Exists)
    """
    user = UserSerializer(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    is_liked_by_user = serializers.SerializerMethodField()
    comments_count = serializers.IntegerField(read_only=True)
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Tweet
        fields = [
            'id',
            'user',
            'text',
            'photo_url',
            'created_at',
            'updated_at',
            'view_count',
            'likes_count',
            'is_liked_by_user',
            'comments_count',
        ]
        read_only_fields = fields

    def get_is_liked_by_user(self, obj):
        """Uses annotated field from optimized queryset."""
        return getattr(obj, 'is_liked_by_user', False)

    def get_photo_url(self, obj):
        """Returns a signed URL for private storage."""
        if hasattr(obj, 'photo_url') and obj.photo_url:
            # Check if it's already a full URL or just a path
            url = obj.photo_url
            if hasattr(url, 'url'): # Handle FileField if used
                url = url.url
            return get_signed_url(str(url))
        return None


class TweetListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for tweet list view.
    - Excludes nested comments for faster response
    - Uses annotated fields for efficient counts
    """
    user = UserSerializer(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    is_liked_by_user = serializers.SerializerMethodField()
    comments_count = serializers.IntegerField(read_only=True)
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Tweet
        fields = [
            'id',
            'user',
            'text',
            'photo_url',
            'created_at',
            'updated_at',
            'view_count',
            'likes_count',
            'is_liked_by_user',
            'comments_count',
        ]
        read_only_fields = fields

    def get_is_liked_by_user(self, obj):
        """Uses annotated field from optimized queryset."""
        return getattr(obj, 'is_liked_by_user', False)

    def get_photo_url(self, obj):
        """Returns a signed URL for private storage."""
        if hasattr(obj, 'photo_url') and obj.photo_url:
            return get_signed_url(str(obj.photo_url))
        return None


class TokenAuthenticationSerializer(serializers.Serializer):
    """
    Serializer for token authentication.
    Accepts username and password, returns an authentication token.
    """
    username = serializers.CharField(
        label="Username",
        write_only=True
    )
    password = serializers.CharField(
        label="Password",
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )
    token = serializers.CharField(
        label="Token",
        read_only=True
    )
    user_id = serializers.IntegerField(
        label="User ID",
        read_only=True
    )
    username_response = serializers.CharField(
        label="Username",
        read_only=True,
        source='username'
    )

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            from django.contrib.auth import authenticate
            user = authenticate(username=username, password=password)
            
            if not user:
                msg = 'Unable to log in with provided credentials.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Must include "username" and "password".'
            raise serializers.ValidationError(msg, code='authorization')

        data['user'] = user
        return data

    def create(self, validated_data):
        from rest_framework.authtoken.models import Token
        
        user = validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        return {
            'token': token.key,
            'user_id': user.id,
            'username': user.username,
        }
