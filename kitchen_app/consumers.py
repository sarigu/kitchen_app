import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync

class NotificationConsumer(AsyncWebsocketConsumer):
    # Function to connect to the websocket
    async def connect(self):
        print(self)
       # Checking if the User is logged in
        if self.scope["user"].is_anonymous:
            # Reject the connection
            self.close()
        else:
            # print(self.scope["user"])   # Can access logged in user details by using self.scope.user, Can only be used if AuthMiddlewareStack is used in the routing.py
            self.group_name = str(self.scope["user"].pk)  # Setting the group name as the pk of the user primary key as it is unique to each user. The group name is used to communicate with the user.
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
        await self.accept()

    # Function to disconnet the Socket
    async def disconnect(self, close_code):
        self.close()
        # pass

        # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        # Send message to room group
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'notify',
                'message': message
            }
        )

    # Custom Notify Function which can be called from Views or api to send message to the frontend
    async def notify(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
   