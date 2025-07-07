from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def send_alert_to_user(user_id: int, message: str) -> None:
    """
    Send a real-time alert to a user's alert_<user_id> group.
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"alert_{user_id}",
        {
            "type": "send_alert",   # matches AlertConsumer.send_alert
            "message": message,
        }
    )
