from django.shortcuts import render, get_object_or_404, reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from .models import User, Room, RoomForm, RoomMembers, Tasks

# Create your views here.
@login_required
def index(request):
    rooms = []
    queryset = RoomMembers.objects.filter(user=request.user).values_list('room', flat=True)
    for room in queryset:
        room = get_object_or_404(Room, pk=room)
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
    queryset = RoomMembers.objects.filter(user=request.user).values_list('room', flat=True)
    for room in queryset:
        room = get_object_or_404(Room, pk=room)
        rooms.append(room)
        
    context={
        'rooms': rooms,
        'user': request.user,    
    }
    return render(request, 'kitchen_app/index.html', context)

@login_required
def enter_room(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    unassignedTasks = Tasks.objects.filter(room=room_id).exclude(user__isnull=False)
    assignedTasks = Tasks.objects.filter(room=room_id).filter(user=request.user)
    context={
        'room': room,
        'user': request.user, 
        'assignedTasks': assignedTasks, 
        'unassignedTasks': unassignedTasks, 
    }

    if request.method == 'POST' and 'takeTaskBtn' in request.POST:
        taskID = request.POST['taskID']
        task = get_object_or_404(Tasks, pk=taskID)
        task.setUser(request.user)

    if request.method == 'POST' and 'addTaskBtn' in request.POST:
        newTask = request.POST['task']
        Tasks.create(room, newTask, "anything")

    if request.method == 'POST' and 'doneBtn' in request.POST:
        taskID = request.POST['taskID']
        task = get_object_or_404(Tasks, pk=taskID)
        task.delete()

    if request.method == 'POST' and 'removeBtn' in request.POST:
        taskID = request.POST['taskID']
        task = get_object_or_404(Tasks, pk=taskID)
        task.delete()
    return render(request, 'kitchen_app/dashboard.html', context)

@login_required
def members(request, room_id):
    members = RoomMembers.objects.filter(room=room_id)
    room = get_object_or_404(Room, pk=room_id)
    context = {
        'user': request.user,   
        'members': members,
        'room': room
    }

    if request.method == 'POST' and 'updateBtn' in request.POST:
        memberID = request.POST['memberID']
        member = get_object_or_404(RoomMembers, user=memberID)
        member.status = "admin"
        member.save()
    if request.method == 'POST' and 'searchBtn' in request.POST:
        name = request.POST['name']
        members = RoomMembers.objects.filter(room=room_id).values_list('user', flat=True)
        users = User.objects.filter(username__icontains=name).exclude(id__in = members)

        context['search_term'] = name
        context['users'] = users

    if request.method == 'POST' and 'addBtn' in request.POST:
        userID = request.POST['userID']
        user = get_object_or_404(User, pk=userID)
        RoomMembers.create(user, room, "member")

    if request.method == 'POST' and 'removeBtn' in request.POST:
        memberID = request.POST['memberID']
        queryset = RoomMembers.objects.filter(room=room_id)
        member = get_object_or_404(queryset, user=memberID)
        member.delete()
     

    return render(request, 'kitchen_app/members.html', context)

@login_required
def profile(request):
    context = { 
        'user': request.user
    }
    return render(request, 'kitchen_app/profile.html', context)

@login_required
def kitchen_fund(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    tasks = Tasks.objects.filter(room=room_id).filter(type="kitchen")
    
    context = {
        'user': request.user,   
        'room': room,
        'tasks': tasks,
    }

    if request.method == 'POST' and 'addBtn' in request.POST:
        newTask = request.POST['task']
        Tasks.create(room, newTask, "kitchen")
    return render(request, 'kitchen_app/kitchen_fund.html', context)