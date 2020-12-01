from django.contrib import admin
from django.urls import path

from . import views

app_name = "kitchen_app"

urlpatterns = [
   path('', views.index, name='index'),
   path('index/', views.index, name='index'),
   path('create_room/', views.create_room, name='create_room'),
   path('enter_room/<int:room_id>/', views.enter_room, name='enter_room'),
   path('members/<int:room_id>/', views.members, name='members'),
   path('profile/', views.profile, name='profile'),
   path('kitchen_fund/<int:room_id>/', views.kitchen_fund, name='kitchen_fund'),
   path('weekly_cleaning/<int:room_id>/', views.weekly_cleaning, name='weekly_cleaning'),
   path('schedule/<int:room_id>/', views.schedule, name='schedule'),
]
