from django.urls import path
from . import views

app_name = 'check_password'

urlpatterns = [
    path('', views.check_password_view, name='check_password'),
]
