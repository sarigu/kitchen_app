from django.shortcuts import render, get_object_or_404, reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from .models import User, Room, RoomForm, RoomMembers


# Create your views here.
@login_required
def index(request):
    rooms = []
    queryset = RoomMembers.objects.filter(userID=request.user).values_list('roomID', flat=True)
    for roomID in queryset:
        room = get_object_or_404(Room, pk=roomID)
        rooms.append(room)
    context={
        'rooms': rooms,
        'user': request.user,    
    }
    return render(request, 'kitchen_app/index.html', context)

@login_required
def create_room(request):
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            newRoom = form.save()
            if(newRoom):
                RoomMembers.create(request.user, newRoom, "admin")
             
    rooms = []
    queryset = RoomMembers.objects.filter(userID=request.user).values_list('roomID', flat=True)
    for roomID in queryset:
        room = get_object_or_404(Room, pk=roomID)
        rooms.append(room)
        
    context={
        'rooms': rooms,
        'user': request.user,    
    }
    return render(request, 'kitchen_app/index.html', context)

@login_required
def enter_room(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    context={
        'room': room,
        'user': request.user,    
    }
    return render(request, 'kitchen_app/dashboard.html', context)

@login_required
def members(request, room_id):
    members = RoomMembers.objects.filter(roomID=room_id)
    context = {
        'user': request.user,   
        'members': members,
        'room': room_id
    }

    if request.method == 'POST':
        print("hello")
        name = request.POST['name']
        print(name)
        users = User.objects.filter(username__icontains=name)
        print(users)
        context['search_term'] = name
        context['users'] = users

    return render(request, 'kitchen_app/members.html', context)

