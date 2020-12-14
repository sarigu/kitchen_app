from django.contrib import admin
from django.urls import path

from . import views

app_name = 'chat'

urlpatterns = [
    path('chatroom/<str:room_name>/', views.chatroom, name='chatroom'),
]