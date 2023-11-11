from django.urls import path
from tomogotchi import consumers

websocket_urlpatterns = [
    path('friends/data', consumers.FriendConsumer.as_asgi()),
    path('messages/data', consumers.MessagesConsumer.as_asgi()),
    path('furniture/data', consumers.FurnitureConsumer.as_asgi()),
]