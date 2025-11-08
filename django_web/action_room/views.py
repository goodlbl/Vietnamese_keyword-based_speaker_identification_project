import requests
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from room_registering_page.models import Room
from member_registering_page.models import MemberRecord
from django.views.decorators.csrf import csrf_exempt
import numpy as np, json

# ============================================================
# 🔹 Flask API URL
# ============================================================
MODEL2_API_URL = "http://127.0.0.1:5000/predict"
# Nếu dùng Cloudflare tunnel thì đổi dòng trên:
# MODEL2_API_URL = "https://adjust-victory-worldcat-luis.trycloudflare.com/predict"

# ============================================================
# 🔹 Danh sách thiết bị tương ứng thứ tự trong mảng buttons
# ============================================================
DEVICE_NAMES = ["Bếp", "Ti vi", "Máy lạnh", "Quạt", "Quạt trần", "Đèn"]

# ============================================================
# 🔹 Trang hiển thị điều khiển
# ============================================================
def action_room_view(request, room_id):
    """Hiển thị trang điều khiển của từng phòng"""
    room = get_object_or_404(Room, id=room_id)
    return render(request, 'action_room/action_room copy.html', {'room': room})


# ============================================================
# 🔹 Xác thực giọng nói và trả danh sách chức năng
# ============================================================
@csrf_exempt
def verify_voice(request):
    if request.method != "POST":
        return JsonResponse({"error": "Phương thức không hợp lệ"}, status=405)

    audio_file = request.FILES.get("audio")
    room_id = request.POST.get("room_id")

    if not audio_file:
        return JsonResponse({"error": "Không có file audio"}, status=400)
    if not room_id:
        return JsonResponse({"error": "Thiếu room_id"}, status=400)

    # ========================================================
    # 🔸 Lấy thông tin phòng và chủ phòng
    # ========================================================
    room = get_object_or_404(Room, id=room_id)
    owner: MemberRecord = room.owner

    # 🔸 Đọc 3 embedding 192-dim từ chủ phòng
    emb_list = []
    for i in range(1, 4):
        emb_bytes = getattr(owner, f"audio{i}", None)
        if emb_bytes:
            emb = np.frombuffer(emb_bytes, dtype=np.float32)
            emb_list.append(emb.tolist())

    if not emb_list:
        return JsonResponse({"error": "Không có embedding mẫu cho chủ phòng"}, status=404)

    # ========================================================
    # 🔸 Gửi file test + embedding mẫu sang Flask /predict
    # ========================================================
    try:
        files = {"audio": audio_file}
        data = {"ref_embeddings": json.dumps(emb_list)}
        resp = requests.post(MODEL2_API_URL, files=files, data=data, timeout=60)
        flask_data = resp.json()
    except Exception as e:
        return JsonResponse({"error": f"Lỗi Flask API: {e}"}, status=500)

    # ========================================================
    # 🔸 Kiểm tra phản hồi từ Flask
    # ========================================================
    if "score" not in flask_data:
        return JsonResponse({"error": "Không nhận được score từ Flask", "raw": flask_data}, status=500)

    similarity = round(flask_data.get("score", 0.0), 4)
    is_match = flask_data.get("is_match", False)

    # ========================================================
    # 🔸 Nếu giọng khớp → lấy thông tin người đó và quyền
    # ========================================================
    if is_match:
        # Tạm thời chỉ so với chủ phòng (sau có thể mở rộng nhiều người)
        matched_member = owner

        # 🔍 Giải mã quyền từ mảng [1,0,1,1,0,0]
        try:
            raw_buttons = matched_member.buttons
            rights = json.loads(raw_buttons) if isinstance(raw_buttons, str) else raw_buttons
        except Exception:
            rights = [0, 0, 0, 0, 0, 0]

        # 🔍 Lọc thiết bị có quyền
        functions = [DEVICE_NAMES[i] for i, val in enumerate(rights) if val == 1]

        return JsonResponse({
            "owner": matched_member.name,
            "room_id": room_id,
            "similarity": similarity,
            "is_match": True,
            "is_owner": matched_member.is_owner,
            "functions": functions
        })

    # ========================================================
    # 🔸 Nếu không khớp
    # ========================================================
    return JsonResponse({
        "owner": owner.name,
        "room_id": room_id,
        "similarity": similarity,
        "is_match": False
    })
