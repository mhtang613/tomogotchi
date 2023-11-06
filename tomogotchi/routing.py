from django.urls import path
from tomogotchi import consumers

websocket_urlpatterns = [
    path('furniture/data', consumers.FurnitureConsumer.as_asgi()),
]