from django.urls import path
from tomogotchi import consumers

websocket_urlpatterns = [
    path('test/data', consumers.TestConsumer.as_asgi()),
    path('furniture/data', consumers.FurnitureConsumer.as_asgi()),
]