from django.urls import path
from . import views

app_name = 'member_registering_page'  

urlpatterns = [
    path('', views.register_view, name='register'), 
    path('submit_all/', views.submit_all, name='submit_all'),
    path('go_back/', views.back_to_password, name='go_back'),
]
