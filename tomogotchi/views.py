from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from django.http import HttpResponse, Http404

from django.utils import timezone

from tomogotchi.models   import *
# from tomogotchi.forms import *

import randomname
import json

# Create your views here.

def test_html(request):
    context = {}
    return render(request, 'other_home.html', context)

def login(request):
    context = {}
    return render(request, "login.html", context)

    

# Params : player - an instance of the Player model
# Returns : nothing
# Given a Player instance, give it a unique random name and save it to the db
def assign_random_username(player):
    rand_name = randomname.get_name()
    while Player.objects.filter(name=rand_name).exists():
        rand_name = randomname.get_name()
    player.name = rand_name
    player.save()


# Params : this function runs when a player clicks on the "Edit Username" button
def edit_username(request):
    if 'username' not in request.POST or not request.POST['username']:
        context['error'] = True
        context['error_message'] = 'You must enter text to post.'
        return render(request, 'own_home.html', context)
    user_id = request.user
    player = get_object_or_404(Player, user_id=user_id)
    player.name = request.POST['username']

    return redirect('view-own-home')



def shop(request):
    # todo: fill in context with the Items and Furniture models
    furniture_list = [i for i in range(30)]
    item_list = [i for i in range(30)]
    context = {'furniture_list' : furniture_list, 'item_list' : item_list}
    return render(request, 'shop.html', context)
    
