# Đã xóa 'requests'
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from room_registering_page.models import Room
from member_registering_page.models import MemberRecord
from django.views.decorators.csrf import csrf_exempt
import numpy as np, json
import os, tempfile

# 🚀 Thêm thư viện để so sánh cosine và import model
from sklearn.metrics.pairwise import cosine_similarity
try:
    # Giả sử app chứa model tên là 'audio_model'
    from audio_model.utils import GLOBAL_MODEL, extract_embedding, DEVICE
except ImportError:
    GLOBAL_MODEL = None
    extract_embedding = None

# 🚀 Đặt ngưỡng so sánh (similarity threshold)
# Bạn cần tinh chỉnh con số này dựa trên thực tế
VOICE_THRESHOLD = 0.8 

DEVICE_NAMES = ["Bếp", "Ti vi", "Máy lạnh", "Quạt", "Quạt trần", "Đèn"]

def action_room_view(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    return render(request, 'action_room/action_room.html', {'room': room})

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
    
    # Kiểm tra model đã sẵn sàng chưa
    if not GLOBAL_MODEL or not extract_embedding:
        return JsonResponse({"error": "Dịch vụ model không sẵn sàng"}, status=500)

    room = get_object_or_404(Room, id=room_id)
    owner: MemberRecord = room.owner

    # Đọc 3 embedding mẫu (dạng list-of-lists)
    ref_emb_list = []
    for i in range(1, 4):
        emb_bytes = getattr(owner, f"audio{i}", None)
        if emb_bytes:
            emb = np.frombuffer(emb_bytes, dtype=np.float32)
            ref_emb_list.append(emb) # Giữ ở dạng np.array để xử lý

    if not ref_emb_list:
        return JsonResponse({"error": "Không có embedding mẫu cho chủ phòng"}, status=404)

    # ========================================================
    # 🟩 Xử lý audio và so sánh cục bộ (thay thế API call)
    # ========================================================
    tmp_file_path = None
    try:
        # 1. Trích xuất embedding từ file audio mới
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            for chunk in audio_file.chunks():
                tmp_file.write(chunk)
            tmp_file_path = tmp_file.name
        
        # Gọi hàm utils
        new_emb = extract_embedding(GLOBAL_MODEL, tmp_file_path)
        new_emb_2d = new_emb.reshape(1, -1) # Shape (1, 192)

        # 2. Chuẩn bị embedding mẫu
        # ref_emb_list là list [array(192,), array(192,), ...]
        ref_emb_array = np.array(ref_emb_list) # Shape (3, 192)

        # 3. Tính toán cosine similarity
        scores = cosine_similarity(new_emb_2d, ref_emb_array)
        
        # Lấy điểm trung bình (hoặc max)
        similarity = float(np.mean(scores[0])) 
        is_match = similarity >= VOICE_THRESHOLD

    except Exception as e:
        return JsonResponse({"error": f"Lỗi xử lý audio cục bộ: {e}"}, status=500)
    finally:
        # Luôn xóa file tạm
        if tmp_file_path and os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)
    # ========================================================
    # ❌ Kết thúc khối xử lý cục bộ
    # ========================================================

    if is_match:
        matched_member = owner

        try:
            raw_buttons = matched_member.buttons
            rights = json.loads(raw_buttons) if isinstance(raw_buttons, str) else raw_buttons
        except Exception:
            rights = [0, 0, 0, 0, 0, 0]

        functions = [DEVICE_NAMES[i] for i, val in enumerate(rights) if val == 1]

        return JsonResponse({
            "owner": matched_member.name,
            "room_id": room_id,
            "similarity": round(similarity, 4),
            "is_match": True,
            "is_owner": matched_member.is_owner,
            "functions": functions
        })

    return JsonResponse({
        "owner": owner.name,
        "room_id": room_id,
        "similarity": round(similarity, 4),
        "is_match": False
    })