from django.core.management.base import BaseCommand
from django.utils import timezone

from tweet.models import Tweet, Comment
from django.contrib.auth import get_user_model
from django.db import models


class Command(BaseCommand):
    help = "Clean up production posts/comments and optionally seed tweets."

    def add_arguments(self, parser):
        parser.add_argument(
            "--delete-text",
            action="append",
            dest="delete_texts",
            help="Exact comment text to dedupe/delete (can be provided multiple times)",
        )
        parser.add_argument(
            "--dedupe-all",
            action="store_true",
            dest="dedupe_all",
            help="Detect any duplicate comment texts and remove duplicates, keeping one",
        )
        parser.add_argument(
            "--delete-regex",
            dest="delete_regex",
            help="Delete comments whose text matches this regex",
        )
        parser.add_argument(
            "--delete-superusers",
            action="store_true",
            dest="delete_superusers",
            help="Delete all Tweets and Comments authored by superusers",
        )
        parser.add_argument(
            "--seed-count",
            type=int,
            dest="seed_count",
            help="Create N seed tweets to boost feed size",
        )
        parser.add_argument(
            "--seed-user",
            dest="seed_user",
            help="Username to attribute seed tweets to (required if --seed-count provided)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            dest="dry_run",
            help="Don't perform destructive actions; only report what would change",
        )

    def handle(self, *args, **options):
        User = get_user_model()
        dry = options.get("dry_run")

        if options.get("dedupe_all"):
            self.stdout.write("Scanning for duplicate comment texts...")
            dup_qs = (
                Comment.objects.values("text")
                .annotate(count=models.Count("id"))
                .filter(count__gt=1)
                .order_by("-count")
            )
            if not dup_qs:
                self.stdout.write("No duplicate comment texts found.")
            for item in dup_qs:
                text = item["text"]
                comments = list(Comment.objects.filter(text=text).order_by("created_at"))
                keep = comments[0]
                to_delete = comments[1:]
                self.stdout.write(f"Text: {text!r} — keeping id={keep.id}; deleting {len(to_delete)} duplicates")
                if not dry:
                    ids = [c.id for c in to_delete]
                    Comment.objects.filter(id__in=ids).delete()

        if options.get("delete_texts"):
            for txt in options.get("delete_texts"):
                qs = Comment.objects.filter(text=txt).order_by("created_at")
                count = qs.count()
                if count == 0:
                    self.stdout.write(f"No comments with exact text: {txt!r}")
                    continue
                keep = qs.first()
                to_delete = qs.exclude(id=keep.id)
                self.stdout.write(f"Found {count} comments with text {txt!r}; keeping id={keep.id}, deleting {to_delete.count()}")
                if not dry:
                    to_delete.delete()

        if options.get("delete_regex"):
            import re

            pattern = re.compile(options.get("delete_regex"), re.IGNORECASE)
            matches = []
            for c in Comment.objects.all():
                if pattern.search(c.text or ""):
                    matches.append(c.id)
            self.stdout.write(f"Comments matching regex {options.get('delete_regex')!r}: {len(matches)}")
            if not dry and matches:
                Comment.objects.filter(id__in=matches).delete()

        if options.get("delete_superusers"):
            su_ids = list(User.objects.filter(is_superuser=True).values_list("id", flat=True))
            self.stdout.write(f"Superuser ids: {su_ids}")
            if su_ids:
                tcnt = Tweet.objects.filter(user_id__in=su_ids).count()
                ccnt = Comment.objects.filter(user_id__in=su_ids).count()
                self.stdout.write(f"Tweets to delete: {tcnt}; Comments to delete: {ccnt}")
                if not dry:
                    Tweet.objects.filter(user_id__in=su_ids).delete()
                    Comment.objects.filter(user_id__in=su_ids).delete()

        if options.get("seed_count"):
            n = options.get("seed_count")
            username = options.get("seed_user")
            if not username:
                self.stderr.write("--seed-user is required when using --seed-count")
                return
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                self.stderr.write(f"User {username!r} not found")
                return
            created = []
            for i in range(n):
                txt = f"Seed tweet #{i+1} — clean content for recruiter demo."
                if dry:
                    self.stdout.write(f"DRY RUN: would create tweet for {username}: {txt}")
                else:
                    t = Tweet.objects.create(user=user, text=txt, created_at=timezone.now(), updated_at=timezone.now())
                    created.append(t.id)
            self.stdout.write(f"Created {len(created)} seed tweets (ids={created})")

        self.stdout.write("Done.")
