from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('login_app.urls')),
    path('', include('kitchen_app.urls')),
]
