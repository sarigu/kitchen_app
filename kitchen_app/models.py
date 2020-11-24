from django.contrib.auth.models import User
from django.db import models
from django.forms import ModelForm
from django.db.models.query import QuerySet


class Room (models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}"


class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = ['name']

class RoomMembers (models.Model):
    userID = models.ForeignKey(User, on_delete=models.CASCADE)
    roomID = models.ForeignKey(Room, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create(cls, userID, roomID, status):
        roomMember = cls()
        roomMember.userID  = userID
        roomMember.roomID = roomID
        roomMember.status = status
        roomMember.created_at = models.DateTimeField(auto_now_add=True)
        roomMember.save()

    def __str__(self):
        return f"{self.userID} - {self.roomID} - {self.status} - {self.created_at}"