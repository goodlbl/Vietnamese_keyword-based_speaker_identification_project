from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('submit_all/', views.submit_all, name='submit_all'),
]
