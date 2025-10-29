from django.urls import path
from . import views

app_name = 'main_page'

urlpatterns = [
    path('', views.home, name='home'),
    path('room/<str:room_id>/', views.room_detail, name='room_detail'),
]
