import secrets
from django.views.generic import TemplateView, ListView, View
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.core.cache import cache
from django.db.models import Count, Q

from ..models import Tweet, Comment

class SuperuserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_superuser

    def handle_no_permission(self):
        return HttpResponseForbidden("Access denied.")


class AdminDashboardView(SuperuserRequiredMixin, TemplateView):
    template_name = "admin_dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # Cache stats for 1 hour to prevent timeout on serverless database connections
        stats_cache_key = "admin_dashboard_stats"
        stats = cache.get(stats_cache_key)

        if stats is None:
            try:
                stats = {
                    "total_users": User.objects.count(),
                    "total_tweets": Tweet.objects.count(),
                    "total_comments": Comment.objects.count(),
                    "total_likes": Tweet.objects.aggregate(n=Count("likes", distinct=True))["n"] or 0,
                    "active_users": User.objects.filter(is_active=True).count(),
                    "staff_users": User.objects.filter(is_staff=True).count(),
                }
                cache.set(stats_cache_key, stats, 3600)
            except Exception:
                stats = {
                    "total_users": 0, "total_tweets": 0, "total_comments": 0, "total_likes": 0,
                    "active_users": 0, "staff_users": 0, "error": "Failed to load statistics"
                }

        # Cache top users for 30 minutes
        top_users_cache_key = "admin_dashboard_top_users"
        top_users = cache.get(top_users_cache_key)

        if top_users is None:
            try:
                top_users = list(
                    User.objects.annotate(tweet_count=Count("tweet"))
                    .only("id", "username", "email")
                    .order_by("-tweet_count")[:5]
                )
                cache.set(top_users_cache_key, top_users, 1800)
            except Exception:
                top_users = []

        try:
            recent_tweets = (
                Tweet.objects.select_related("user")
                .prefetch_related("likes", "comments")
                .only("id", "user_id", "user__username", "text", "created_at", "view_count")
                .order_by("-created_at")[:10]
            )
            recent_users = User.objects.only("id", "username", "email", "date_joined").order_by("-date_joined")[:5]
        except Exception:
            recent_tweets = []
            recent_users = []

        ctx.update({
            "stats": stats,
            "recent_tweets": recent_tweets,
            "recent_users": recent_users,
            "top_users": top_users,
        })
        return ctx


class AdminUserListView(SuperuserRequiredMixin, ListView):
    template_name = "admin_users.html"
    context_object_name = "users"
    paginate_by = 20

    def get_queryset(self):
        query = self.request.GET.get("q", "").strip()
        role_filter = self.request.GET.get("role", "")

        users_list = (
            User.objects.annotate(tweet_count=Count("tweet"))
            .only("id", "username", "email", "is_superuser", "is_staff", "is_active", "date_joined")
            .order_by("-date_joined")
        )

        if query:
            users_list = users_list.filter(
                Q(username__icontains=query) | Q(email__icontains=query)
            )

        if role_filter == "superuser":
            users_list = users_list.filter(is_superuser=True)
        elif role_filter == "staff":
            users_list = users_list.filter(is_staff=True, is_superuser=False)
        elif role_filter == "user":
            users_list = users_list.filter(is_staff=False, is_superuser=False)

        self.users_count = users_list.count()
        return users_list

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            "query": self.request.GET.get("q", "").strip(),
            "role_filter": self.request.GET.get("role", ""),
            "total_count": getattr(self, "users_count", 0),
        })
        return ctx


class AdminUserDeleteView(SuperuserRequiredMixin, View):
    def post(self, request, user_id, *args, **kwargs):
        user_to_delete = get_object_or_404(User, pk=user_id)
        if user_to_delete.is_superuser:
            messages.error(request, "Cannot delete a superuser account.")
        else:
            username = user_to_delete.username
            user_to_delete.delete()
            messages.success(request, f"User @{username} has been permanently deleted.")
        return redirect("admin_users")


class AdminUserPasswordResetView(SuperuserRequiredMixin, View):
    def get(self, request, user_id, *args, **kwargs):
        user_to_reset = get_object_or_404(User, pk=user_id)
        return render(request, "admin_reset_password_confirm.html", {"user_to_reset": user_to_reset})

    def post(self, request, user_id, *args, **kwargs):
        user_to_reset = get_object_or_404(User, pk=user_id)
        new_password = secrets.token_urlsafe(12)
        user_to_reset.set_password(new_password)
        user_to_reset.save()
        messages.success(
            request, 
            f"Password reset for @{user_to_reset.username} was successful."
        )
        return redirect("admin_users")
