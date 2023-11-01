from django.shortcuts import render

# Create your views here.

def test_html(request):
    context = {}
    return render(request, 'other_home.html', context)

def login(request):
    context = {}
    return render(request, "login.html", context)