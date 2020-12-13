from django.urls import path
from . import views


urlpatterns = [
    path('id/<int:id>/', views.getImage.as_view()),
]