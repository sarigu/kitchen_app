from django.shortcuts import render, get_object_or_404, reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from .models import Room, RoomForm, RoomMembers


# Create your views here.
@login_required
def index(request):
    return render(request, 'kitchen_app/index.html')

@login_required
def create_room(request):
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            newRoom = form.save()
            if(newRoom):
                RoomMembers.create(request.user, newRoom, "admin")
    return render(request, 'kitchen_app/dashboard.html')