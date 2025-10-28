from django.urls import path
from . import views
app_name = 'room_registering_page' 

urlpatterns = [
    path('create_owner/', views.create_owner, name='create_owner'),
    path('create_room/<int:owner_id>/', views.create_room, name='create_room'),
]
 