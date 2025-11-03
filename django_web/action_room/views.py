import requests
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from room_registering_page.models import Room
from django.views.decorators.csrf import csrf_exempt
import tempfile


# ✅ URL API model2 — nếu dùng Cloudflare Tunnel, đổi URL tại đây
MODEL2_API_URL = "http://127.0.0.1:5000/predict"
# MODEL2_API_URL = "https://voice-verifier-tuan.cloudflareTunnel.com/predict"

def action_room_view(request, room_id):
    """Hiển thị trang điều khiển của từng phòng"""
    room = get_object_or_404(Room, id=room_id)
    return render(request, 'action_room/action_room.html', {'room': room})


@csrf_exempt
def verify_voice(request):
    if request.method == "POST":
        audio_file = request.FILES.get("audio")
        if not audio_file:
            return JsonResponse({"error": "Không có file audio"}, status=400)

        # ✅ gửi tiếp đến Flask API của bạn
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            for chunk in audio_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        try:
            res = requests.post("http://127.0.0.1:5000/predict", files={"audio": open(tmp_path, "rb")})
            data = res.json()
            return JsonResponse(data)
        except Exception as e:
            return JsonResponse({"error": f"Lỗi Flask API: {e}"}, status=500)
    return JsonResponse({"error": "Phương thức không hợp lệ"}, status=405)
