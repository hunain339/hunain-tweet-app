from rest_framework import serializers
from .models import Tweet, Comment
from django.contrib.auth.models import User


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
    """Serializer for Tweet model with related data"""
    user = UserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    is_liked_by_user = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

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
            'comments',
        ]
        read_only_fields = [
            'id',
            'user',
            'created_at',
            'updated_at',
            'view_count',
            'likes_count',
            'is_liked_by_user',
            'comments_count',
            'comments',
        ]

    def get_likes_count(self, obj):
        """Get the count of likes for a tweet"""
        return obj.likes.count()

    def get_is_liked_by_user(self, obj):
        """Check if the current user likes this tweet"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False

    def get_comments_count(self, obj):
        """Get the count of comments for a tweet"""
        return obj.comments.count()


class TweetListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for tweet list view - excludes nested comments"""
    user = UserSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    is_liked_by_user = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

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
        read_only_fields = [
            'id',
            'user',
            'created_at',
            'updated_at',
            'view_count',
            'likes_count',
            'is_liked_by_user',
            'comments_count',
        ]

    def get_likes_count(self, obj):
        """Get the count of likes for a tweet"""
        return obj.likes.count()

    def get_is_liked_by_user(self, obj):
        """Check if the current user likes this tweet"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False

    def get_comments_count(self, obj):
        """Get the count of comments for a tweet"""
        return obj.comments.count()


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
