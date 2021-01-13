import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
       # check if the User is logged in
        if self.scope["user"].is_anonymous:
            self.close()
        else:
            self.group_name = str(self.scope["user"].pk)  
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
        await self.accept()


    async def disconnect(self, close_code):
        self.close()
 

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'notify',
                'message': message
            }
        )


    async def notify(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))
   