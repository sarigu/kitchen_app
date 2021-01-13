from django.contrib import admin
from django.urls import path, include

from . import views

app_name = 'kitchen_app'

urlpatterns = [
   path('', views.index, name='index'),
   path('index/', views.index, name='index'),
   path('create_room/', views.create_room, name='create_room'),
   path('enter_room/<int:room_id>/', views.enter_room, name='enter_room'),
   path('members/<int:room_id>/', views.members, name='members'),
   path('profile/<int:room_id>/', views.profile, name='profile'),
   path('kitchen_fund/<int:room_id>/', views.kitchen_fund, name='kitchen_fund'),
   path('weekly_cleaning_list/<int:room_id>/', views.weekly_cleaning_list, name='weekly_cleaning_list'),
   path('cleaning_schedule/<int:room_id>/', views.cleaning_schedule, name='cleaning_schedule'),
   path('create_event/<int:room_id>/', views.create_event, name='create_event'),
   path('event/<int:room_id>/<int:event_id>/', views.event, name='event'),
   path('rules/<int:room_id>/', views.rules, name='rules'),
   path('completed_tasks/<int:room_id>/', views.completed_tasks, name='completed_tasks'),
   path('edit_profile/<int:room_id>/', views.edit_profile, name='edit_profile'),
   path('admin_view/<int:room_id>/', views.admin_view, name='admin_view'),  
   path('delete_event/<int:room_id>/', views.delete_event, name='delete_event'),  
   path('admin_completed_tasks/<int:room_id>/', views.admin_completed_tasks, name='admin_completed_tasks'), 
   path('admin_members/<int:room_id>/', views.admin_members, name='admin_members'),  
   path('admin_schedule/<int:room_id>/', views.admin_schedule, name='admin_schedule'),  
   path('admin_rules/<int:room_id>/', views.admin_rules, name='admin_rules'),  
   path('edit_rules/<int:room_id>/', views.edit_rules, name='edit_rules'),  
   path('view_images/<int:room_id>/', views.view_images, name='view_images'),  
   path('set_new_bg_image/<int:room_id>/', views.set_new_bg_image, name='set_new_bg_image'),  
   path('admin_kitchen_fund/<int:room_id>/', views.admin_kitchen_fund, name='admin_kitchen_fund'),
   path('admin_cleaning_tasks/<int:room_id>/', views.admin_cleaning_tasks, name='admin_cleaning_tasks'),
   path('enter_chat/<int:room_id>/', views.enter_chat, name='enter_chat'),
   path('leave_room/<int:room_id>/', views.leave_room, name='leave_room'),
   path('admin_edit_room/<int:room_id>/', views.admin_edit_room, name='admin_edit_room'),
   path('room_info/<int:room_id>/', views.room_info, name='room_info'),
]
