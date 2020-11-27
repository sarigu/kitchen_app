from django.contrib import admin
from django.urls import path

from . import views

app_name = "kitchen_app"

urlpatterns = [
   path('', views.index, name='index'),
   path('create_room/', views.create_room, name='create_room'),
   path('enter_room/<int:room_id>/', views.enter_room, name='enter_room'),
   path('members/<int:room_id>/', views.members, name='members'),
]
