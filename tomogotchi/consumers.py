from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from tomogotchi.models import *
from django.contrib.auth.models import User
import json
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.db import transaction

class FurnitureConsumer(WebsocketConsumer):
    channel_name = 'furniture_channel'

    user = None

    def connect(self):
        self.group_name = f'furniture_group_{self.scope["url_route"]["kwargs"]["house_id"]}'
        async_to_sync(self.channel_layer.group_add)(
            self.group_name, self.channel_name
        )

        self.accept()

        if not self.scope["user"].is_authenticated:
            self.send_error(f'You must be logged in')
            self.close()
            return        

        self.user = self.scope["user"]

        self.send_collision_list()

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

    def send_collision_list(self):
        player = get_object_or_404(Player, user=self.user)
        collision_list = Furniture.objects.filter(house=player.house, placed=True)
        send_list = list()
        for furn in collision_list:
            furn_info = {
                'name' : furn.name,
                'true_id' : furn.id,
                'picture' : furn.picture,
                'is_big' : furn.is_big,
                'hitboxX' : furn.hitboxX,
                'hitboxY' : furn.hitboxY,
                'locationX' : furn.locationX,
                'locationY' : furn.locationY,
                'content_type' : furn.content_type,
                'house': furn.house,
                'placed' : furn.placed
            }
        
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'broadcast_event',
                'message': json.dumps(send_list)     # Updated Furniture list goes here
            }
        )

    def broadcast_event(self, event):
        self.send(text_data=event['message'])

class MessagesConsumer(WebsocketConsumer):
    channel_name = 'message_channel'

    user = None

    def connect(self):
        self.group_name = f'message_group_{self.scope["url_route"]["kwargs"]["house_id"]}'
        async_to_sync(self.channel_layer.group_add)(
            self.group_name, self.channel_name
        )

        self.accept()

        if not self.scope["user"].is_authenticated:
            self.send_error(f'You must be logged in')
            self.close()
            return        

        self.user = self.scope["user"]

        self.broadcast_event({'message': f'Connected to Messages Websocket Group {self.group_name}'})
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

    # sends a single message (used for updating already loaded front end)
    def send_message(self, msg):
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
        msg_list = [msg_info]
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'broadcast_event',
                'message': json.dumps(msg_list)
            }
        )
        
    # Sends current list of all messages through websocket
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

    # Saves a new message to the current visiting house (& broadcasts the new msg)
    def add_message(self, data):
        if 'message' not in data or not data['message']:
            self.send_error('you must send a nonempty message')
            return
        # Get house from player current visiting house
        house = self.user.player.visiting
        msg = Message(user=self.user, house=house, text=data['message'], date=timezone.now())
        msg.save()
        self.send_message(msg)
    
    def send_error(self, error_message):
        self.send(text_data=json.dumps({'error': error_message}))

    def broadcast_event(self, event):
        self.send(text_data=event['message'])

class FriendConsumer(WebsocketConsumer):
    channel_name = 'friends_channel'
    
    user = None

    def connect(self):
        self.group_name = f'friends_group_{self.scope["url_route"]["kwargs"]["user_id"]}'
        async_to_sync(self.channel_layer.group_add)(
            self.group_name, self.channel_name
        )

        self.accept()

        if not self.scope["user"].is_authenticated:
            self.send_error(f'You must be logged in')
            self.close()
            return        

        self.user = self.scope["user"]

        self.broadcast_event({'message': f'Connected to Friends Websocket Group {self.group_name}'})
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
        if self.user.player.following.filter(id=friend.id).exists():
            self.send_error(f'You are already following {friend.player.name}')
        # Get Current User for update
        player = self.user.player
        player.following.add(friend)
        player.save()

        if friend.player.following.filter(id=self.user.id).exists():
            self.send_user1_to_user2(friend, self.user)
            self.send_user1_to_user2(self.user, friend)
        else:
            # Get house from player current visiting house
            house = friend.player.house
            notif = f'You recieved a Friend Request from {self.user.player.name}! Accept their request by searching their name in your friends bar.'
            msg = Message(user=self.user, house=house, text=notif, date=timezone.now())
            msg.save()
            self.send_message(friend, msg)
    
    # Send message [user1_info] to user2's friend websocket
    def send_user1_to_user2(self, user1, user2):
        
        friend_info = {
            'id': user1.id,
            'picture': str(user1.player.picture),
            'player_name': user1.player.name, 
        }
        friend_list = [friend_info]  
        
        async_to_sync(self.channel_layer.group_send)(
            f'friends_group_{user2.id}',
            {
                'type': 'broadcast_event',
                'message': json.dumps(friend_list)
            }
        )
    
    # sends a single message (used for updating msg box with friend request)
    def send_message(self, friend, msg):
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
        msg_list = [msg_info]

        friend_msg_group = f'message_group_{friend.player.house.id}'
        async_to_sync(self.channel_layer.group_send)(
            friend_msg_group,
            {
                'type': 'broadcast_event',
                'message': json.dumps(msg_list)
            }
        )

    # Sends current list of messages through websocket
    def send_friend_list(self): 
        # Get following from player (filter by the ones that follow back)
        following = User.objects.filter(player__following__id=self.user.id, followers__id=self.user.player.id)
        """
        DUMMY DATA
        class player_data:
                picture = ''
                def __init__(self, picture) -> None:
                    self.picture = picture
        class user_data:
            id = 0
            first_name = ''
            last_name = ''
            player = None
            def __init__(self, id, picture, first, last):
                self.id = id
                self.player = player_data(picture)
                self.first_name = first
                self.last_name = last

        following = [user_data(1, '/images/icons/pikachu.png', 'first', 'last'), user_data(2, '/images/icons/burger.png', 'nyan', 'burger')] # Test data
        """

        friend_list = list()
        for user in following:
            friend_info = {
                'id': user.id,
                'picture': str(user.player.picture),
                'player_name': user.player.name, 
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

class ShopConsumer(WebsocketConsumer):
    group_name = 'shop_group'
    channel_name = 'shop_channel'

    user = None

    def connect(self):
        print("shop consumer connected")
        async_to_sync(self.channel_layer.group_add)(
            self.group_name, self.channel_name
        )

        self.accept()

        if not self.scope["user"].is_authenticated:
            self.send_error(f'You must be logged in')
            self.close()
            return        

        self.user = self.scope["user"]

        # self.broadcast_list()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name, self.channel_name
        )

    def receive(self, **kwargs):
        print("shop consumer received")
        if 'text_data' not in kwargs:
            self.send_error('you must send text_data')
            return

        try:
            data = json.loads(kwargs['text_data'])
        except json.JSONDecodeError:
            self.send_error('invalid JSON sent to server')
            return
        print(f'data: {data}')
        if 'item_id' not in data:
            self.send_error('item_id not sent in JSON')
            return
        if 'action' not in data:
            self.send_error('action property not sent in JSON')
            return

        action = data['action']
        print(f'action: {action}')

        if action == 'buy-item':
            self.buy_item(data)
            return

        self.send_error(f'Invalid action property: "{action}"')

    # Simply adds the item to the user's inventory, nothing more
    def buy_item(self, data):
        if 'item_id' not in data or not data['item_id']:
            self.send_error('you must select an item to buy')
            return
        item_id = data['item_id']
        item = get_object_or_404(Items, id = item_id)
        player = get_object_or_404(Player, user=self.user)
        player.inventory.add(item)
        item_price = item.price
        if (player.money - item_price >= 0):
            player.money = player.money - item_price
            player.save()
            print(f'player: {player.name} bought item {item_id}')
            if item.is_furniture:
                furn = Furniture(name=item.name,
                                true_id=item.id,
                                picture=item.picture,
                                is_big=item.is_big,
                                hitboxX=item.hitboxX,
                                hitboxY=item.hitboxY,
                                locationX=0,
                                locationY=0,
                                house=player.house,
                                placed=False,
                                content_type=item.content_type)
                furn.save()
            else: # item must be food
                existing_food = Food.objects.filter(true_id=item.id, user_id=self.user.id).first()
                if existing_food:
                    existing_food.count += 1
                    existing_food.save()
                else:
                    food = Food(name=item.name,
                                true_id=item.id,
                                user_id=self.user.id,
                                picture=item.picture,
                                content_type=item.content_type,
                                count=1)
                    food.save()
        
    def send_error(self, error_message):
        self.send(text_data=json.dumps({'error': error_message}))

    def broadcast_event(self, event):
        self.send(text_data=event['message'])

class NameEditingConsumer(WebsocketConsumer):
    channel_name = 'name_editing_channel'
    group_name = f'name_editing_group'

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

        self.broadcast_event({'message': f'Connected to Name Editing Websocket'})
    
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

        if action == 'edit':
            self.validate_name(data)
            return

        self.send_error(f'Invalid action property: "{action}"')

    # sends a single message (used for updating already loaded front end)
    def send_name(self, name):
        self.send(text_data=json.dumps({'name': name}))

    # Saves a new message to the current visiting house (& broadcasts the new msg)
    def validate_name(self, data):
        if 'name' not in data or not data['name']:
            self.send_error('Invalid name')
            return
        name = data['name']
        # Check if name exists/is repeat here
        with transaction.atomic():
            if not Player.objects.select_for_update().filter(name=name).exists():   # get DB lock
                self.user.player.name = name
                self.user.player.save() # update name in DB
                self.send_name(name)
                return
        self.send_error(f'The name {name} is already taken')
    
    def send_error(self, error_message):
        self.send(text_data=json.dumps({'error': error_message}))

    def broadcast_event(self, event):
        self.send(text_data=event['message'])

class FoodConsumer(WebsocketConsumer):
    channel_name = 'food_channel'

    user = None

    def connect(self):
        self.group_name = f'food_group_{self.scope["url_route"]["kwargs"]["user_id"]}'
        async_to_sync(self.channel_layer.group_add)(
            self.group_name, self.channel_name
        )

        self.accept()

        if not self.scope["user"].is_authenticated:
            self.send_error(f'You must be logged in')
            self.close()
            return        

        self.user = self.scope["user"]

        # self.broadcast_list()
        self.send_food_list()
    
    def send_food_list(self):
        print("consumers.py send_food_list")
        my_food = Food.objects.filter(user_id=self.user.id)
        food_list = list()
        for food in my_food:
            food_info = {
                'name' : food.name,
                'food_id' : food.id,
                'food_true_id' : food.true_id,
                'user_id' : food.user_id,
                'count' : food.count,
            }
            food_list.append(food_info)
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'broadcast_event',
                'message': json.dumps(food_list)
            }
        )

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name, self.channel_name
        )

    def receive(self, **kwargs):
        print("consumers.py food receive")
        if 'text_data' not in kwargs:
            self.send_error('you must send text_data')
            return

        try:
            data = json.loads(kwargs['text_data'])
        except json.JSONDecodeError:
            self.send_error('invalid JSON sent to server')
            return
        print(f'data: {data}')
        if 'food_id' not in data:
            self.send_error('food_id not sent in JSON')
            return
        if 'action' not in data:
            self.send_error('action property not sent in JSON')
            return

        action = data['action']
        print(f'action: {action}')

        if action == 'use-food':
            self.broadcast_event({'message': f'use-food event received'}) 
            self.use_food(data)
            return
        if action == 'get':
            self.send_food_list()
            return

        self.send_error(f'Invalid action property: "{action}"')

    # Simply adds the item to the user's inventory, nothing more
    def use_food(self, data):
        print("consumers.py use_food")
        if 'food_id' not in data or not data['food_id']:
            self.send_error('you must select an food to use')
            return
        # update Food model
        food_id = data['food_id']
        
        food_instance = Food.objects.get(id=food_id)
        f = food_instance.count - 1
        food_instance.count = f
        food_instance.save()

        player = get_object_or_404(Player, user=self.user)
        item_instance = get_object_or_404(Items, id=food_instance.true_id)
        hunger_inc = item_instance.hunger
        player.hunger = player.hunger + hunger_inc
        if player.hunger > 100:
            player.hunger = 100
        player.save()
        
        
            
        self.send_food_list()
        
    def send_error(self, error_message):
        self.send(text_data=json.dumps({'error': error_message}))

    def broadcast_event(self, event):
        self.send(text_data=event['message'])
