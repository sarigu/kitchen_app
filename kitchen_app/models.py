from django.contrib.auth.models import User
from django.db import models
from django.forms import ModelForm
from django.db.models.query import QuerySet

type_of_room_member = (
    ('admin', 'Admin'),
    ('member', 'Member'),
)


class Room (models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}"


class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = ['name']

class RoomMembers (models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=type_of_room_member, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create(cls, user, room, status):
        roomMember = cls()
        roomMember.user  = user
        roomMember.room = room
        roomMember.status = status
        roomMember.created_at = models.DateTimeField(auto_now_add=True)
        roomMember.save()

    def __str__(self):
        return f"{self.user} - {self.room} - {self.status} - {self.created_at}"

class Tasks (models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    task = models.CharField(max_length=200)
    status = models.BooleanField(default=False)

    @classmethod
    def create(cls, room, text):
        task = cls()
        task.room = room
        task.task = text
        task.save()


    def toggle_status(self):
        self.status = not self.status
        self.save()

    def setUser(self, user):
        self.user = user
        self.save()

    def __str__(self):
        return f"{self.user} - {self.room} - {self.task} - {self.status}"
