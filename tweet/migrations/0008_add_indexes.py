from django.db import migrations, models


def create_partial_unread_index(apps, schema_editor):
    conn = schema_editor.connection
    if conn.vendor != "postgresql":
        return
    with conn.cursor() as cur:
        cur.execute(
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_notifications_user_unread ON tweet_notification (user_id) WHERE (is_read = false);"
        )


def drop_partial_unread_index(apps, schema_editor):
    conn = schema_editor.connection
    if conn.vendor != "postgresql":
        return
    with conn.cursor() as cur:
        cur.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_notifications_user_unread;")


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("tweet", "0007_add_gin_index_search"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="comment",
            index=models.Index(fields=["parent"], name="tweet_comment_parent_idx"),
        ),
        migrations.RunPython(create_partial_unread_index, drop_partial_unread_index),
    ]
