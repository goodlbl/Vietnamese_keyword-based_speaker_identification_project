import requests
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from room_registering_page.models import Room
from member_registering_page.models import MemberRecord
from django.views.decorators.csrf import csrf_exempt
import numpy as np, json

# ✅ Flask API URL (điểm tới /predict)
MODEL2_API_URL = "http://127.0.0.1:5000/predict"

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
        owner: MemberRecord = room.owner

        # ✅ Đọc 3 embedding 192-dim từ DB
        emb_list = []
        for i in range(1, 4):
            emb_bytes = getattr(owner, f"audio{i}", None)
            if emb_bytes:
                emb = np.frombuffer(emb_bytes, dtype=np.float32)
                emb_list.append(emb.tolist())

        if not emb_list:
            return JsonResponse({"error": "Không có embedding mẫu cho chủ phòng"}, status=404)

        # ✅ Gửi file test + embedding mẫu sang Flask /predict
        try:
            files = {"audio": audio_file}
            data = {"ref_embeddings": json.dumps(emb_list)}

            resp = requests.post(MODEL2_API_URL, files=files, data=data, timeout=60)
            data = resp.json()

        except Exception as e:
            return JsonResponse({"error": f"Lỗi Flask API: {e}"}, status=500)

        # ✅ Kiểm tra phản hồi từ Flask
        if "score" not in data:
            return JsonResponse({"error": "Không nhận được score từ Flask", "raw": data}, status=500)

        return JsonResponse({
            "owner": owner.name,
            "room_id": room_id,
            "similarity": round(data["score"], 4),
            "is_match": data.get("is_match", False)
        })

    return JsonResponse({"error": "Phương thức không hợp lệ"}, status=405)
