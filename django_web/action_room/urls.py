from django.urls import path
from . import views

urlpatterns = [
    path('<int:room_id>/', views.action_room_view, name='action_room_view'),
]
