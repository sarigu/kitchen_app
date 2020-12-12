from .models import RoomMembers
from django.shortcuts import get_object_or_404

def is_room_admin(user, room_id) -> bool:
    member = get_object_or_404(RoomMembers.objects.filter(room=room_id), user=user)
    return True if member.status == "admin" else False
