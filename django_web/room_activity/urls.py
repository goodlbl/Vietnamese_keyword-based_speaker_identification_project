from django.urls import path
from . import views

app_name = 'room_activity'

urlpatterns = [
    path('history/<int:room_id>/', views.room_history, name='history_view'),
]