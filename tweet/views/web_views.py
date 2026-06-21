import logging

from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView, FormView, View, RedirectView
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import login
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit

from ..models import Tweet, Comment, Notification
from ..forms import TweetForm, UserRegistrationForm, CommentForm
from ..selectors.tweet_selector import OptimizedTweetQueries
from ..selectors.notification_selector import NotificationSelector
from ..services.tweet_service import TweetService
from ..services.comment_service import CommentService
from ..services.notification_service import NotificationService

logger = logging.getLogger(__name__)

class IndexView(RedirectView):
    pattern_name = "tweet_list"
    permanent = False


class TweetListView(ListView):
    template_name = "tweet_list.html"
    context_object_name = "tweets"
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get("q", "").strip()
        qs = OptimizedTweetQueries.get_tweets_for_list(user=self.request.user)
        if query:
            try:
                from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
                vector = SearchVector("text", weight="A") + SearchVector("user__username", weight="B")
                search_query = SearchQuery(query)
                qs = qs.annotate(rank=SearchRank(vector, search_query)).filter(rank__gt=0.01).order_by("-rank")
            except Exception:
                from django.db.models import Q
                qs = qs.filter(Q(text__icontains=query) | Q(user__username__icontains=query))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["query"] = self.request.GET.get("q", "").strip()

        if self.request.user.is_authenticated:
            page_obj = ctx.get("page_obj")
            if page_obj:
                tweet_ids = [t.id for t in page_obj.object_list]
                TweetService.increment_views_batch(self.request.user, tweet_ids)

        return ctx


class TweetCreateView(LoginRequiredMixin, CreateView):
    model = Tweet
    form_class = TweetForm
    template_name = "tweet_form.html"
    extra_context = {"action": "create"}

    @method_decorator(ratelimit(key="user", rate="10/h", block=True))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            tweet = TweetService.create_tweet(
                user=self.request.user,
                text=form.cleaned_data.get("text", ""),
                photo_file=self.request.FILES.get("photo"),
            )
            self.object = tweet
            messages.success(self.request, "Tweet posted successfully! 🎉")
            return redirect(reverse("tweet_list"))
        except Exception as e:
            logger.exception("Tweet creation failed for user %s", self.request.user.pk)
            messages.error(self.request, "Something went wrong while posting your tweet. Please try again.")
            return self.form_invalid(form)


class TweetDetailView(DetailView):
    model = Tweet
    template_name = "tweet_detail.html"
    context_object_name = "tweet"

    def get_queryset(self):
        return OptimizedTweetQueries.get_tweets_for_detail()


class TweetEditPermission(UserPassesTestMixin):
    def test_func(self):
        tweet = self.get_object()
        return tweet.user_id == self.request.user.id

    def handle_no_permission(self):
        raise Http404()


class TweetUpdateView(LoginRequiredMixin, TweetEditPermission, UpdateView):
    model = Tweet
    form_class = TweetForm
    template_name = "tweet_form.html"
    extra_context = {"action": "edit"}

    def form_valid(self, form):
        tweet = self.get_object()
        try:
            TweetService.update_tweet(
                tweet,
                self.request.user,
                text=form.cleaned_data.get("text", ""),
                photo_file=self.request.FILES.get("photo"),
            )
            # Check if remove_photo checkbox is set
            if self.request.POST.get("remove_photo"):
                if tweet.photo_url:
                    from ..utils.storage import delete_from_supabase
                    try:
                        delete_from_supabase(tweet.photo_url)
                    except Exception:
                        pass
                tweet.photo_url = ""
                tweet.save()
            messages.success(self.request, "Tweet updated successfully! ✅")
            self.object = tweet
            return redirect(reverse("tweet_list"))
        except Exception as e:
            logger.exception("Tweet update failed for tweet %s by user %s", self.get_object().pk, self.request.user.pk)
            messages.error(self.request, "Something went wrong while updating your tweet. Please try again.")
            return self.form_invalid(form)


class TweetDeleteView(LoginRequiredMixin, TweetEditPermission, DeleteView):
    model = Tweet
    template_name = "tweet_confirm_delete.html"
    success_url = reverse_lazy("tweet_list")

    def delete(self, request, *args, **kwargs):
        tweet = self.get_object()
        TweetService.delete_tweet(tweet, request.user)
        messages.success(request, "Tweet deleted.")
        return redirect(self.success_url)


class UserProfileView(ListView):
    template_name = "profile.html"
    context_object_name = "tweets"
    paginate_by = 10

    def get_queryset(self):
        from django.contrib.auth.models import User
        self.profile_user = get_object_or_404(User, username=self.kwargs["username"])
        return OptimizedTweetQueries.get_tweets_by_user(
            user_id=self.profile_user.id,
            request_user=self.request.user
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["profile_user"] = self.profile_user
        return ctx


class UserRegisterView(FormView):
    template_name = "registration/register.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy("tweet_list")

    @method_decorator(ratelimit(key="ip", rate="3/h", block=True))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user, backend="django.contrib.auth.backends.ModelBackend")
        messages.success(self.request, f"Welcome to Tweetbar, @{user.username}! 🚀")
        return super().form_valid(form)


class TweetLikeView(LoginRequiredMixin, View):
    @method_decorator(ratelimit(key="user", rate="30/h", block=True))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, tweet_id, *args, **kwargs):
        tweet = get_object_or_404(Tweet, id=tweet_id)
        liked = TweetService.toggle_like(tweet, request.user)
        
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({
                "success": True,
                "liked": liked,
                "count": tweet.likes.count(),
            })
        return redirect("tweet_list")


class CommentCreateView(LoginRequiredMixin, View):
    @method_decorator(ratelimit(key="user", rate="20/h", block=True))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, tweet_id, *args, **kwargs):
        tweet = get_object_or_404(Tweet, id=tweet_id)
        form = CommentForm(request.POST)
        
        if form.is_valid():
            parent_id = request.POST.get("parent_id")
            comment = CommentService.create_comment(
                user=request.user,
                tweet=tweet,
                text=form.cleaned_data.get("text", ""),
                parent_id=parent_id
            )
            
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({
                    "success": True,
                    "username": comment.user.username,
                    "text": comment.text,
                    "count": tweet.comments.count(),
                    "comment_id": comment.id,
                })
            messages.success(request, "Comment added! 💬")
        else:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({"success": False, "errors": form.errors}, status=400)

        return redirect("tweet_list")


class NotificationListView(LoginRequiredMixin, ListView):
    template_name = "notifications.html"
    context_object_name = "notifications"
    paginate_by = 15

    def get_queryset(self):
        return NotificationSelector.get_notifications_for_user(self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["unread_count"] = NotificationSelector.get_unread_count(self.request.user)
        return ctx


class NotificationMarkReadView(LoginRequiredMixin, View):
    def post(self, request, notification_id, *args, **kwargs):
        NotificationService.mark_as_read(request.user, notification_id)
        
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({
                "success": True,
                "unread_count": NotificationSelector.get_unread_count(request.user),
            })
        return redirect("notifications")


class NotificationMarkAllReadView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        NotificationService.mark_all_as_read(request.user)
        
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"success": True})
        return redirect("notifications")


class NotificationUnreadCountView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        count = NotificationSelector.get_unread_count(request.user)
        return JsonResponse({"count": count})
