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
            for _ in range(needed):
                Comment.objects.create(
                    tweet=tweet,
                    user=random.choice(users),
                    text=random.choice(self.SAMPLE_COMMENTS),
                )
                created += 1

        self.stdout.write(self.style.SUCCESS(f"Created {created} realistic comments."))
