from django.contrib.auth.models import User
from django.db import models
from django.forms import ModelForm
from django.db.models.query import QuerySet
from django.db.models.signals import post_save

type_of_room_member = (
    ('admin', 'Admin'),
    ('member', 'Member'),
)

event_type_choices = (
    ('getTogether', 'GetTogether'),
    ('kitchenMeeting', 'KitchenMeeting'),
    ('kitchenCleaning', 'kitchenCleaning'),
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
        return f"{self.user} - {self.user.pk} - {self.room} - {self.status} - {self.created_at}"

class Tasks (models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    task = models.CharField(max_length=200)
    status = models.BooleanField(default=False)
    type = models.CharField(max_length=50, null=True, blank=True)
    deadline = models.CharField(max_length=10, null=True, blank=True)

    @classmethod
    def create(cls, user, room, text, type, deadline):
        task = cls()
        task.user = user
        task.room = room
        task.task = text
        task.type = type
        task.deadline = deadline
        task.save()

    def toggle_status(self):
        self.status = not self.status
        self.save()

    def deleteTask(sender, instance, **kwargs):
        queryset = Subtasks.objects.filter(task=instance.task.pk)
        subtasks = []
        doneTasks = []
        for subtask in queryset: 
            subtasks.append(subtask)
            if(subtask.status == True):
                doneTasks.append(subtask)

        if(len(doneTasks) == len(subtasks)):
            instance.task.status = True
            instance.task.save()

    def setUser(self, user):
        self.user = user
        self.save()
    
    def __str__(self):
        return f"{self.user} - {self.room} - {self.task} - {self.type} - {self.status} - {self.deadline}"
    

class Subtasks (models.Model):
    task = models.ForeignKey(Tasks, on_delete=models.CASCADE)
    taskDescription = models.CharField(max_length=200)
    status = models.BooleanField(default=False)

    def toggle_status(self):
        self.status = not self.status
        self.save()

    def __str__(self):
        return f"{self.task} - {self.pk} - {self.taskDescription} - {self.status}"


post_save.connect(Tasks.deleteTask, sender=Subtasks)

class Events (models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=event_type_choices, default="getTogether")
    start_date = models.DateField()
    end_date =  models.DateField()
    created_at = models.DateField(auto_now_add=True)
    
    @classmethod
    def create(cls, title, description, room, type, start_date, end_date):
        event = cls()
        event.title = title
        event.description = description
        event.room = room
        event.type = type
        event.start_date = start_date
        event.end_date = end_date
        event.created_at = models.DateTimeField(auto_now_add=True)
        event.save()

    def __str__(self):
        return f"{self.title} - {self.description} - {self.room} - {self.start_date} - {self.end_date} - {self.created_at}"

