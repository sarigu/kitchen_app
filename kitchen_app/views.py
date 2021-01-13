from django.shortcuts import render, get_object_or_404, reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from .models import User, Room, RoomForm, RoomMembers, Tasks, Subtasks, Events, Posts, Comments, Likes, UserProfile, Rules, ListTasks, List, Chat, ChatMembers
from datetime import datetime
import datetime
from isoweek import Week
from django.db import IntegrityError
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from .utils import is_room_admin
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def index(request):
    #get all rooms the user is member of
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
    unassignedTasks = Tasks.objects.filter(room=room_id).filter(status=False).exclude(user__isnull=False)
    assignedTasks = Tasks.objects.filter(room=room_id).filter(user=request.user).filter(status=False)
    events = Events.objects.filter(room=room_id)
    posts = Posts.objects.filter(room=room_id)
    comments = Comments.objects.filter(room=room_id)

    # set user for a chosen task
    if request.method == 'POST' and 'takeTaskBtn' in request.POST:
        taskID = request.POST['taskID']
        task = get_object_or_404(Tasks, pk=taskID)
        task.setUser(request.user)
        return HttpResponseRedirect(reverse('kitchen_app:enter_room', args=(room.id,)))

    # create new task
    if request.method == 'POST' and 'addTaskBtn' in request.POST:
        newTask = request.POST['task']
        Tasks.create(None, room, newTask, "anything", None)
        return HttpResponseRedirect(reverse('kitchen_app:enter_room', args=(room.id,)))

    # set task status to true/mark as done
    if request.method == 'POST' and 'doneBtn' in request.POST:
        taskID = request.POST['taskID']
        task = get_object_or_404(Tasks, pk=taskID)
        task.status = True
        task.save()
        return HttpResponseRedirect(reverse('kitchen_app:enter_room', args=(room.id,)))

    # delete a task
    if request.method == 'POST' and 'removeBtn' in request.POST:
        taskID = request.POST['taskID']
        task = get_object_or_404(Tasks, pk=taskID)
        task.delete()
        return HttpResponseRedirect(reverse('kitchen_app:enter_room', args=(room.id,)))

    # create a post
    if request.method == 'POST' and 'addPostBtn' in request.POST:
        postText = request.POST['post']
        Posts.create(postText, request.user, room)
        return HttpResponseRedirect(reverse('kitchen_app:enter_room', args=(room.id,)))

    # create a comment for a certain post
    if request.method == 'POST' and 'commentBtn' in request.POST:
        text = request.POST['comment']
        postID = request.POST['postID']
        parentPost = get_object_or_404(Posts, pk=postID)
        Comments.create(text, request.user, parentPost, room )
        return HttpResponseRedirect(reverse('kitchen_app:enter_room', args=(room.id,)))

    # create a like if doesn't exit for user, else toggle like
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
               
    # delete post if user is author
    if request.method == 'POST' and 'removePostBtn' in request.POST:
        postID = request.POST['postID']
        post = get_object_or_404(Posts, pk=postID)
        if post.user == request.user:
            post.delete()
        return HttpResponseRedirect(reverse('kitchen_app:enter_room', args=(room.id,)))

    # remove comment if user is author
    if request.method == 'POST' and 'removeCommentBtn' in request.POST:
        commentID = request.POST['commentID']
        comment = get_object_or_404(Comments, pk=commentID)
        if comment.user == request.user:
            comment.delete()
        return HttpResponseRedirect(reverse('kitchen_app:enter_room', args=(room.id,)))
    
    # create a like for a comment
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
               
    # get number of active likes for posts and comments
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

    if request.method == 'POST':
        #get clicked on person
        chatToID = request.POST['chatToID']
        chatToUser = get_object_or_404(User, pk=chatToID)
        # check if clicked on person is not user
        if chatToUser != request.user:
            chatFrom = ChatMembers.objects.filter(room=room).filter(user = request.user)
            #check if user has a chat with the user he wants to chat with
            for chat in chatFrom:
                checkForChat = ChatMembers.objects.filter(room=room).filter(user = chatToUser).filter(chat=chat.chat.pk).exists()
                if checkForChat:
                    chatID = chat.chat.pk
                    chatroom = get_object_or_404(Chat, pk=chatID)
                    chaturl = chatroom.name
                    chatExists = True
                    return HttpResponseRedirect(reverse('chat:chatroom' ,args=( chaturl,)))

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

    # overwrite profile information
    if request.method == 'POST':
        user.username = request.POST['username']
        user.email = request.POST['email']
        user.first_name = request.POST['first_name']
        user.last_name = request.POST['last_name']
        user.save()
        #change phone number in user profile
        if request.POST['phone']: 
            userDetails.phone = request.POST['phone']
            userDetails.save()
            
        return HttpResponseRedirect(reverse('kitchen_app:profile', args=(room.id,)))
   
    return render(request, 'kitchen_app/edit-profile.html', context)


def kitchen_fund(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    tasks = Tasks.objects.filter(room=room_id).filter(type="kitchen").filter(status=False)
    members = RoomMembers.objects.filter(room=room_id)
    requestedPayments = Tasks.objects.filter(room=room_id).filter(type="payback").filter(status=False)
    donePayments = Tasks.objects.filter(room=room_id).filter(type="payback").filter(status=True)
    
    context = {
        'user': request.user,   
        'room': room,
        'tasks': tasks,
        'members': members,
        'requestedPayments': requestedPayments,
        'donePayments': donePayments,
    }

    # create task for items to purchase
    if request.method == 'POST' and 'addBtn' in request.POST:
        newTask = request.POST['task']
        Tasks.create(None, room, newTask, "kitchen", None)
        return HttpResponseRedirect(reverse('kitchen_app:kitchen_fund', args=(room.id,)))
    
    # create a task for money back request
    if request.method == 'POST' and 'requestBtn' in request.POST:
        amount = request.POST['amount']
        purchase = request.POST['purchase'] 
        text = amount + 'DKK for ' + purchase + ' to ' + str(request.user)
        Tasks.create(None, room, text, "payback", None)
   
        return HttpResponseRedirect(reverse('kitchen_app:kitchen_fund', args=(room.id,)))

    return render(request, 'kitchen_app/kitchen_fund.html', context)


def weekly_cleaning(request, room_id):
    room = get_object_or_404(Room, pk=room_id)

    #get task and its subtasks
    queryset = Tasks.objects.filter(room=room_id).filter(user=request.user).filter(type="clean")
    for elem in queryset:
        task = get_object_or_404(Tasks, pk=elem.pk)
    subtasks = Subtasks.objects.filter(task=task.pk)

    context={  
        'user': request.user,   
        'room': room,
        'subtasks': subtasks
    }

    # mark a weekly cleaning task as done
    if request.method == 'POST':
        subtaskID = request.POST['taskID']
        subtask = get_object_or_404(Subtasks, pk=subtaskID)
        subtask.toggle_status()
        #check if all subtasks are marked as done
        if Subtasks.objects.filter(task=task.pk).count() == Subtasks.objects.filter(task=task.pk).filter(status=True).count():
            messages.success(request, 'Your done')
        return HttpResponseRedirect(reverse('kitchen_app:weekly_cleaning', args=(room.id,)))

    return render(request, 'kitchen_app/weekly_cleaning.html', context)


def schedule(request, room_id):
    room = get_object_or_404(Room, pk=room_id)  
    members = RoomMembers.objects.filter(room=room_id) 
    takenWeeks = Tasks.objects.filter(room=room_id).filter(type="clean").filter(task="weekly cleaning")
    #get all weeks of the year (year hardcoded)
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

    #create event
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        startDate= request.POST['start']
        endDate = request.POST['end']
        type = request.POST['type']

        Events.create(title, description, room, type, startDate, endDate)
        return HttpResponseRedirect(reverse('kitchen_app:create_event', args=(room.id,)))

    return render(request, 'kitchen_app/dashboard.html', context)


#get event
def event(request, room_id, event_id):
    room = get_object_or_404(Room, pk=room_id)
    event = get_object_or_404(Events, pk=event_id)
    context={  
        'user': request.user,   
        'room': room,
        'event': event,
    }
    return render(request, 'kitchen_app/event_details.html', context)


#get rules
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

    #remove completed task
    if request.method == 'POST':
        taskID = request.POST['taskID']
        task = get_object_or_404(Tasks, pk=taskID)
        task.delete()
        return HttpResponseRedirect(reverse('kitchen_app:completed_task', args=(room.id,)))

    #get all completed tasks
    completedTasks = Tasks.objects.filter(room=room_id).filter(user=request.user).filter(status=True)
    
    context={  
        'room': room,   
        'completedTasks': completedTasks, 
        'members': members,
    }
    return render(request, 'kitchen_app/completed_tasks.html', context)


def enter_chat(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    return HttpResponseRedirect(reverse('kitchen_app:members', args=(room.id,)))


def leave_room(request, room_id):
        room = get_object_or_404(Room, pk=room_id)
        member = get_object_or_404(RoomMembers.objects.filter(room=room_id), user=request.user)
        if(member):
            member.delete()
        return HttpResponseRedirect(reverse('kitchen_app:index'))



#####  ADMIN EDIT MODE FUNCTIONS #######

def admin_view(request, room_id):
    #make sure it is an admin
    assert is_room_admin(request.user, room_id), 'Member routed to member view.'

    room = get_object_or_404(Room, pk=room_id)
    members = RoomMembers.objects.filter(room=room_id)
    unassignedTasks = Tasks.objects.filter(room=room_id).filter(status=False).exclude(user__isnull=False)
    assignedTasks = Tasks.objects.filter(room=room_id).filter(status=False).exclude(user__isnull=True)
    events = Events.objects.filter(room=room_id)
    posts = Posts.objects.filter(room=room_id)
    comments = Comments.objects.filter(room=room_id)
   
   # assign a task to a selected room member
    if request.method == 'POST' and 'assignTaskBtn' in request.POST:
        assignedUser = request.POST['members_choice']
        taskID = request.POST['taskID']
        task = get_object_or_404(Tasks, pk=taskID) 
        user = get_object_or_404(User, username=assignedUser) 
        task.setUser(user) 

        # send a notification to assigned user
        channel_layer = get_channel_layer()
        data = "Hi. You got a new task: " + task.task
        async_to_sync(channel_layer.group_send)(
            str(user.pk),  
            {
                "type": "notify",   
                "message": data,
            },
        )  
        return HttpResponseRedirect(reverse('kitchen_app:admin_view', args=(room.id,)))

    # add a task
    if request.method == 'POST' and 'addTaskBtn' in request.POST:
        newTask = request.POST['task']
        Tasks.create(None, room, newTask, "anything", None)
        return HttpResponseRedirect(reverse('kitchen_app:admin_view', args=(room.id,)))

    # remove a task
    if request.method == 'POST' and 'removeBtn' in request.POST:
        taskID = request.POST['taskID']
        task = get_object_or_404(Tasks, pk=taskID)
        task.delete()
        return HttpResponseRedirect(reverse('kitchen_app:admin_view', args=(room.id,)))

    # add a post
    if request.method == 'POST' and 'addPostBtn' in request.POST:
        postText = request.POST['post']
        Posts.create(postText, request.user, room)
        return HttpResponseRedirect(reverse('kitchen_app:admin_view', args=(room.id,)))

    # add a comment for a post
    if request.method == 'POST' and 'commentBtn' in request.POST:
        text = request.POST['comment']
        postID = request.POST['postID']
        parentPost = get_object_or_404(Posts, pk=postID)
        Comments.create(text, request.user, parentPost, room )
        return HttpResponseRedirect(reverse('kitchen_app:admin_view', args=(room.id,)))

    # create or toggle a like for a post
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
               
    # remove a post
    if request.method == 'POST' and 'removePostBtn' in request.POST:
        postID = request.POST['postID']
        post = get_object_or_404(Posts, pk=postID)
        if post.user == request.user:
            post.delete()
        return HttpResponseRedirect(reverse('kitchen_app:admin_view', args=(room.id,)))

    # remove a comment
    if request.method == 'POST' and 'removeCommentBtn' in request.POST:
        commentID = request.POST['commentID']
        comment = get_object_or_404(Comments, pk=commentID)
        if comment.user == request.user:
            comment.delete()
        return HttpResponseRedirect(reverse('kitchen_app:admin_view', args=(room.id,)))
    
    # create or toggle a like for a comment
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

    # switch user status from member to admin
    if request.method == 'POST' and 'updateBtn' in request.POST:
        memberID = request.POST['memberID']
        member = get_object_or_404(RoomMembers.objects.filter(room=room_id), user=memberID)
        member.status = "admin"
        member.save()
        return HttpResponseRedirect(reverse('kitchen_app:admin_members', args=(room.id,)))

    # switch user status from admin to member
    if request.method == 'POST' and 'makeMemberBtn' in request.POST:
        memberID = request.POST['memberID']
        member = get_object_or_404(RoomMembers.objects.filter(room=room_id), user=memberID)
        member.status = "member"
        member.save()
        return HttpResponseRedirect(reverse('kitchen_app:admin_members', args=(room.id,)))

    # look for a person (who is not part of the group already)
    if request.method == 'POST' and 'searchBtn' in request.POST:
        name = request.POST['name']
        members = RoomMembers.objects.filter(room=room_id).values_list('user', flat=True)
        users = User.objects.filter(username__icontains=name).exclude(id__in = members)

        context['search_term'] = name
        context['users'] = users

    # add person to room (as a member)
    if request.method == 'POST' and 'addBtn' in request.POST:
        userID = request.POST['userID']
        user = get_object_or_404(User, pk=userID)
        if not RoomMembers.objects.filter(room=room).filter(user=user).exists():
            RoomMembers.create(user, room, "member")
        return HttpResponseRedirect(reverse('kitchen_app:admin_members', args=(room.id,)))

    # remove a member from the room
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

    # get all weeks that have cleaning schedule
    takenWeeks = Tasks.objects.filter(room=room_id).filter(type="clean").filter(task="weekly cleaning")

    #get all weeks of the year
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
  
    # assign a week to a room member for cleaning
    if request.method == 'POST' and 'addBtn' in request.POST:
        try: 
            dueToWeek = Week.fromstring(request.POST['week'])
            if takenWeeks: 
                for takenWeek in takenWeeks:
                    if dueToWeek.isoformat() == takenWeek.deadline:
                        context['error'] = "Week is taken"
                        taken = True
               
            if taken == False:
                #create a task for the week of cleaning
                assignedUser = request.POST['members_choice']
                user = get_object_or_404(User, username=assignedUser)  
                Tasks.create(user, room, "weekly cleaning", "clean", dueToWeek)

                #create a list of subtasks
                queryset = Tasks.objects.filter(room=room_id)
                task = get_object_or_404(queryset, deadline=dueToWeek.isoformat())
                list = get_object_or_404(List, pk=1)
                listTasks = ListTasks.objects.filter(list=list)
                for listTask in listTasks:
                    Subtasks.create(task, listTask.task)
                return HttpResponseRedirect(reverse('kitchen_app:admin_schedule', args=(room.id,)))
        except IntegrityError as e:
            context['error'] = "Week is taken"

    # remove an assigned week
    if request.method == 'POST' and 'removeBtn' in request.POST:
        takenWeekID = request.POST['takenWeekID']
        task =  get_object_or_404(Tasks, pk=takenWeekID)
        task.delete()
        return HttpResponseRedirect(reverse('kitchen_app:admin_schedule', args=(room.id,)))
                        
    return render(request, 'kitchen_app/admin_cleaning_schedule.html', context)


def admin_rules(request, room_id):
    assert is_room_admin(request.user, room_id), 'Member routed to member view.'
    room = get_object_or_404(Room, pk=room_id)
    rules = get_object_or_404(Rules, room=room)
    context = {
        'room': room,
        'rules': rules,
    }
    return render(request, 'kitchen_app/admin_rules.html', context)


def edit_rules(request, room_id):
    assert is_room_admin(request.user, room_id), 'Member routed to member view.'
    room = get_object_or_404(Room, pk=room_id)
    rules = get_object_or_404(Rules, room=room)
    context={   
        'room': room,
        'rules': rules,
    }

    if request.method == 'POST':
        rules.text = request.POST['text']
        rules.updated_at = datetime.datetime.now()
        rules.save()   
        return HttpResponseRedirect(reverse('kitchen_app:admin_rules', args=(room.id,)))
   
    return render(request, 'kitchen_app/edit_rules.html', context)

#redirect to page with images
def view_images(request, room_id):
    assert is_room_admin(request.user, room_id), 'Member routed to member view.'
    room = get_object_or_404(Room, pk=room_id)
    context={ 'room': room,}
    return render(request, 'kitchen_app/image_choices.html', context)


def set_new_bg_image(request, room_id):
    assert is_room_admin(request.user, room_id), 'Member routed to member view.'
    room = get_object_or_404(Room, pk=room_id)

    #save chosen background image as new background image for room
    if request.method == 'POST':
        imageID= request.POST['imageID']
        room.backgroundImage = 'http://127.0.0.1:8000/api/id/' + imageID
        room.save()
    
    return HttpResponseRedirect(reverse('kitchen_app:admin_view', args=(room.id,)))
    

def admin_kitchen_fund(request, room_id):
    assert is_room_admin(request.user, room_id), 'Member routed to member view.'
    room = get_object_or_404(Room, pk=room_id)
    tasks = Tasks.objects.filter(room=room_id).filter(type="kitchen").filter(status=False)
    members = RoomMembers.objects.filter(room=room_id)
    requestedPayments = Tasks.objects.filter(room=room_id).filter(type="payback").filter(status=False)
    donePayments = Tasks.objects.filter(room=room_id).filter(type="payback").filter(status=True)
    
    context = {
        'user': request.user,   
        'room': room,
        'tasks': tasks,
        'members': members,
        'requestedPayments': requestedPayments,
        'donePayments': donePayments,
    }

    # update amount of kitchen fund
    if request.method == 'POST' and 'updateAmountBtn' in request.POST:
        amount = request.POST['amount']
        room.fund = amount
        room.save()
        return HttpResponseRedirect(reverse('kitchen_app:admin_kitchen_fund', args=(room.id,)))

    # update mobile pay box information
    if request.method == 'POST' and 'changeBoxBtn' in request.POST:
        newMobilePayBox = request.POST['mobilePayBox']
        room.mobilePayBox = newMobilePayBox
        room.save()
        return HttpResponseRedirect(reverse('kitchen_app:admin_kitchen_fund', args=(room.id,)))
    
    # remove item from buying list
    if request.method == 'POST' and 'removeBtn' in request.POST:
        taskID = request.POST['taskID']
        task = get_object_or_404(Tasks, pk=taskID)
        task.delete()
        return HttpResponseRedirect(reverse('kitchen_app:admin_kitchen_fund', args=(room.id,)))

    # mark money back request as done
    if request.method == 'POST' and 'doneBtn' in request.POST:
        taskID = request.POST['taskID']
        task = get_object_or_404(Tasks, pk=taskID)
        task.status = True
        task.save()
        return HttpResponseRedirect(reverse('kitchen_app:admin_kitchen_fund', args=(room.id,)))

    # add item to buying list
    if request.method == 'POST' and 'addBtn' in request.POST:
        newTask = request.POST['task']
        Tasks.create(None, room, newTask, "kitchen", None)
        return HttpResponseRedirect(reverse('kitchen_app:admin_kitchen_fund', args=(room.id,)))

    # remove item from reciept list
    if request.method == 'POST' and 'removeRecieptBtn' in request.POST:
        taskID = request.POST['taskID']
        task = get_object_or_404(Tasks, pk=taskID)
        task.delete()
        return HttpResponseRedirect(reverse('kitchen_app:admin_kitchen_fund', args=(room.id,)))

    return render(request, 'kitchen_app/admin_kitchen_fund.html', context)


def admin_cleaning_tasks(request, room_id):
    assert is_room_admin(request.user, room_id), 'Member routed to member view.'
    room = get_object_or_404(Room, pk=room_id)
    list = get_object_or_404(List, pk=1)
    listTasks = ListTasks.objects.filter(list=list)

    context={ 
        'room': room,
        'listTasks': listTasks,
    }

    # add task for weekly cleaning
    if request.method == 'POST' and 'addBtn' in request.POST:
        newTask = request.POST['listTask']
        ListTasks.create(list, newTask)
        return HttpResponseRedirect(reverse('kitchen_app:admin_cleaning_tasks', args=(room.id,)))

    # remove task for weekly cleaning 
    if request.method == 'POST' and 'removeBtn' in request.POST:
        listTaskID = request.POST['listTaskID']
        listTask = get_object_or_404(listTasks, pk=listTaskID)
        listTask.delete()
        return HttpResponseRedirect(reverse('kitchen_app:admin_cleaning_tasks', args=(room.id,)))

    return render(request, 'kitchen_app/admin_cleaning_tasks.html', context)


def admin_edit_room (request, room_id):
    assert is_room_admin(request.user, room_id), 'Member routed to member view.'

    room = get_object_or_404(Room, pk=room_id)
    context={ 
        'room': room,
    }

    # update room information
    if request.method == 'POST':
        room.name = request.POST['name']
        room.mobilePayBox = request.POST['mobilePayBox']
        room.fund = request.POST['fund']
        room.dorm = request.POST['dorm']
        room.save()
        return HttpResponseRedirect(reverse('kitchen_app:admin_edit_room', args=(room.id,)))

    return render(request, 'kitchen_app/admin_room_info.html', context)

