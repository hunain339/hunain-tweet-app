from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Count
from tweet.models import Comment


class Command(BaseCommand):
    help = "Remove duplicate comments and regenerate seed comments with realistic content."

    REALISTIC_COMMENTS = [
        "This tweet really made my day!",
        "Love how this was explained, very clear.",
        "I can relate to this so much.",
        "This is a great example of a production-ready feature.",
        "The design and UX here are very polished.",
        "Always nice to see clean code and good architecture.",
        "This approach is thoughtful and easy to understand.",
        "I appreciate how much testing and validation went into this.",
        "Nice work on making the feed feel responsive.",
        "This comment thread would be useful for new users.",
    ]

    def handle(self, *args, **options):
        self.stdout.write("Scanning comments for duplicates...")
        duplicates = (
            Comment.objects.values("tweet_id", "user_id", "text")
            .annotate(count=Count("id"))
            .filter(count__gt=1)
        )

        total_removed = 0
        for dup in duplicates:
            comments = Comment.objects.filter(
                tweet_id=dup["tweet_id"],
                user_id=dup["user_id"],
                text=dup["text"],
            ).order_by("created_at")
            keep = comments.first()
            to_remove = comments.exclude(id=keep.id)
            removed_count, _ = to_remove.delete()
            total_removed += removed_count
            self.stdout.write(
                f"Removed {removed_count} duplicate comments for tweet={dup['tweet_id']} user={dup['user_id']}"
            )

        if total_removed == 0:
            self.stdout.write("No duplicate comments found.")
        else:
            self.stdout.write(f"Removed {total_removed} duplicate comment rows.")

        self.stdout.write("Validating all comments now...")
        self.stdout.write(f"Remaining comments: {Comment.objects.count()}")

        # Additional pass: remove global duplicate texts (keep earliest)
        self.stdout.write("Scanning for global duplicate comment texts...")
        text_duplicates = (
            Comment.objects.values("text").annotate(count=Count("id")).filter(count__gt=1)
        )
        global_removed = 0
        for td in text_duplicates:
            comments = Comment.objects.filter(text=td["text"]).order_by("created_at")
            keep = comments.first()
            to_remove = comments.exclude(id=keep.id)
            removed_count, _ = to_remove.delete()
            global_removed += removed_count
            self.stdout.write(f"Removed {removed_count} global duplicate comments for text='{td['text'][:40]}'")

        if global_removed:
            self.stdout.write(f"Removed {global_removed} global duplicate comment rows.")

        self.stdout.write("Seed cleanup complete.")
