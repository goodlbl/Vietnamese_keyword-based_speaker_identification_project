from django.shortcuts import render, get_object_or_404
from member_registering_page.models import MemberRecord
from .models import Room
import io, requests, numpy as np

def create_owner_and_room(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        buttons = [1, 1, 1, 1, 1, 1]

        record = MemberRecord.objects.create(name=name, buttons=buttons)

        # 🟩 Lấy 3 file audio
        audio_files = []
        for i in range(1, 4):
            audio = request.FILES.get(f'audio{i}')
            if audio:
                # chỉ đọc 1 lần, không lưu file .wav nữa
                audio_bytes = audio.read()
                audio_files.append(('files', (audio.name, io.BytesIO(audio_bytes), audio.content_type)))

        try:
            # 🟩 Gửi sang Flask để trích embedding
            resp = requests.post("http://127.0.0.1:5000/predict_embedding", files=audio_files, timeout=60)
            data = resp.json()

            if "embeddings" in data:
                emb_list = data["embeddings"]

                # ✅ Lưu embedding (float32 → bytes)
                for i, emb_vec in enumerate(emb_list, start=1):
                    emb_array = np.array(emb_vec, dtype=np.float32)
                    setattr(record, f"audio{i}", emb_array.tobytes())

                record.save(update_fields=["audio1", "audio2", "audio3"])
                print(f"✅ Đã lưu 3 embedding 192-dim cho {name}")
            else:
                print("⚠️ Flask không trả về embeddings:", data)

        except Exception as e:
            print(f"🔥 Lỗi khi gọi Flask API: {e}")

        # 🟩 4️⃣ Tạo phòng mới
        room_number = request.POST.get('room_number') or f"R{record.id:04d}"
        password = request.POST.get('password') or "1234"

        # tránh trùng room_number
        from random import randint
        while Room.objects.filter(room_number=room_number).exists():
            room_number = f"R{randint(1000, 9999)}"

        new_room = Room.objects.create(
            room_number=room_number,
            password=password,
            owner=record,
            total_members=1
        )

        record.room = new_room.id
        record.save()

        room = get_object_or_404(Room, id=new_room.id)
        return render(request, 'action_room/action_room.html', {'room': room})

    return render(request, 'room_registering_page/owner_and_room_register.html')
