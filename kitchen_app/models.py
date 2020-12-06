from django.contrib.auth.models import User
from django.db import models
from django.forms import ModelForm
from django.db.models.query import QuerySet
from django.db.models.signals import post_save
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation

type_of_room_member = (
    ('admin', 'Admin'),
    ('member', 'Member'),
)

event_type_choices = (
    ('getTogether', 'GetTogether'),
    ('kitchenMeeting', 'KitchenMeeting'),
    ('kitchenCleaning', 'kitchenCleaning'),
)

type_of_like = (
    ('post', 'Post'),
    ('comment', 'Comment'),
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
    deadline = models.CharField(max_length=10, null=True, blank=True, unique=True)

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
        return f"{self.title}- {self.pk} - {self.description} - {self.room} - {self.start_date} - {self.end_date} - {self.created_at}"

class Likes (models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=type_of_like)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    @classmethod
    def create(cls, user, room, type, content_type, object_id):
        like = cls()
        like.user = user
        like.room = room
        like.type = type
        like.content_type = content_type
        like.object_id = object_id
        like.save()

    def __str__(self):
        return f"{self.user} - {self.room} - {self.type} - {self.content_type} - {self.object_id} - {self.content_object}"

class Posts (models.Model):
    text = models.CharField(max_length=500)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    likes = GenericRelation(Likes,related_query_name='likes')
    created_at = models.DateField(auto_now_add=True)

    @classmethod
    def create(cls, text, user, room):
        post = cls()
        post.text = text
        post.user = user
        post.room = room
        post.created_at = models.DateTimeField(auto_now_add=True)
        post.save()

    def __str__(self):
        return f"{self.text} -  {self.user} -  {self.room} - {self.created_at}"


class Comments (models.Model):
    text = models.CharField(max_length=250)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = models.ForeignKey(Posts, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True)

    @classmethod
    def create(cls, text, user, parent, room):
        comment = cls()
        comment.text = text
        comment.user = user
        comment.parent = parent
        comment.room = room
        comment.created_at = models.DateTimeField(auto_now_add=True)
        comment.save()

    def __str__(self):
        return f"{self.text} - {self.pk} - {self.user} - {self.created_at} - {self.parent}"


