import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.other_user_id = int(self.scope["url_route"]["kwargs"]["user_id"])
        self.room_group_name = f"chat_{min(self.user.id, self.other_user_id)}_{max(self.user.id, self.other_user_id)}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        print(f"✅ {self.user} connected to chat with user {self.other_user_id}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"❌ {self.user} disconnected")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)

            if data.get("type") == "heartbeat":
                return

            message = data.get("message")
            if not message:
                return

            msg_obj = await self.save_message(self.user.id, self.other_user_id, message)
            sender = msg_obj.sender
            receiver = msg_obj.receiver

            # Send to chat group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender_id': sender.id,
                    'sender_username': sender.username,
                    'receiver_id': receiver.id,
                    'timestamp': msg_obj.timestamp.strftime('%H:%M'),
                }
            )

            # Also notify the receiver (via notification socket)
            await self.channel_layer.group_send(
                f"notify_{receiver.id}",
                {
                    'type': 'notify_message',
                    'message': message,
                    'sender_id': sender.id,
                    'receiver_id': receiver.id,
                    'sender_username': sender.username,
                    'timestamp': msg_obj.timestamp.strftime('%H:%M'),
                }
            )

        except Exception as e:
            print("⚠️ Receive error:", e)

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @sync_to_async
    def save_message(self, sender_id, receiver_id, content):
        from django.contrib.auth.models import User
        from chat.models import Message

        sender = User.objects.get(id=sender_id)
        receiver = User.objects.get(id=receiver_id)

        return Message.objects.create(
            sender=sender,
            receiver=receiver,
            content=content,
            read=False
        )


# ✅ Notification WebSocket
class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.group_name = f"notify_{self.user.id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        print(f"🔔 Notification channel opened for {self.user.username}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        print(f"🔕 Notification channel closed for {self.user.username}")

    async def notify_message(self, event):
        await self.send(text_data=json.dumps(event))


import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.other_user_id = int(self.scope["url_route"]["kwargs"]["user_id"])
        self.room_group_name = f"chat_{min(self.user.id, self.other_user_id)}_{max(self.user.id, self.other_user_id)}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        print(f"✅ {self.user} connected to chat with user {self.other_user_id}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"❌ {self.user} disconnected")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)

            if data.get("type") == "heartbeat":
                return

            message = data.get("message")
            if not message:
                return

            msg_obj = await self.save_message(self.user.id, self.other_user_id, message)
            sender = msg_obj.sender
            receiver = msg_obj.receiver

            # 🔵 Send to chat WebSocket
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender_id': sender.id,
                    'sender_username': sender.username,
                    'receiver_id': receiver.id,
                    'timestamp': msg_obj.timestamp.strftime('%H:%M'),
                }
            )

            # 🟡 Send to notifications tab
            await self.channel_layer.group_send(
                f"notify_{receiver.id}",
                {
                    'type': 'notify_message',
                    'message': message,
                    'sender_id': sender.id,
                    'receiver_id': receiver.id,
                    'sender_username': sender.username,
                    'timestamp': msg_obj.timestamp.strftime('%H:%M'),
                }
            )

            # 🔴 Send to alert channel (heart icon)
            await self.channel_layer.group_send(
                f"alert_{receiver.id}",
                {
                    'type': 'send_alert',
                    'message': f"New message from {sender.username}"
                }
            )

        except Exception as e:
            print("⚠️ Receive error:", e)

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @sync_to_async
    def save_message(self, sender_id, receiver_id, content):
        from django.contrib.auth.models import User
        from chat.models import Message

        sender = User.objects.get(id=sender_id)
        receiver = User.objects.get(id=receiver_id)

        return Message.objects.create(
            sender=sender,
            receiver=receiver,
            content=content,
            read=False
        )


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.group_name = f"notify_{self.user.id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        print(f"🔔 Notification channel opened for {self.user.username}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        print(f"🔕 Notification channel closed for {self.user.username}")

    async def notify_message(self, event):
        await self.send(text_data=json.dumps(event))


class AlertConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            self.group_name = f"alert_{self.user.id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            print(f"📡 Alert channel connected for {self.user.username}")
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        print(f"🔌 Alert channel disconnected for {self.user.username}")

    async def send_alert(self, event):
        await self.send(text_data=json.dumps({
            'type': 'send_alert',
            'message': event['message']
        }))
