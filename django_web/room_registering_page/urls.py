from django.urls import path
from . import views

app_name = 'room_registering_page' 

urlpatterns = [
    path('create_owner_and_room/', views.create_owner_and_room, name='create_owner_and_room'),
]
