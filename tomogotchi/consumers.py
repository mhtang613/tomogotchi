from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from tomogotchi.models import Items, Furniture, House, Message, Player
import json


class FurnitureConsumer(WebsocketConsumer):
    group_name = 'furniture_group'
    channel_name = 'furniture_channel'

    user = None

    def connect(self):
        async_to_sync(self.channel_layer.group_add)(
            self.group_name, self.channel_name
        )

        self.accept()

        if not self.scope["user"].is_authenticated:
            self.send_error(f'You must be logged in')
            self.close()
            return        

        self.user = self.scope["user"]

        self.broadcast_list()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name, self.channel_name
        )

    def receive(self, **kwargs):
        if 'text_data' not in kwargs:
            self.send_error('you must send text_data')
            return

        try:
            data = json.loads(kwargs['text_data'])
        except json.JSONDecodeError:
            self.send_error('invalid JSON sent to server')
            return

        if 'id' not in data:
            self.send_error('furniture id not sent in JSON')
            return
        if 'action' not in data:
            self.send_error('action property not sent in JSON')
            return

        action = data['action']

        if action == 'place':
            self.received_place(data)
            return

        if action == 'remove':
            self.received_remove(data)
            return

        self.send_error(f'Invalid action property: "{action}"')

    # User puts furniture in room
    def received_place(self, data):
        if 'pos' not in data:
            self.send_error('"pos" property not sent in JSON')
            return
        
        id = data['id']
        pos_x = data['pos']['x']
        pos_y = data['pos']['y']
        try:
            furniture = Furniture.objects.get(id=id)
        except Furniture.DoesNotExist:
            self.send_error(f'Furniture with id={id} Does Not Exist.')
        if (furniture.house.user != self.user):    # NOTE: Uncertain if this comparison works... MUST TEST!!
            self.send_error(f'You cannot place furniture you do not own.')
        
        furniture.locationX = pos_x
        furniture.locationY = pos_y
        furniture.save()
        self.broadcast_list()

    # User removes furniture from room
    def received_remove(self, data):
        id = data['id']
        try:
            furniture = Furniture.objects.get(id=id)
        except Furniture.DoesNotExist:
            self.send_error(f"Furniture with id={id} does not exist")
            return

        self.user.furnitureActive.remove(furniture)     # May need to retrieve user from database!!
        self.broadcast_list()

    def send_error(self, error_message):
        self.send(text_data=json.dumps({'error': error_message}))

    def broadcast_list(self):
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'broadcast_event',
                'message': json.dumps()     # Updated Furniture list goes here
            }
        )

    def broadcast_event(self, event):
        self.send(text_data=event['message'])


class TestConsumer(WebsocketConsumer):
    group_name = 'test_group'
    channel_name = 'test_channel'

    user = None

    def connect(self):
        async_to_sync(self.channel_layer.group_add)(
            self.group_name, self.channel_name
        )

        self.accept()

        if not self.scope["user"].is_authenticated:
            self.send_error(f'You must be logged in')
            self.close()
            return        

        self.user = self.scope["user"]

        self.broadcast_event({'message': 'Connected to Websocket'})
    
    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name, self.channel_name
        )

    def receive(self, **kwargs):
        if 'text_data' not in kwargs:
            self.send_error('you must send text_data')
            return

        try:
            data = json.loads(kwargs['text_data'])
        except json.JSONDecodeError:
            self.send_error('invalid JSON sent to server')
            return

        self.broadcast_event({'message': f'Event recieved from user {self.user} with data {data}'})
    
    def send_error(self, error_message):
        self.send(text_data=json.dumps({'error': error_message}))

    def broadcast_event(self, event):
        self.send(text_data=event['message'])