from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main_page.urls', namespace='main_page')),
    path('member_registering_page/', include('member_registering_page.urls')),
    path('room_registering_page/', include('room_registering_page.urls')),
    path('check_password/', include('check_password.urls')),
    path('action_room/', include('action_room.urls')),
]
