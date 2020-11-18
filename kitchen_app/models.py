from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Room(models.Model):
    name = models.CharField(max_length=250)

    @classmethod
    def create(cls, name):
        room = cls()
        room.name = name
        room.save()

    def __str__(self):
        return f"{self.name}"
