from django.urls import path
from . import views

app_name = 'check_password'

urlpatterns = [
    path('check_password/<int:room_id>/', views.check_password_view, name='check_password_view'),
]
