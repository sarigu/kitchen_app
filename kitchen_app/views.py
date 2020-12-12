from django.shortcuts import render, get_object_or_404, reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from .models import User, Room, RoomForm, RoomMembers, Tasks, Subtasks, Events, Posts, Comments, Likes, UserProfile, Rules
from datetime import date
from isoweek import Week
from django.db import IntegrityError
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.http import HttpResponseRedirect
from .utils import is_room_admin


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


def create_room(request):
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            newRoom = form.save()
            if(newRoom):
                RoomMembers.create(request.user, newRoom, "admin")
                
    return HttpResponseRedirect(reverse('kitchen_app:index'))


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
        return HttpResponseRedirect(reverse('kitchen_app:enter_room', args=(room.id,)))

    if request.method == 'POST' and 'addTaskBtn' in request.POST:
        newTask = request.POST['task']
        Tasks.create(None, room, newTask, "anything", None)
        return HttpResponseRedirect(reverse('kitchen_app:enter_room', args=(room.id,)))

    if request.method == 'POST' and 'doneBtn' in request.POST:
        taskID = request.POST['taskID']
        task = get_object_or_404(Tasks, pk=taskID)
        task.status = True
        task.save()
        return HttpResponseRedirect(reverse('kitchen_app:enter_room', args=(room.id,)))

    if request.method == 'POST' and 'removeBtn' in request.POST:
        taskID = request.POST['taskID']
        task = get_object_or_404(Tasks, pk=taskID)
        task.delete()
        return HttpResponseRedirect(reverse('kitchen_app:enter_room', args=(room.id,)))

    if request.method == 'POST' and 'addPostBtn' in request.POST:
        postText = request.POST['post']
        Posts.create(postText, request.user, room)
        return HttpResponseRedirect(reverse('kitchen_app:enter_room', args=(room.id,)))

    if request.method == 'POST' and 'commentBtn' in request.POST:
        text = request.POST['comment']
        postID = request.POST['postID']
        parentPost = get_object_or_404(Posts, pk=postID)
        Comments.create(text, request.user, parentPost, room )
        return HttpResponseRedirect(reverse('kitchen_app:enter_room', args=(room.id,)))

    if request.method == 'POST' and 'likeBtn' in request.POST:
        postID = request.POST['postID']
        post = get_object_or_404(Posts, pk=postID)
        likes = post.likes.all()
        if likes.filter(user=request.user).exists() == False:
            content_type = ContentType.objects.get_for_model(Posts)
            Likes.create(request.user, room, "post", content_type, postID)
        else: 
            likes = Likes.objects.filter(user=request.user).filter(object_id=postID)
            for like in likes:
                like.toggle_active()
        return HttpResponseRedirect(reverse('kitchen_app:enter_room', args=(room.id,)))
               

    if request.method == 'POST' and 'removePostBtn' in request.POST:
        postID = request.POST['postID']
        post = get_object_or_404(Posts, pk=postID)
        if post.user == request.user:
            post.delete()
        return HttpResponseRedirect(reverse('kitchen_app:enter_room', args=(room.id,)))

    if request.method == 'POST' and 'removeCommentBtn' in request.POST:
        commentID = request.POST['commentID']
        comment = get_object_or_404(Comments, pk=commentID)
        if comment.user == request.user:
            comment.delete()
        return HttpResponseRedirect(reverse('kitchen_app:enter_room', args=(room.id,)))
    
    
    if request.method == 'POST' and 'commentLikeBtn' in request.POST:
        commentID = request.POST['commentID']
        comment = get_object_or_404(Comments, pk=commentID)
        likes = comment.likes.all()
        if likes.filter(user=request.user).exists() == False:
            content_type = ContentType.objects.get_for_model(Comments)
            Likes.create(request.user, room, "comment", content_type, commentID)
        else: 
            likes = Likes.objects.filter(user=request.user).filter(object_id=commentID)
            for like in likes:
                like.toggle_active()
        return HttpResponseRedirect(reverse('kitchen_app:enter_room', args=(room.id,)))
               
      
    postLikes = []
    commentLikes = []

    for elem in posts:
        post = get_object_or_404(Posts, pk=elem.pk)
        likes = post.likes.all().filter(active=True)
        postLike = {'numberOfLikes' : len(likes), 'post': post }
        postLikes.append(postLike)
    

    for elem in comments:
        comment = get_object_or_404(Comments, pk=elem.pk)
        likes = comment.likes.all().filter(active=True)
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

def members(request, room_id):
    members = RoomMembers.objects.filter(room=room_id)
    room = get_object_or_404(Room, pk=room_id)

    context = {
        'user': request.user,   
        'members': members,
        'room': room
    }

    return render(request, 'kitchen_app/members.html', context)


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


def edit_profile(request, room_id):
    user = get_object_or_404(User, pk=request.user.pk)
    userDetails = get_object_or_404(UserProfile, user=request.user)
    room = get_object_or_404(Room, pk=room_id)
    members = RoomMembers.objects.filter(room=room_id)

    context = { 
        'user': request.user,
        'user_details': userDetails,
        'room': room,
        'members': members,
    }


    if request.method == 'POST':
        user.username = request.POST['username']
        user.email = request.POST['email']
        user.first_name = request.POST['first_name']
        user.last_name = request.POST['last_name']
        user.save()
        if request.POST['phone']: 
            userDetails.phone = request.POST['phone']
            userDetails.save()
            
        return HttpResponseRedirect(reverse('kitchen_app:profile', args=(room.id,)))
   
    return render(request, 'kitchen_app/edit-profile.html', context)


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
        return HttpResponseRedirect(reverse('kitchen_app:kitchen_fund', args=(room.id,)))

    return render(request, 'kitchen_app/kitchen_fund.html', context)


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
        if Subtasks.objects.filter(task=task.pk).count() == Subtasks.objects.filter(task=task.pk).filter(status=True).count():
            messages.success(request, 'Your done')
        return HttpResponseRedirect(reverse('kitchen_app:weekly_cleaning', args=(room.id,)))

    return render(request, 'kitchen_app/weekly_cleaning.html', context)


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
          
    return render(request, 'kitchen_app/cleaning_schedule.html', context)


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
        return HttpResponseRedirect(reverse('kitchen_app:create_event', args=(room.id,)))

    return render(request, 'kitchen_app/dashboard.html', context)


def event(request, room_id, event_id):
    room = get_object_or_404(Room, pk=room_id)
    event = get_object_or_404(Events, pk=event_id)
    context={  
        'user': request.user,   
        'room': room,
        'event': event,
    }
    return render(request, 'kitchen_app/event_details.html', context)


def rules(request, room_id):
    members = RoomMembers.objects.filter(room=room_id)
    room = get_object_or_404(Room, pk=room_id)
    rules = get_object_or_404(Rules, room=room)
    context={  
        'user': request.user,   
        'room': room,
        'rules': rules,
        'members': members,
    }
    return render(request, 'kitchen_app/rules.html', context)


def completed_task(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    members = RoomMembers.objects.filter(room=room_id)

    if request.method == 'POST':
        taskID = request.POST['taskID']
        task = get_object_or_404(Tasks, pk=taskID)
        task.delete()
        return HttpResponseRedirect(reverse('kitchen_app:completed_task', args=(room.id,)))

    completedTasks = Tasks.objects.filter(room=room_id).filter(user=request.user).filter(status=True)
    
    context={  
        'room': room,   
        'completedTasks': completedTasks, 
        'members': members,
    }
    return render(request, 'kitchen_app/completed_tasks.html', context)

#####  admin edit mode

def admin_view(request, room_id):
    assert is_room_admin(request.user, room_id), 'Member routed to member view.'
    room = get_object_or_404(Room, pk=room_id)
    members = RoomMembers.objects.filter(room=room_id)
    unassignedTasks = Tasks.objects.filter(room=room_id).exclude(user__isnull=False)
    assignedTasks = Tasks.objects.filter(room=room_id).filter(status=False).exclude(user__isnull=True)
    events = Events.objects.filter(room=room_id)
    posts = Posts.objects.filter(room=room_id)
    comments = Comments.objects.filter(room=room_id)
   
    if request.method == 'POST' and 'assignTaskBtn' in request.POST:
        assignedUser = request.POST['members_choice']
        taskID = request.POST['taskID']
        task = get_object_or_404(Tasks, pk=taskID) 
        user = get_object_or_404(User, username=assignedUser) 
        task.setUser(user) 
        return HttpResponseRedirect(reverse('kitchen_app:admin_view', args=(room.id,)))

    if request.method == 'POST' and 'addTaskBtn' in request.POST:
        newTask = request.POST['task']
        Tasks.create(None, room, newTask, "anything", None)
        return HttpResponseRedirect(reverse('kitchen_app:admin_view', args=(room.id,)))

    if request.method == 'POST' and 'removeBtn' in request.POST:
        taskID = request.POST['taskID']
        task = get_object_or_404(Tasks, pk=taskID)
        task.delete()
        return HttpResponseRedirect(reverse('kitchen_app:admin_view', args=(room.id,)))

    if request.method == 'POST' and 'addPostBtn' in request.POST:
        postText = request.POST['post']
        Posts.create(postText, request.user, room)
        return HttpResponseRedirect(reverse('kitchen_app:admin_view', args=(room.id,)))

    if request.method == 'POST' and 'commentBtn' in request.POST:
        text = request.POST['comment']
        postID = request.POST['postID']
        parentPost = get_object_or_404(Posts, pk=postID)
        Comments.create(text, request.user, parentPost, room )
        return HttpResponseRedirect(reverse('kitchen_app:admin_view', args=(room.id,)))

    if request.method == 'POST' and 'likeBtn' in request.POST:
        postID = request.POST['postID']
        post = get_object_or_404(Posts, pk=postID)
        likes = post.likes.all()
        if likes.filter(user=request.user).exists() == False:
            content_type = ContentType.objects.get_for_model(Posts)
            Likes.create(request.user, room, "post", content_type, postID)
        else: 
            likes = Likes.objects.filter(user=request.user).filter(object_id=postID)
            for like in likes:
                like.toggle_active()
        return HttpResponseRedirect(reverse('kitchen_app:admin_view', args=(room.id,)))
               

    if request.method == 'POST' and 'removePostBtn' in request.POST:
        postID = request.POST['postID']
        post = get_object_or_404(Posts, pk=postID)
        if post.user == request.user:
            post.delete()
        return HttpResponseRedirect(reverse('kitchen_app:admin_view', args=(room.id,)))

    if request.method == 'POST' and 'removeCommentBtn' in request.POST:
        commentID = request.POST['commentID']
        comment = get_object_or_404(Comments, pk=commentID)
        if comment.user == request.user:
            comment.delete()
        return HttpResponseRedirect(reverse('kitchen_app:admin_view', args=(room.id,)))
    
    
    if request.method == 'POST' and 'commentLikeBtn' in request.POST:
        commentID = request.POST['commentID']
        comment = get_object_or_404(Comments, pk=commentID)
        likes = comment.likes.all()
        if likes.filter(user=request.user).exists() == False:
            content_type = ContentType.objects.get_for_model(Comments)
            Likes.create(request.user, room, "comment", content_type, commentID)
        else: 
            likes = Likes.objects.filter(user=request.user).filter(object_id=commentID)
            for like in likes:
                like.toggle_active()
        return HttpResponseRedirect(reverse('kitchen_app:admin_view', args=(room.id,)))
               
      
    postLikes = []
    commentLikes = []

    for elem in posts:
        post = get_object_or_404(Posts, pk=elem.pk)
        likes = post.likes.all().filter(active=True)
        postLike = {'numberOfLikes' : len(likes), 'post': post }
        postLikes.append(postLike)
    

    for elem in comments:
        comment = get_object_or_404(Comments, pk=elem.pk)
        likes = comment.likes.all().filter(active=True)
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
 
    return render(request, 'kitchen_app/admin_dashboard.html', context)
   
def delete_event(request, room_id):
    assert is_room_admin(request.user, room_id), 'Member routed to member view.'
    room = get_object_or_404(Room, pk=room_id)
    if request.method == 'POST':
        eventID = request.POST['eventID']
        event = get_object_or_404(Events, pk=eventID)
        event.delete()
    return HttpResponseRedirect(reverse('kitchen_app:admin_view', args=(room.id,)))

def admin_completed_tasks(request, room_id):
    assert is_room_admin(request.user, room_id), 'Member routed to member view.'
    room = get_object_or_404(Room, pk=room_id)
    completedTasks = Tasks.objects.filter(room=room_id).filter(status=True)
    context={  
        'room': room,   
        'completedTasks': completedTasks, 
    }
    return render(request, 'kitchen_app/admin_completed_tasks.html', context)

def admin_members(request, room_id):
    assert is_room_admin(request.user, room_id), 'Member routed to member view.'
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
        return HttpResponseRedirect(reverse('kitchen_app:admin_members', args=(room.id,)))

    if request.method == 'POST' and 'makeMemberBtn' in request.POST:
        memberID = request.POST['memberID']
        member = get_object_or_404(RoomMembers.objects.filter(room=room_id), user=memberID)
        member.status = "member"
        member.save()
        return HttpResponseRedirect(reverse('kitchen_app:admin_members', args=(room.id,)))

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
        return HttpResponseRedirect(reverse('kitchen_app:admin_members', args=(room.id,)))

    if request.method == 'POST' and 'removeBtn' in request.POST:
        memberID = request.POST['memberID']
        member = get_object_or_404(RoomMembers.objects.filter(room=room_id), user=memberID)
        member.delete()
        return HttpResponseRedirect(reverse('kitchen_app:admin_members', args=(room.id,)))
    

    return render(request, 'kitchen_app/admin_members.html', context)

def admin_schedule(request, room_id):
    assert is_room_admin(request.user, room_id), 'Member routed to member view.'
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
  
    if request.method == 'POST' and 'addBtn' in request.POST:
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
                return HttpResponseRedirect(reverse('kitchen_app:admin_schedule', args=(room.id,)))
        except IntegrityError as e:
            context['error'] = "Week is taken"

    if request.method == 'POST' and 'removeBtn' in request.POST:
        takenWeekID = request.POST['takenWeekID']
        task =  get_object_or_404(Tasks, pk=takenWeekID)
        task.delete()
        return HttpResponseRedirect(reverse('kitchen_app:admin_schedule', args=(room.id,)))
                        
    return render(request, 'kitchen_app/admin_cleaning_schedule.html', context)
