from django.shortcuts import render, reverse
from django.contrib.auth.models import User #user object comes with attributes like username, password, email, name
from django.contrib.auth import authenticate, login as dj_login, logout 
from django.http import HttpResponseRedirect
from . import models

# Create your views here.
def login(request):
   if request.method == 'POST':
      username = request.POST['username']
      password = request.POST['password']
      user = authenticate(request, username=username, password=password)
      if user:
         dj_login(request, user)
         return HttpResponseRedirect(reverse('kitchen_app:index'))
      else:
         context = {'error': 'wrong email or password.'}
   return render(request, 'login_app/login.html')

def sign_up(request):
   context = {}
   if request.method == 'POST':
      username = request.POST['username']
      password = request.POST['password']
      confirm_password = request.POST['confirm_password']
      email = request.POST['email']
      if password == confirm_password:
         if User.objects.create_user(username, email, password):
            return HttpResponseRedirect(reverse('login_app:login'))
         else:
            context = {'error': 'Could not create user - try somethig else.'}
      else:
         context = {'error': 'Passwords do not match.'}
   return render(request, 'login_app/sign_up.html', context)


