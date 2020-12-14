from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from . models import UserProfile, Subtasks, Tasks, RoomMembers, Chat, ChatMembers


@receiver(post_save, sender=User, dispatch_uid="create_user_profile")
def create_user_profile(sender, instance, **kwargs):
   if not UserProfile.objects.filter(user=instance).exists():
      user_profile = UserProfile()
      user_profile.user = instance
      user_profile.save()

@receiver(post_save, sender=Subtasks, dispatch_uid="mark_task_as_done")
def mark_task_as_done(sender, instance, **kwargs):
   if Subtasks.objects.filter(task=instance.task.pk).count() == Subtasks.objects.filter(task=instance.task.pk).filter(status=True).count():
      instance.task.status = True
      instance.task.save()

@receiver(post_save, sender=RoomMembers, dispatch_uid="create_chatroom")
def create_chatroom(sender, instance, **kwargs):
   members = RoomMembers.objects.filter(room=instance.room)
   for member in members: 
      chat = Chat()
      chat.name = 'alohaaaaa'
      chat.save()
      chatmember = ChatMembers()
      chatmember.chat = chat
      chatmember.user = instance.user
      chatmember.room = instance.room
      chatmember.save()
      otherchatmember = ChatMembers()
      otherchatmember.chat = chat
      otherchatmember.user = member.user
      otherchatmember.room = member.room
      otherchatmember.save()
     

  

         