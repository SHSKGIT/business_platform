from channels.generic.websocket import AsyncWebsocketConsumer
import json
import asyncio

from .sqlalchemy_setup import get_dbsession
from .models.auth_entity import AuthEntity


class PurchaseConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"]
        self.room_group_name = f"purchase_{self.user_id}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")

        if action == "process_purchase":
            await self.process_purchase(data)

    async def process_purchase(self, data):
        user_id = data.get("user_id")

        # Query the database for the user
        dbsession = next(get_dbsession())  # Get the SQLAlchemy session
        user = dbsession.query(AuthEntity).filter_by(id=user_id).one_or_none()
        dbsession.close()

        # Send processing message immediately
        await self.send(
            text_data=json.dumps(
                {
                    "status": "processing",
                    "message": f"Processing purchase for user {user.username}...",
                }
            )
        )

        # Simulate processing time (3 seconds delay)
        await asyncio.sleep(3)

        # Send finished message after processing
        await self.send(
            text_data=json.dumps(
                {
                    "status": "finished",
                    "message": f"Purchase completed for user {user.username}!",
                }
            )
        )
