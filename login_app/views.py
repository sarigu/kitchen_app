from django.shortcuts import render, reverse
from django.contrib.auth.models import User #user object comes with attributes like username, password, email, name
from django.contrib.auth import authenticate, login as dj_login, logout as dj_logout
from django.http import HttpResponseRedirect
from django.db import IntegrityError
from .models import PasswordResetRequest
import django_rq
from . messaging import email_password_reset

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


def request_password_reset(request):
   context = {}
   if request.method == "POST":
      user_email = request.POST['email']
      user = None

      if user_email:
            try:
               user = User.objects.get(email=user_email)
            except:
               context = {'message': 'Opps. Something went wrong'}
   
      if user:
            prr = PasswordResetRequest()
            prr.user = user
            prr.save()
            django_rq.enqueue(email_password_reset, {
               'token' : prr.token,
               'email' : prr.user.email,
            })
            return HttpResponseRedirect(reverse('login_app:login'))

   return render(request, 'login_app/password_reset_request.html', context)

def set_new_password(request):
   print("new password")
   context ={}
   if request.method == "POST":
      email = request.POST['email']
      password = request.POST['password']
      confirm_password = request.POST['confirm_password']
      token = request.POST['token']

      user = User.objects.get(email=email)
      reset_request = PasswordResetRequest.objects.get(user=user,token=token)

      if password == confirm_password:
         user.set_password(password)
         user.save()
         reset_request.save()
         return HttpResponseRedirect(reverse('login_app:login'))
      else:
         context = {'message': 'Opps. Something went wrong'}

   return render(request, 'login_app/password_reset.html', context)

