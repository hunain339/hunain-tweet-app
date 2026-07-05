import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tweet.models import Tweet, Comment


class Command(BaseCommand):
    help = "Generate realistic comment seed data for tweets."

    SAMPLE_COMMENTS = [
        "This is a thoughtful perspective — thanks for sharing.",
        "Really enjoying the direction this project is taking.",
        "I appreciate the attention to performance and user experience.",
        "Nice work, the feature set feels polished and modern.",
        "This comment thread is a good example of clean product design.",
        "I love how accessible the UI feels from the first glance.",
        "Great implementation details here — very easy to follow.",
        "This would make a strong portfolio project for backend and frontend work.",
        "Seeing this live app flow is impressive and well-structured.",
        "The relational design around tweets and comments is solid.",
    ]

    def handle(self, *args, **options):
        self.stdout.write("Generating realistic comments for existing tweets...")
        tweets = list(Tweet.objects.all())
        if not tweets:
            self.stdout.write(self.style.WARNING("No tweets found. Create tweets first."))
            return

        users = list(User.objects.filter(is_active=True))
        if not users:
            self.stdout.write(self.style.WARNING("No active users found. Create users first."))
            return

        created = 0
        for tweet in tweets:
            comment_count = Comment.objects.filter(tweet=tweet).count()
            if comment_count >= 3:
                continue

            needed = 3 - comment_count
            # Sample comments without replacement to avoid creating duplicate texts
            available_samples = [s for s in self.SAMPLE_COMMENTS if not Comment.objects.filter(text=s).exists()]
            if not available_samples:
                # Nothing unique left to add
                continue

            for _ in range(needed):
                # Refresh available samples each iteration
                available_samples = [s for s in available_samples if not Comment.objects.filter(text=s).exists()]
                if not available_samples:
                    break

                chosen_text = random.choice(available_samples)
                chosen_user = random.choice(users)

                # Use get_or_create to avoid duplicate rows for the same (tweet, user, text)
                obj, created_flag = Comment.objects.get_or_create(
                    tweet=tweet,
                    user=chosen_user,
                    text=chosen_text,
                )
                if created_flag:
                    created += 1
                # Remove chosen_text from available_samples to avoid reuse in this run
                try:
                    available_samples.remove(chosen_text)
                except ValueError:
                    pass

        self.stdout.write(self.style.SUCCESS(f"Created {created} realistic comments."))
