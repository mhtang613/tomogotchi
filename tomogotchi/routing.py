from django.urls import path
from tomogotchi import consumers

websocket_urlpatterns = [
    path('friends/data/<int:user_id>', consumers.FriendConsumer.as_asgi()),
    path('messages/data/<int:home_id>', consumers.MessagesConsumer.as_asgi()),
    path('furniture/data/<int:home_id>', consumers.FurnitureConsumer.as_asgi()),
    path('shop/data', consumers.ShopConsumer.as_asgi()),
]