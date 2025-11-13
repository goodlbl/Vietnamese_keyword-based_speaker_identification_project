from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from room_registering_page.models import Room
from member_registering_page.models import MemberRecord
from django.views.decorators.csrf import csrf_exempt
import numpy as np, json, os, tempfile
from sklearn.metrics.pairwise import cosine_similarity

# 🔹 Import mô hình nhận dạng giọng nói
try:
    from main_page.utils import GLOBAL_MODEL, extract_embedding, DEVICE
except ImportError:
    GLOBAL_MODEL = None
    extract_embedding = None

VOICE_THRESHOLD = 0.5

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

    # 🔹 Lấy object Room (để kiểm tra tồn tại)
    room = get_object_or_404(Room, id=room_id)

    # 🔹 Lấy toàn bộ thành viên có cùng room_id (lưu dưới dạng số)
    members = MemberRecord.objects.filter(room=room.id)




    # ========================================================
    # 🟩 Xử lý audio và so sánh với tất cả thành viên
    # ========================================================
    tmp_file_path = None
    try:
        # Lưu file audio tạm để trích xuất embedding
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            for chunk in audio_file.chunks():
                tmp_file.write(chunk)
            tmp_file_path = tmp_file.name

        # Trích xuất embedding giọng nói mới
        new_emb = extract_embedding(GLOBAL_MODEL, tmp_file_path)
        new_emb_2d = new_emb.reshape(1, -1)

        results = []
        for member in members:
            ref_emb_list = []
            for i in range(1, 4):
                emb_bytes = getattr(member, f"audio{i}", None)
                if emb_bytes:
                    emb = np.frombuffer(emb_bytes, dtype=np.float32)
                    ref_emb_list.append(emb)

            if not ref_emb_list:
                continue

            ref_emb_array = np.array(ref_emb_list)
            scores = cosine_similarity(new_emb_2d, ref_emb_array)
            similarity = float(np.mean(scores[0]))  # 0 → 1

            results.append({
                "name": member.name,
                "similarity": round(similarity, 4),   # Giữ trong [0,1]
                "is_match": similarity >= VOICE_THRESHOLD,
                "is_owner": member.is_owner,
            })

        # 🔹 Sắp xếp giảm dần theo similarity
        results.sort(key=lambda x: x["similarity"], reverse=True)

    except Exception as e:
        return JsonResponse({"error": f"Lỗi xử lý audio: {e}"}, status=500)
    finally:
        if tmp_file_path and os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)

    # ========================================================
    # ✅ Tìm người khớp nhất (nếu có)
    # ========================================================
    matched_member = None
    best_result = max(results, key=lambda x: x["similarity"]) if results else None

    if best_result and best_result["is_match"]:
        matched_member = members.get(name=best_result["name"])

        try:
            raw_buttons = matched_member.buttons
            rights = json.loads(raw_buttons) if isinstance(raw_buttons, str) else raw_buttons
        except Exception:
            rights = [0, 0, 0, 0, 0, 0]

        functions = [DEVICE_NAMES[i] for i, val in enumerate(rights) if val == 1]
    else:
        functions = []

    # ========================================================
    # ✅ Trả về toàn bộ kết quả + thiết bị nếu có
    # ========================================================
    return JsonResponse({
        "results": results,  # Danh sách tất cả thành viên
        "matched_member": best_result["name"] if best_result else None,
        "room_id": room_id,
        "functions": functions
    })
