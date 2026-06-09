from notifications.models import Notification

def send_notification(user, message, notification_type="info"):
    Notification.objects.create(
        user=user,
        message=message,
        notification_type=notification_type,
        is_read=False
    )


