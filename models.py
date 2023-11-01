from django.db import models
from django.contrib.auth.models import User

# Items Model
class Items(models.Model):
    # name
    name = models.CharField(max_length=200)
    # image
    picture = models.FileField(blank=True)


# Furniture Model
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

# House Model (The Player's House)
class House(models.Model):
    # user
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # furniture (displayed furniture)
    furniturePlaced = models.ManyToManyField(Furniture, related_name="furnitureActive")
    # owned furniture
    furnitureOwned = models.ManyToManyField(Furniture, related_name="furniture")
    # messages
    # messages = models.ManyToOneField(Messages, on_delete=models.PROTECT, related_name="house") <--- this is a reverse relation from Messages
    # visitors
    visitors = models.ManyToManyField(User, related_name="visitors")

# Messages Model
class Messages(models.Model):
    # Sender:
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Recipient: (ForeignKey => each messages has ONE house, but a house can have many messages)
    house = models.ForeignKey(House, on_delete=models.CASCADE) 
    # Text:
    text = models.CharField(max_length=100)
    # Date:
    date = models.DateTimeField()

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
