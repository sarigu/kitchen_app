from django.contrib import admin
from .models import Room, RoomMembers, Tasks

admin.site.register(Room)
admin.site.register(RoomMembers)
admin.site.register(Tasks)

