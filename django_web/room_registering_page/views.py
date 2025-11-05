# room_registering_page/views.py
from django.shortcuts import render, get_object_or_404
from member_registering_page.models import MemberRecord
from .models import Room
import io, requests, numpy as np
from random import randint

MODEL2_API_URL = "http://127.0.0.1:5000/predict_embedding"

def create_owner_and_room(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        buttons = [1, 1, 1, 1, 1, 1]

        # 1️⃣ Tạo record chủ phòng
        record = MemberRecord.objects.create(name=name, buttons=buttons, is_owner=True)

        # 2️⃣ Thu 3 audio
        audio_files = []
        for i in range(1, 4):
            audio = request.FILES.get(f'audio{i}')
            if audio:
                audio_bytes = audio.read()
                audio_files.append(('files', (audio.name, io.BytesIO(audio_bytes), audio.content_type)))

        # 3️⃣ Gọi Flask model2 (như member)
        try:
            resp = requests.post(MODEL2_API_URL, files=audio_files, timeout=60)
            data = resp.json()

            if "embeddings" in data:
                for i, emb_vec in enumerate(data["embeddings"], start=1):
                    emb_array = np.array(emb_vec, dtype=np.float32)
                    setattr(record, f"audio{i}", emb_array.tobytes())
                record.save(update_fields=["audio1", "audio2", "audio3"])
                print(f"✅ Lưu embedding chủ phòng {name} thành công!")
            else:
                print("⚠️ Flask không trả về embeddings:", data)

        except Exception as e:
            print(f"🔥 Lỗi khi gọi Flask API: {e}")

        # 4️⃣ Tạo phòng mới
        room_number = request.POST.get('room_number') or f"R{record.id:04d}"
        password = request.POST.get('password') or "1234"

        # tránh trùng số phòng
        while Room.objects.filter(room_number=room_number).exists():
            room_number = f"R{randint(1000, 9999)}"

        new_room = Room.objects.create(
            room_number=room_number,
            password=password,
            owner=record,
            total_members=1
        )

        # Lưu session (để member sau này dùng)
        request.session['room_id'] = new_room.id

        print(f"🏠 Đã tạo phòng {room_number} với chủ {name}")
        return render(request, 'action_room/action_room copy.html', {'room': new_room})

    return render(request, 'room_registering_page/owner_and_room_register.html')
