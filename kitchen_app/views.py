from django.shortcuts import render, get_object_or_404, reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from .models import User, Room, RoomForm, RoomMembers, Tasks, Subtasks, Events, Posts, Comments, Likes, UserProfile
from datetime import date
from isoweek import Week
from django.db import IntegrityError
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.http import HttpResponseRedirect

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
    members = RoomMembers.objects.filter(room=room_id)
    unassignedTasks = Tasks.objects.filter(room=room_id).exclude(user__isnull=False)
    assignedTasks = Tasks.objects.filter(room=room_id).filter(user=request.user).filter(status=False)
    events = Events.objects.filter(room=room_id)
    posts = Posts.objects.filter(room=room_id)
    comments = Comments.objects.filter(room=room_id)

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

    if request.method == 'POST' and 'addPostBtn' in request.POST:
        postText = request.POST['post']
        Posts.create(postText, request.user, room)

    if request.method == 'POST' and 'commentBtn' in request.POST:
        text = request.POST['comment']
        postID = request.POST['postID']
        parentPost = get_object_or_404(Posts, pk=postID)
        Comments.create(text, request.user, parentPost, room )

    if request.method == 'POST' and 'likeBtn' in request.POST:
        postID = request.POST['postID']
        post = get_object_or_404(Posts, pk=postID)
        likes = post.likes.all()
        if likes.filter(user=request.user).exists() == False:
            content_type = ContentType.objects.get_for_model(Posts)
            Likes.create(request.user, room, "post", content_type, postID)
    
    if request.method == 'POST' and 'commentLikeBtn' in request.POST:
        commentID = request.POST['commentID']
        comment = get_object_or_404(Comments, pk=commentID)
        likes = comment.likes.all()
        if likes.filter(user=request.user).exists() == False:
            content_type = ContentType.objects.get_for_model(Comments)
            Likes.create(request.user, room, "comment", content_type, commentID)
      
    postLikes = []
    commentLikes = []

    for elem in posts:
        post = get_object_or_404(Posts, pk=elem.pk)
        likes = post.likes.all()
        postLike = {'numberOfLikes' : len(likes), 'post': post }
        postLikes.append(postLike)
    

    for elem in comments:
        comment = get_object_or_404(Comments, pk=elem.pk)
        likes = comment.likes.all()
        commentLike = {'numberOfLikes' : len(likes), 'comment': comment }
        commentLikes.append(commentLike)


    context = {
        'room': room,
        'user': request.user, 
        'assignedTasks': assignedTasks, 
        'unassignedTasks': unassignedTasks, 
        'events': events,
        'posts': posts,
        'comments': comments,
        'postLikes': postLikes,
        'commentLikes': commentLikes,
        'members': members, 
    }
 
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
        member = get_object_or_404(RoomMembers.objects.filter(room=room_id), user=memberID)
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
        member = get_object_or_404(RoomMembers.objects.filter(room=room_id), user=memberID)
        member.delete()
    
    members = RoomMembers.objects.filter(room=room_id)
    context['members'] = members


    return render(request, 'kitchen_app/members.html', context)

@login_required
def profile(request, room_id):
    userDetails = get_object_or_404(UserProfile, user=request.user)
    room = get_object_or_404(Room, pk=room_id)
    members = RoomMembers.objects.filter(room=room_id)
    context = { 
        'user': request.user,
        'user_details': userDetails,
        'room': room,
        'members': members,
    }
    return render(request, 'kitchen_app/profile.html', context)

@login_required
def kitchen_fund(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    tasks = Tasks.objects.filter(room=room_id).filter(type="kitchen")
    members = RoomMembers.objects.filter(room=room_id)
    
    context = {
        'user': request.user,   
        'room': room,
        'tasks': tasks,
        'members': members,
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
        subtaskID = request.POST['taskID']
        subtask = get_object_or_404(Subtasks, pk=subtaskID)
        subtask.toggle_status()
        if Subtasks.objects.filter(task=task.pk).count() == Subtasks.objects.filter(status=True).count():
            messages.success(request, 'Your done')
 

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

@login_required
def completed_task(request, room_id):
    room = get_object_or_404(Room, pk=room_id)

    if request.method == 'POST':
        taskID = request.POST['taskID']
        task = get_object_or_404(Tasks, pk=taskID)
        task.delete()

    completedTasks = Tasks.objects.filter(room=room_id).filter(user=request.user).filter(status=True)
    
    context={  
        'room': room,   
        'completedTasks': completedTasks, 
    }
    return render(request, 'kitchen_app/completed_tasks.html', context)