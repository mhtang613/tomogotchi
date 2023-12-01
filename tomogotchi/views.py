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
from collections import Counter

import randomname, random
import imghdr
import json
import os
import logging

logger = logging.getLogger(__name__)

# Create your views here.

# Params : player - an instance of the Player model
# Returns : nothing
# Given a Player instance, give it a unique random name and save it to the db
# NOTE: Runs within atomic section of home
def assign_random_username(player):
    rand_name = randomname.get_name(adj=('speed','shape','sound','colors','taste'),
                                    noun=('cats','dogs','apex_predators','birds','fish'))
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
    player.money = 10000

# Gets furniture from home and puts it into a list.
@login_required
def get_placed_furniture(player):
    house = player.house
    furniture_list = Furniture.objects.filter(house=house, placed=True).order_by('-hitboxX')
    placedFurniture = [{
        'name': furniture.name,
        'true_id': furniture.true_id,
        'locationX': furniture.locationX,
        'locationY': furniture.locationY,
        'hitboxX': furniture.hitboxX,
        'hitboxY': furniture.hitboxY,
        'picture': furniture.picture.url
    } for furniture in furniture_list]
    return placedFurniture

# Gets set of visitors for a house:
@login_required
def get_visitors(house):
    visitors = Player.objects.filter(visiting=house)
    return set(visitors)

# Collision check between sprite and furniture:
def is_collide(xV, yV, xF, yF, xHF, yHF):
    # Sprites have a hitbox of 2x2
    (xV1, xV2) = (xV, xV+2)
    (yV1, yV2) = (yV, yV+2)
    # Furniture Hitbox:
    (xF1, xF2) = (xF, xF + xHF)
    (yF1, yF2) = (yF, yF + yHF)
    # Bounds check (20x20 screen)
    if not (1 <= xV1 and xV2 <= 20 and
            1 <= yV1 and yV2 <= 20):
        return False
    # Collision check
    # Check for overlap in X and Y coordinates
    overlap_x = (xV1 < xF2) and (xF1 < xV2)
    overlap_y = (yV1 < yF2) and (yF1 < yV2)

    return overlap_x and overlap_y

# Generate open slots for sprites:
def find_spaces(context):
    res = set()
    for i in range(1,20):
        for j in range(1,20):
            valid = True
            for furniture in context['placedFurniture']:
                xF = furniture['locationX']
                yF = furniture['locationY']
                xHF = furniture['hitboxX']
                yHF = furniture['hitboxY']
                if is_collide(i, j, xF, yF, xHF, yHF): valid = False
            if valid: res.add((i,j))
    return res

# Place visitors into unoccupied spaces
    # Requires context to have context['placedFurniture'] populated
def place_visitors(context, house):
    # Find necessary info
    visitors = list(get_visitors(house))
    open_spaces = list(find_spaces(context))
    random.shuffle(open_spaces) #in-place shuffle
    context['visitors'] = []
    # Populate as many open spaces as possible:
    while open_spaces and visitors:
        space = open_spaces.pop()
        visitor = visitors.pop()
        context["visitors"].append({
            "visitor" : visitor,
            "locationX" : space[0],
            "locationY" : space[1],
            "picture" : visitor.picture
        })
    # return updated context
    return context


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
    # place furniture
    context['placedFurniture'] = get_placed_furniture(request.user.player)
    # update self's visiting room
    request.user.player.visiting = my_home
    request.user.player.save()
    # place visitors
    context = place_visitors(context, my_home)
    # Needed for background tiles:
    context["range10"] = [i * 2 + 1 for i in range(10)]
    context["range20"] = [i + 1 for i in range(20)]
    return render(request, 'my_home.html', context)

@login_required
def visit(request, user_id):
    context = {}
    other_user = get_object_or_404(User, id=user_id)

    # Check that users are Mutual Friends
    # If not, return redirect(reverse('home'))
    if not other_user.player.following.filter(id=request.user.id).exists():
        return redirect(reverse('home'))

    context['house'] = other_user.house
    # update self's visiting room
    request.user.player.visiting = other_user.house
    request.user.player.save()
    # place furniture
    context['placedFurniture'] = get_placed_furniture(other_user.player)
    # Needed for background tiles:
    context["range10"] = [i * 2 + 1 for i in range(10)]
    context["range20"] = [i + 1 for i in range(20)]
    # place visitors
    context = place_visitors(context, other_user.house)
   
    return render(request, 'other_home.html', context)

# for displaying the inventory of furniture in edit.html
@login_required
def edit_furniture_page(request):
    context = {}
    if request.method == 'POST':
        # Remove furniture is only valid post request
        my_furniture = Furniture.objects.filter(house__user=request.user, placed=True).update(placed=False)
    my_home = request.user.house
    context['house'] = my_home
    context['placedFurniture'] = get_placed_furniture(request.user.player)
    
    my_furniture = Furniture.objects.filter(house=request.user.house)
    counter = Counter(furn.true_id for furn in my_furniture)


    unique_big_set = set()
    unique_small_set = set()
    context['big_list'] = []
    context['small_list'] = []
    for item in my_furniture:
        if not item.placed:
            if item.is_big and item.true_id not in unique_big_set:
                context['big_list'].append((item, counter[item.true_id], item.hitboxX, item.hitboxY))
                unique_big_set.add(item.true_id)
            elif not item.is_big and item.true_id not in unique_small_set:
                context['small_list'].append((item, counter[item.true_id], item.hitboxX, item.hitboxY))
                unique_small_set.add(item.true_id)

        
    # Needed for background tiles:
    context["range10"] = [i * 2 + 1 for i in range(10)]
    context["range20"] = [i + 1 for i in range(20)]

    return render(request, 'edit.html', context)

def login(request):
    context = {}
    # If user already logged in, 
    # don't let them log in with different account 
    # until they log out
    if request.user.is_authenticated:   
        return redirect(reverse('home'))
    return render(request, "login.html", context)

@login_required
def shop(request):
    furniture_items = Items.objects.filter(is_furniture=True).order_by("name")
    other_items = Items.objects.filter(is_furniture=False).order_by("price")
    context = {'furniture_list' : furniture_items, 'item_list' : other_items}
    
    return render(request, 'shop.html', context)
    
@login_required
def get_item_picture(request, name):
    item_instance = Items.objects.get(name=name)
    if not item_instance.picture:
        return Http404
    return HttpResponse(item_instance.picture, content_type = item_instance.content_type)

# This function is never called, instead we use buy_items in consumers.py
# def buy_item(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             item_id = data['id']
#         except:
#             return HttpResponse(status=400)
    
#         item = get_object_or_404(Items, id=item_id)
#         player = get_object_or_404(Player, user=request.user)
#         player.inventory.add(item)
#         player.save()

#         if item.is_furniture:
#             furn = Furniture(name=item.name,
#                                 picture=item.picture,
#                                 is_big=item.is_big,
#                                 hitboxX=item.hitboxX,
#                                 hitboxY=item.hitboxY,
#                                 locationX=0,
#                                 locationY=0,
#                                 house=player.house,
#                                 placed=False,
#                                 content_type=item.content_type)
#             furn.save()
#         return HttpResponse()
