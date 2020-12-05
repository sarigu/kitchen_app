from django.contrib import admin
from .models import Room, RoomMembers, Tasks, Subtasks, Events, Posts, Comments, Likes

admin.site.register(Room)
admin.site.register(RoomMembers)
admin.site.register(Tasks)
admin.site.register(Subtasks)
admin.site.register(Events)
admin.site.register(Posts)
admin.site.register(Comments)
admin.site.register(Likes)

