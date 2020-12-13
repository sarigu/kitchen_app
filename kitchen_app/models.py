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

class UserProfile(models.Model):
   user = models.OneToOneField(User, on_delete=models.CASCADE)
   phone = models.CharField(max_length=25, blank=True)

   def __str__(self):
      return f"{self.user} - {self.user.email} -  {self.user.first_name} -  {self.user.last_name} - {self.phone}"


class Room (models.Model):
    name = models.CharField(max_length=100)
    backgroundImage = models.CharField(max_length=100, blank=True, null=True)
    mobilePayBox = models.CharField(max_length=6 , blank=True, null=True )
    fund = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} - {self.backgroundImage} - {self.mobilePayBox} - {self.fund}"


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

class Rules (models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    text = models.CharField(max_length=2000, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.room} - {self.created_at} - {self.text} - {self.updated_at}"


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
    active = models.BooleanField(default=False)
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
        like.active = True
        like.content_type = content_type
        like.object_id = object_id
        like.save()

    def toggle_active(self):
        self.active = not self.active
        self.save()

    def __str__(self):
        return f"{self.user} - {self.room}  - {self.type}  - {self.active} - {self.object_id} - {self.content_object}"

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
    likes = GenericRelation(Likes, related_query_name='likes')
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


