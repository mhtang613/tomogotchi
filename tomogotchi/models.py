from django.db import models
from django.contrib.auth.models import User

# Items Model
class Items(models.Model):
    # name
    name = models.CharField(max_length=200)
    # image
    picture = models.FileField(blank=True)

    def __str__(self):
        return f'id={self.id}, name="{self.name}", picture={self.picture}'

# House Model (The Player's House)
class House(models.Model):
    # user
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="house")
    # furniture (displayed furniture) <-- Use filter (trading between lists is not necessary)
    # owned furniture <-- reverse relation 
    # messages
    # messages = models.ManyToOneField(Messages, on_delete=models.PROTECT, related_name="house") <--- this is a reverse relation from Messages
    # visitors
    visitors = models.ManyToManyField(User, related_name="visitors")

    def __str__(self):
        return f'id={self.id}, user={self.user.username}'

# Furniture Model
# Buying a furniture must create a new instance (bc pos must be unique)
class Furniture(models.Model):
    # name
    name = models.CharField(max_length=200)
    # image
    picture = models.FileField(blank=True)
    # hitbox
    hitboxX = models.IntegerField()
    hitboxY = models.IntegerField()
    # location
    locationX = models.IntegerField()
    locationY = models.IntegerField()
    
    # Each furniture belongs to exactly 1 house (house can have many furniture)
    house = models.ForeignKey(House, on_delete=models.PROTECT, related_name="furnitureOwned")
    # True iff the furniture is placed in room
    placed = models.BooleanField()

    def __str__(self):
        return f'id={self.id}, name="{self.name}", hitbox=({self.hitboxX},{self.hitboxY}), location=({self.locationX},{self.locationY})'

# Messages Model
class Message(models.Model):
    # Sender: (each message has ONE sender, but each user can send many messages)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # Recipient: (ForeignKey => each message has ONE house, but a house can have many messages)
    house = models.ForeignKey(House, on_delete=models.CASCADE) 
    # Text:
    text = models.CharField(max_length=100)
    # Date:
    date = models.DateTimeField()
    def __str__(self):
        return f'id={self.id}, user={self.user.username}, text="{self.text}", date={self.date}'

# Player Model: (The Player's data)
class Player(models.Model):
    # user
    user = models.OneToOneField(User, on_delete=models.PROTECT, related_name="user")
    # house
    house = models.OneToOneField(House, on_delete=models.PROTECT, related_name="house")
    # friends
    following = models.ManyToManyField(User, related_name="following")
    # inventory (all items and food owned)
    inventory = models.ManyToManyField(Items, related_name="inventory")
    # tamagotchi info
    name = models.CharField(max_length=200)
    picture = models.FileField(blank=True)
    hunger = models.IntegerField()
    mood = models.IntegerField()

    def __str__(self):
        return f'id={self.id}, user="{self.user.username}"'
