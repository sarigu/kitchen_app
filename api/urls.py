from django.urls import path
from . import views


urlpatterns = [
    path('images/', views.images.as_view()),
    path('id/<int:id>/', views.get_image.as_view()), 
]