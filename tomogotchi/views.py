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
    return render(request, 'base.html', context)

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
        return render(request, 'tomogotchi/own_house.html', context)
    user_id = request.user
    player = get_object_or_404(Player, user_id=user_id)
    player.name = request.POST['username']

    return redirect('view-own-house')



# view your own house
def my_house(request):
    context = {}
    return render(request, 'tomogotchi/my_house.html', context)

    
