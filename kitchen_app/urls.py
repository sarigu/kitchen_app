from django.contrib import admin
from django.urls import path

from . import views

app_name = "kitchen_app"

urlpatterns = [
   path('', views.index, name='index'),
   path('create_room/', views.create_room, name='create_room'),
]
