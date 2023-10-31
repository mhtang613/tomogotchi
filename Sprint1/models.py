from django.db import models
from django.contrib.auth.models import User


# Items Model
class Items(model.Model):
    # name
    name = models.CharField(max_length=200)
    # image
    picture = models.FileField(blank=True)


# Furniture Model
class Furniture(model.Model):
    # name
    name = models.CharField(max_length=200)
    # image
    picture = models.FileField(blank=True)
    # hitbox
    # locations

# House Model (The Player's House)
class House(model.Models):
    # user
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # furniture (displayed furniture)
    furniturePlaced = models.ManyToManyField(Furniture, on_delete=models.PROTECT)
    # owned furniture
    # messages
    # visitors:

# Player Model: (The Player's data)
class Player(model.Models):
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
    
# Messages Model
class Messages(model.Model):
    # Sender:
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # Recipient:
    house = models.ManyToOne(House, on_delete=models.CASCADE)
    # Text:
    text    = models.CharField(max_length=100)
    # Date:
    date    = models.DateTimeField()
