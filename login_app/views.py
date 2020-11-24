from django.shortcuts import render, reverse
from django.contrib.auth.models import User #user object comes with attributes like username, password, email, name
from django.contrib.auth import authenticate, login as dj_login, logout as dj_logout
from django.http import HttpResponseRedirect
from django.db import IntegrityError
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

def logout(request):
   dj_logout(request)
   return HttpResponseRedirect(reverse('login_app:login'))

def sign_up(request):
   context = {}
   if request.method == 'POST':
      username = request.POST['username']
      password = request.POST['password']
      confirm_password = request.POST['confirm_password']
      email = request.POST['email']
      if password == confirm_password:
         try:
            User.objects.create_user(username, email, password)
            return HttpResponseRedirect(reverse('login_app:login'))
         except IntegrityError as e:
            context = {'error': 'Username exists try a different name.'}
      else:
         context = {'error': 'Passwords do not match.'}
   return render(request, 'login_app/sign_up.html', context)


