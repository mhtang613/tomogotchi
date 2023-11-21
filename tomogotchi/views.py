from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db import transaction

from django.http import HttpResponse, Http404

from django.utils import timezone

from tomogotchi.models import *
# from tomogotchi.forms import *

import randomname, random
import imghdr
import json

# Create your views here.

def test_html(request):
    context = {}
    return render(request, 'other_home.html', context)

# Params : this function runs when a player clicks on the "Edit Username" button
# TODO: Migrate this to websockets
def edit_username(request):
    if 'username' not in request.POST or not request.POST['username']:
        context = {}
        context['error'] = True
        context['error_message'] = 'You must enter text to post.'
        return render(request, 'my_home.html', context)
    user_id = request.user
    player = get_object_or_404(Player, user_id=user_id)
    player.name = request.POST['username']

    return redirect(reverse('home'))

# Params : player - an instance of the Player model
# Returns : nothing
# Given a Player instance, give it a unique random name and save it to the db
# NOTE: Runs within atomic section of home
def assign_random_username(player):
    rand_name = randomname.get_name()
    while Player.objects.select_for_update().filter(name=rand_name).exists():
        rand_name = randomname.get_name()
    player.name = rand_name

# Tomogotchi Retrival Funcs
def get_random_tomogotchi(player):
    tomogotchi_list = ['images/sprites/cleffa.gif',
                       'images/sprites/litten.gif',
                       'images/sprites/munchlax.gif',
                       'images/sprites/pichu.gif',
                       'images/sprites/pollywag.gif',
                       'images/sprites/skitty.gif',
                       'images/sprites/umbreon.gif',
                       'images/sprites/whismur.gif',
                       'images/sprites/wooper.gif',]
    rand_tomogotchi = tomogotchi_list[random.randint(0, len(tomogotchi_list)-1 )]
    player.picture = rand_tomogotchi
    player.hunger = 70
    player.mood = 70

# Gets furniture from home and puts it into a list.
@login_required
def get_placed_furniture(player):
    house = player.house
    furniture_list = Furniture.objects.filter(house=house)
    placedFurniture = [{
        'locationX': furniture.locationX,
        'locationY': furniture.locationY,
        'hitboxX': furniture.hitboxX,
        'hitboxY': furniture.hitboxY,
        'picture': furniture.picture.url
    } for furniture in furniture_list]
    return placedFurniture

@login_required
def home(request):
    context = {}
    with transaction.atomic():  # prevent race conditions
        # If this is a new user (no player, no house, CREATE needed things for new user)
        if not Player.objects.select_for_update().filter(user__email=request.user.email).exists():   # get DB lock
            print("New user registering")
            house = House(user=request.user)
            house.save()
            player = Player(user=request.user, house=house, visiting=house, money=0)
            get_random_tomogotchi(player)
            assign_random_username(player)
            player.save()

    my_home = request.user.house
    context['house'] = my_home
    context['placedFurniture'] = get_placed_furniture(request.user.player)
    # update self's visiting room
    request.user.player.visiting = my_home
    request.user.player.save()
    return render(request, 'my_home.html', context)

def visit(request, user_id):
    context = {}
    other_user = get_object_or_404(User, id=user_id)
    context['house'] = other_user.house
    # update self's visiting room
    request.user.player.visiting = other_user.house
    request.user.player.save()
    # place furniture
    context['placedFurniture'] = get_placed_furniture(other_user.player)

    # TODO: Check that users are Mutual Friends
    # TODO: If not, return redirect(reverse('home'))
   
    return render(request, 'other_home.html', context)

def edit_furniture_page(request):
    context = {}
    # furniture_inventory = request.user.house.furnitureOwned
    # filter by size (big vs smol)
    my_home = request.user.house
    context['house'] = my_home
    context['placedFurniture'] = get_placed_furniture(request.user.player)
    # example data
    context['big_list'] = [{'hitboxX': 3*3, 'hitboxY': 2*3}, 
                           {'hitboxX': 4*3, 'hitboxY': 1*3}, 
                           {'hitboxX': 4*3, 'hitboxY': 3*3},
                           {'hitboxX': 3*3, 'hitboxY': 2*3}, 
                           {'hitboxX': 4*3, 'hitboxY': 1*3}, 
                           {'hitboxX': 4*3, 'hitboxY': 3*3},
                           {'hitboxX': 3*3, 'hitboxY': 2*3}, 
                           {'hitboxX': 4*3, 'hitboxY': 1*3}, 
                           {'hitboxX': 4*3, 'hitboxY': 3*3},
                           {'hitboxX': 3*3, 'hitboxY': 2*3}, 
                           {'hitboxX': 4*3, 'hitboxY': 1*3}, 
                           {'hitboxX': 4*3, 'hitboxY': 3*3},
                           {'hitboxX': 3*3, 'hitboxY': 2*3}, 
                           {'hitboxX': 4*3, 'hitboxY': 1*3}, 
                           {'hitboxX': 4*3, 'hitboxY': 3*3},
                           ]
    context['small_list'] = [{'hitboxX': 2*5, 'hitboxY': 2*5}, 
                             {'hitboxX': 1*5, 'hitboxY': 2*5}, 
                             {'hitboxX': 1*5, 'hitboxY': 1*5}]
    
    return render(request, 'edit.html', context)

def login(request):
    context = {}
    # If user already logged in, 
    # don't let them log in with different account 
    # until they log out
    if request.user.is_authenticated:   
        return redirect(reverse('home'))
    return render(request, "login.html", context)

def shop(request):
    furniture_items = Items.objects.filter(is_furniture=True)
    other_items = Items.objects.filter(is_furniture=False)

    context = {'furniture_list' : furniture_items, 'item_list' : other_items}
    return render(request, 'shop.html', context)
    

def get_item_picture(request, name):
    item_instance = Items.objects.get(name=name)
    if not item_instance.picture:
        return Http404
    return HttpResponse(item_instance.picture, content_type = item_instance.content_type)

def buy_item(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            item_id = data['id']
        except:
            return HttpResponse(status=400)
    
        item = get_object_or_404(Items, id=item_id)
        player = get_object_or_404(Player, user=request.user)
        player.inventory.add(item)
        player.save()
        print(f'bought item {item_id}')
        print(f'player:  {player.name}')

        return HttpResponse()

