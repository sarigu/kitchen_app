from django.shortcuts import render, get_object_or_404, reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required
def index(request):
    return  render(request, 'kitchen_app/index.html')

