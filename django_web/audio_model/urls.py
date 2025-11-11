# audio_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # 1. Đường dẫn gốc của ứng dụng (Hiển thị Form) -> GET
    path('', views.upload_form_view, name='upload_form'), 
    
    # 2. Đường dẫn API (Xử lý POST request) -> POST
    path('extract/', views.extract_embedding_api, name='extract_embedding_api'),
]