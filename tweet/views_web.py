from django.views.generic import (
    ListView,
    CreateView,
    DetailView,
    UpdateView,
    DeleteView,
)
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .selectors.tweet_selector import OptimizedTweetQueries
from .services.tweet_service import TweetService
from .models import Tweet
from .forms import TweetForm


class TweetListView(ListView):
    template_name = "tweet_list.html"
    context_object_name = "tweets"
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get("q", "").strip()
        qs = OptimizedTweetQueries.get_tweets_for_list(user=self.request.user)
        if query:
            qs = qs.filter(text__icontains=query)
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
    template_name = "tweet/create.html"

    def form_valid(self, form):
        tweet = TweetService.create_tweet(
            user=self.request.user,
            text=form.cleaned_data.get("text", ""),
            photo_file=self.request.FILES.get("photo"),
        )
        # Avoid calling form.save() again (would create a Tweet without user)
        self.object = tweet
        return redirect(reverse("tweet_detail", kwargs={"pk": tweet.id}))


class TweetDetailView(DetailView):
    model = Tweet
    template_name = "tweet/detail.html"
    context_object_name = "tweet"


class TweetEditPermission(UserPassesTestMixin):
    def test_func(self):
        tweet = self.get_object()
        return tweet.user_id == self.request.user.id

    def handle_no_permission(self):
        # Tests expect a 404 when a user attempts to edit/delete another's tweet
        from django.http import Http404

        raise Http404()


class TweetUpdateView(LoginRequiredMixin, TweetEditPermission, UpdateView):
    model = Tweet
    form_class = TweetForm
    template_name = "tweet/edit.html"

    def form_valid(self, form):
        tweet = self.get_object()
        TweetService.update_tweet(
            tweet,
            text=form.cleaned_data.get("text", ""),
            photo_file=self.request.FILES.get("photo"),
        )
        return super().form_valid(form)


class TweetDeleteView(LoginRequiredMixin, TweetEditPermission, DeleteView):
    model = Tweet
    template_name = "tweet/confirm_delete.html"
    success_url = reverse_lazy("tweet:list")
