from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from tomogotchi.models import Items, Furniture, House, Message, Player
from django.contrib.auth.models import User
import json
from django.utils import timezone

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


class MessagesConsumer(WebsocketConsumer):
    group_name = 'message_group'
    channel_name = 'message_channel'

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

        self.broadcast_event({'message': 'Connected to Messages Websocket'})
        self.send_message_list()    # On connection, send over current messages
    
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
        
        # NOTE: DEBUG SEND
        self.broadcast_event({'message': f'Event recieved from user {self.user.id} with data {data}'}) 
        if 'action' not in data or not data['action']:
            self.send_error('your request must contain an action')
            return
        
        action = data['action']

        if action == 'add':
            self.add_message(data)
            return

        if action == 'get':
            self.send_message_list()
            return

        self.send_error(f'Invalid action property: "{action}"')

    # Sends current list of messages through websocket
    def send_message_list(self): 
        # Get house from player current visiting house
        house = self.user.player.visiting
        msg_list = list()
        for msg in house.messages.order_by('date'):
            msg_info = {
                'id': msg.id,
                'text': msg.text,
                'date': msg.date.isoformat(),    # ISO formatted date & time (needs to be read & reformatted in JS)
                'user' : {
                    'id': msg.user.id,
                    'player': {
                        'name': msg.user.player.name
                    }
                },
            }
            msg_list.append(msg_info)  
        
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'broadcast_event',
                'message': json.dumps(msg_list)
            }
        )

    # Saves a new message to the current visiting house
    def add_message(self, data):
        if 'message' not in data or not data['message']:
            self.send_error('you must send a nonempty message')
            return
        # Get house from player current visiting house
        house = self.user.player.visiting
        msg = Message(user=self.user, house=house, text=data['message'], date=timezone.now())
        msg.save()
        self.send_message_list()
        
    
    def send_error(self, error_message):
        self.send(text_data=json.dumps({'error': error_message}))

    def broadcast_event(self, event):
        self.send(text_data=event['message'])

class FriendConsumer(WebsocketConsumer):
    group_name = 'friends_group'
    channel_name = 'friends_channel'
    
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

        self.broadcast_event({'message': 'Connected to Friends Websocket'})
        self.send_friend_list()

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
        
        # NOTE: DEBUG SEND
        self.broadcast_event({'message': f'Event recieved from user {self.user.id} with data {data}'}) 
        
        # Handle friend request logic HERE
        # NOTE: make sure to deny friend requests to self
        if 'action' not in data or not data['action']:
            self.send_error('your request must contain an action')
            return
        
        action = data['action']

        if action == 'add':
            self.add_follower(data)
            return

    # Saves a new following for the current user
    def add_follower(self, data):
        if 'name' not in data or not data['name']:
            self.send_error('you must send a nonempty name for a friend request')
            return
        # Validate Friend Exists & Friend not self
        if not Player.objects.filter(name=data['name']).exclude(user=self.user).exists():
            self.send_error('The requested friend does not exist')
            return
        friend = User.objects.filter(player__name=data['name']).all()[0]
        # Get Current User for update
        player = self.user.player
        player.following.add(friend)
        player.save()

        if friend.player.following.filter(id=self.user.id).exists():
            self.send_friend_list()
        else:
            # Get house from player current visiting house
            house = friend.player.house
            notif = f'You recieved a Friend Request from {self.user.player.name}! Accept their request by searching their name in your friends bar.'
            msg = Message(user=self.user, house=house, text=notif, date=timezone.now())
            msg.save()

    # Sends current list of messages through websocket
    def send_friend_list(self): 
        # Get following from player (filter by the ones that follow back)
        following = User.objects.filter(player__following__id=self.user.id, followers__id=self.user.player.id)
        # # DUMMY DATA
        # class player_data:
        #         picture = ''
        #         def __init__(self, picture) -> None:
        #             self.picture = picture
        # class user_data:
        #     id = 0
        #     first_name = ''
        #     last_name = ''
        #     player = None
        #     def __init__(self, id, picture, first, last):
        #         self.id = id
        #         self.player = player_data(picture)
        #         self.first_name = first
        #         self.last_name = last

        # following = [user_data(1, '/images/icons/pikachu.png', 'first', 'last'), user_data(2, '/images/icons/burger.png', 'nyan', 'burger')] # Test data

        friend_list = list()
        for user in following:
            friend_info = {
                'id': user.id,
                'picture': str(user.player.picture),
                'first_name': user.first_name, 
                'last_name': user.last_name,
            }
            friend_list.append(friend_info)  
        
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'broadcast_event',
                'message': json.dumps(friend_list)
            }
        )
    
    def send_error(self, error_message):
        self.send(text_data=json.dumps({'error': error_message}))

    def broadcast_event(self, event):
        self.send(text_data=event['message'])
