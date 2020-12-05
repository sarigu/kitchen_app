from django.shortcuts import render, get_object_or_404, reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from .models import User, Room, RoomForm, RoomMembers, Tasks, Subtasks, Events
import calendar
from django.utils.safestring import mark_safe
from datetime import date
from isoweek import Week
from django.db import IntegrityError


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
    events = Events.objects.filter(room=room_id)
    context={
        'room': room,
        'user': request.user, 
        'assignedTasks': assignedTasks, 
        'unassignedTasks': unassignedTasks, 
        'events': events,
    }

    if request.method == 'POST' and 'takeTaskBtn' in request.POST:
        taskID = request.POST['taskID']
        task = get_object_or_404(Tasks, pk=taskID)
        task.setUser(request.user)

    if request.method == 'POST' and 'addTaskBtn' in request.POST:
        newTask = request.POST['task']
        Tasks.create(None, room, newTask, "anything", None)

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
        Tasks.create(None, room, newTask, "kitchen", None)
    return render(request, 'kitchen_app/kitchen_fund.html', context)

@login_required
def weekly_cleaning(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    queryset = Tasks.objects.filter(room=room_id).filter(user=request.user).filter(type="clean")
    for elem in queryset:
        task = get_object_or_404(Tasks, pk=elem.pk)
    subtasks = Subtasks.objects.filter(task=task.pk)
    context={  
        'user': request.user,   
        'room': room,
        'subtasks': subtasks
    }

    if request.method == 'POST':
        taskID = request.POST['taskID']
        task = get_object_or_404(Subtasks, pk=taskID)
        task.toggle_status()
    return render(request, 'kitchen_app/weekly_cleaning.html', context)

@login_required
def schedule(request, room_id):
    room = get_object_or_404(Room, pk=room_id)  
    members = RoomMembers.objects.filter(room=room_id) 

    takenWeeks = Tasks.objects.filter(room=room_id).filter(type="clean").filter(task="weekly cleaning")

    weeks = []
    i = 1
    while i <= 52:
        w = Week(2020, i)
        week = {'week': w.isoformat(), 'weekStart': w.monday().isoformat(), 'weekEnd': w.sunday().isoformat(), 'deadline': None, 'user': None  }
        weeks.append(week)
        i += 1

    context={  
        'user': request.user,   
        'room': room,
        'members': members,
        'weeks': weeks,
        'takenWeeks': takenWeeks
    }

    taken = False
  
    if request.method == 'POST':
        try: 
            dueToWeek = Week.fromstring(request.POST['week'])
            if takenWeeks: 
                for takenWeek in takenWeeks:
                    if dueToWeek.isoformat() == takenWeek.deadline:
                        context['error'] = "Week is taken"
                        taken = True
               
            if taken == False:
                assignedUser = request.POST['members_choice']
                user = get_object_or_404(User, username=assignedUser)  
                Tasks.create(user, room, "weekly cleaning", "clean", dueToWeek)
                takenWeeks = Tasks.objects.filter(room=room_id).filter(type="clean").filter(task="weekly cleaning")
                context['takenWeeks'] = takenWeeks
        except IntegrityError as e:
            context['error'] = "Week is taken"
                        
    return render(request, 'kitchen_app/cleaning_schedule.html', context)

@login_required
def create_event(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    unassignedTasks = Tasks.objects.filter(room=room_id).exclude(user__isnull=False)
    assignedTasks = Tasks.objects.filter(room=room_id).filter(user=request.user)
    events = Events.objects.filter(room=room_id)
    context={
        'room': room,
        'user': request.user, 
        'assignedTasks': assignedTasks, 
        'unassignedTasks': unassignedTasks, 
        'events': events,
    }

    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        startDate= request.POST['start']
        endDate = request.POST['end']
        type = request.POST['type']

        Events.create(title, description, room, type, startDate, endDate)

    return render(request, 'kitchen_app/dashboard.html', context)

@login_required
def event(request, room_id, event_id):
    room = get_object_or_404(Room, pk=room_id)
    event = get_object_or_404(Events, pk=event_id)
    context={  
        'user': request.user,   
        'room': room,
        'event': event,
    }
    return render(request, 'kitchen_app/event_details.html', context)