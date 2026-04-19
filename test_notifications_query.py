import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hunain_project.settings')
django.setup()

from tweet.models import Notification

def test_notifications_query_all():
    print("Testing notifications query for ALL users...")
    try:
        notifications_list = (
            Notification.objects
            .select_related('comment__user', 'comment__tweet__user')
            .only('id', 'user_id', 'comment_id', 'notification_type', 'is_read', 'created_at',
                  'comment__id', 'comment__text', 'comment__user__username',
                  'comment__tweet__id', 'comment__tweet__text')
            .order_by('-created_at')
        )
        # Force execution
        for n in notifications_list:
            print(f"Notification {n.id} for user {n.user_id}")
            print(f"  Comment: {n.comment.text}")
            print(f"  Tweet: {n.comment.tweet.text}")
        
        print("Query successful!")
    except Exception as e:
        print(f"Query failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_notifications_query_all()
