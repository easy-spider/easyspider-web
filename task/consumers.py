# chat/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json


class TaskConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_pk = self.scope['url_route']['kwargs']['user_pk']
        self.group_name = 'task_%s' % self.user_pk

        # Join room group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'task_message',
                'message': message
            }
        )

    # Receive message from room group
    async def task_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))


def send_group_msg(user_pk, task_pk, message):
    # 从Channels的外部发送消息给Channel
    """
    :param user_pk:
    :param task_pk:
    :param message:
    :return:
    """
    message["task_id"] = task_pk
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'task_{}'.format(user_pk),  # 构造Channels组名称
        {
            "type": "task_message",
            "message": message,
        }
    )
