from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import MemberRecord
from room_registering_page.models import Room
import json, requests, io, numpy as np

# URL Flask API model2
MODEL2_API_URL = "http://127.0.0.1:5000/predict_embedding"

def register_view(request):
    return render(request, 'member_registering_page/index.html')

def submit_all(request):
    if request.method == 'POST':
        room_id = request.session.get('room_id')
        if not room_id:
            return JsonResponse({'success': False, 'error': 'No room_id in session'}, status=400)

        name = request.POST.get('name')
        if not name:
            return JsonResponse({'success': False, 'error': 'No name provided'}, status=400)

        buttons_json = request.POST.get('buttons')
        buttons = json.loads(buttons_json) if buttons_json else []

        # 🟩 1️⃣ Tạo record ban đầu
        member = MemberRecord.objects.create(
            name=name,
            room=room_id,
            buttons=buttons
        )

        # 🟩 2️⃣ Chuẩn bị 3 file audio gửi sang Flask
        audio_files = []
        for i in range(1, 4):
            audio = request.FILES.get(f'audio{i}')
            if audio:
                audio_bytes = audio.read()
                audio_files.append(('files', (audio.name, io.BytesIO(audio_bytes), audio.content_type)))

        # 🟩 3️⃣ Gọi Flask API để trích embedding
        try:
            resp = requests.post(MODEL2_API_URL, files=audio_files, timeout=60)
            data = resp.json()

            if "embeddings" in data:
                emb_list = data["embeddings"]

                # ✅ Lưu từng embedding (192-dim float32)
                for i, emb_vec in enumerate(emb_list, start=1):
                    emb_array = np.array(emb_vec, dtype=np.float32)
                    setattr(member, f"audio{i}", emb_array.tobytes())

                member.save(update_fields=["audio1", "audio2", "audio3"])
                print(f"✅ 3 embeddings saved to DB for {name}")
            else:
                print("⚠️ Không nhận được embeddings từ Flask:", data)

        except Exception as e:
            print(f"🔥 Lỗi khi gọi Flask API: {e}")

        redirect_url = f"/action_room/{room_id}/"
        return JsonResponse({'success': True, 'redirect_url': redirect_url})

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

def back_to_password(request):
    room_id = request.session.get("room_id")
    room = get_object_or_404(Room, id=room_id)

    if room_id:
        return render(request, 'main_page/room_detail.html', {'room': room})
    else:
        return redirect("/")
