from django.contrib import admin
from django.urls import path

from . import views

app_name = 'login_app'

urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('sign_up/', views.sign_up, name='sign_up'),
    path('request_password_reset/', views.request_password_reset, name='request_password_reset'),
    path('set_new_password/', views.set_new_password, name='set_new_password'),
]