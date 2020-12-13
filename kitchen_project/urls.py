from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('login_app.urls')),
    path('chat/', include('chat.urls')),
    path('api/', include('api.urls')),
    path('', include('kitchen_app.urls')),   
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
