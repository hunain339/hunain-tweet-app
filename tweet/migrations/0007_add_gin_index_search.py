from django.db import migrations


def create_trgm_and_index(apps, schema_editor):
    # Only run on PostgreSQL
    conn = schema_editor.connection
    if conn.vendor != "postgresql":
        return
    with conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
        cur.execute(
            "CREATE INDEX IF NOT EXISTS tweet_text_trgm_idx ON tweet_tweet USING gin (text gin_trgm_ops);"
        )


def drop_trgm_and_index(apps, schema_editor):
    conn = schema_editor.connection
    if conn.vendor != "postgresql":
        return
    with conn.cursor() as cur:
        cur.execute("DROP INDEX IF EXISTS tweet_text_trgm_idx;")
        cur.execute("DROP EXTENSION IF EXISTS pg_trgm;")


class Migration(migrations.Migration):

    dependencies = [
        ("tweet", "0006_alter_tweet_photo_url"),
    ]

    operations = [
        migrations.RunPython(create_trgm_and_index, drop_trgm_and_index),
    ]
