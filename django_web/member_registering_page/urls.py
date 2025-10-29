from django.urls import path
from . import views

app_name = 'member_registering_page'  # cần có để dùng namespace

urlpatterns = [
    path('', views.register_view, name='register'),  # URL gốc của app
    path('submit_all/', views.submit_all, name='submit_all'),
]
