from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('toggle/<int:idx>/', views.toggle_button, name='toggle_button'),
]
