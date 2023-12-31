from django.urls import path
from tomogotchi import consumers

websocket_urlpatterns = [
    path('editname', consumers.NameEditingConsumer.as_asgi()),
    path('friends/data/<int:user_id>', consumers.FriendConsumer.as_asgi()),
    path('messages/data/<int:house_id>', consumers.MessagesConsumer.as_asgi()),
    path('furniture/data/<int:house_id>', consumers.FurnitureConsumer.as_asgi()),
    path('shop/data', consumers.ShopConsumer.as_asgi()),
    path('food/data/<int:user_id>', consumers.FoodConsumer.as_asgi()),
]