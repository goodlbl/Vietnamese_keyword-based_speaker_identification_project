# audio_app/views.py
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .utils import extract_embedding, GLOBAL_MODEL
import tempfile
import os
import json # Cần thiết cho phản hồi JSON

# 1. View hiển thị Form
def upload_form_view(request):
    """Hiển thị form tải lên audio."""
    # Đảm bảo tệp HTML nằm trong thư mục templates/audio_app/
    return render(request, 'audio_model/audio_upload.html')

# 2. View xử lý API (POST)
@csrf_exempt # Tắt CSRF cho endpoint API này
@require_http_methods(["POST"])
def extract_embedding_api(request):
    # 1. Kiểm tra mô hình
    if GLOBAL_MODEL is None:
        return JsonResponse(
            {"success": False, "error": "Mô hình chưa được tải hoặc bị lỗi."},
            status=503 # Service Unavailable
        )

    # 2. Xử lý tệp tải lên
    if 'audio_file' not in request.FILES:
        return JsonResponse(
            {"success": False, "error": "Không tìm thấy tệp 'audio_file' trong request."},
            status=400 # Bad Request
        )

    uploaded_file = request.FILES['audio_file']
    
    # 3. Lưu tệp tạm thời
    # Lưu ý: torchaudio có thể gặp vấn đề nếu không có đuôi tệp
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1] or '.wav') as tmp_file:
        for chunk in uploaded_file.chunks():
            tmp_file.write(chunk)
        temp_path = tmp_file.name

    try:
        # 4. Trích xuất Embedding
        embedding = extract_embedding(GLOBAL_MODEL, temp_path)
        
        # 5. Phản hồi kết quả
        return JsonResponse({
            "success": True,
            # Chuyển numpy array sang list để JSON có thể serialize
            "embedding": embedding.tolist(), 
            "embedding_dim": embedding.shape[0] 
        })

    except Exception as e:
        # 6. Xử lý lỗi trong quá trình xử lý âm thanh/mô hình
        print(f"Lỗi trong quá trình trích xuất: {e}")
        return JsonResponse(
            {"success": False, "error": f"Lỗi xử lý âm thanh hoặc mô hình: {str(e)}"},
            status=500 # Internal Server Error
        )
    finally:
        # 7. Dọn dẹp tệp tạm thời
        os.remove(temp_path)