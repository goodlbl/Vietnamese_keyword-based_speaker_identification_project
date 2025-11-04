import requests
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from room_registering_page.models import Room
from django.views.decorators.csrf import csrf_exempt
import tempfile
import os


# ✅ URL API model2 — nếu dùng Cloudflare Tunnel, đổi URL tại đây
MODEL2_API_URL = "http://127.0.0.1:5000/predict"
# MODEL2_API_URL = "https://voice-verifier-tuan.cloudflareTunnel.com/predict"

def action_room_view(request, room_id):
    """Hiển thị trang điều khiển của từng phòng"""
    room = get_object_or_404(Room, id=room_id)
    return render(request, 'action_room/action_room copy.html', {'room': room})


@csrf_exempt 
def verify_voice(request):
    if request.method == "POST":
        audio_file = request.FILES.get("audio")
        room_id = request.POST.get("room_id")

        if not audio_file:
            return JsonResponse({"error": "Không có file audio"}, status=400)
        if not room_id:
            return JsonResponse({"error": "Thiếu room_id"}, status=400)

        # ✅ Lấy thông tin phòng & chủ phòng
        room = get_object_or_404(Room, id=room_id)
        owner = room.owner

        # ✅ Lấy 3 file mẫu của chủ phòng
        registered_links = []
        for i in range(1, 4):
            audio_field = getattr(owner, f"audio{i}", None)
            if audio_field and hasattr(audio_field, "url"):
                abs_path = request.build_absolute_uri(audio_field.url)
                registered_links.append(abs_path)

        if not registered_links:
            return JsonResponse({"error": "Không tìm thấy audio mẫu cho chủ phòng"}, status=404)

        # ✅ Lưu tạm file audio gửi sang Flask
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            for chunk in audio_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        try:
            with open(tmp_path, "rb") as f:
                files = {"audio": f}
                data = {
                    "owner_name": owner.name,
                    "registered_links": ",".join(registered_links)
                }
                res = requests.post(MODEL2_API_URL, files=files, data=data)
                response_data = res.json()

            # ✅ Sau khi đóng file, mới xóa
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

            return JsonResponse(response_data)

        except Exception as e:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except:
                    pass
            return JsonResponse({"error": f"Lỗi Flask API: {e}"}, status=500)

    return JsonResponse({"error": "Phương thức không hợp lệ"}, status=405)
