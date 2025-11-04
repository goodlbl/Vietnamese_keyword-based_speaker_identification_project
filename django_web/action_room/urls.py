from django.urls import path
from . import views
 
app_name = "action_room"

urlpatterns = [
    path("<int:room_id>/", views.action_room_view, name="action_room_view"),
    path("verify_voice/", views.verify_voice, name="verify_voice"),
]
