from django.shortcuts import render, get_object_or_404
from member_registering_page.models import MemberRecord
from .models import Room
import io, numpy as np
from random import randint
import os, tempfile

try:
    from main_page.utils import GLOBAL_MODEL, extract_embedding, DEVICE
    print(f"✅ Tải model thành công trên {DEVICE} cho đăng ký căn hộ views.")
except ImportError:
    print("❌ LỖI IMPORT: Không tìm thấy utils.py hoặc model.")
    GLOBAL_MODEL = None
    extract_embedding = None

def create_owner_and_room(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        buttons = [1, 1, 1, 1, 1, 1]

        record = MemberRecord.objects.create(name=name, buttons=buttons, is_owner=True)

        # Trích xuất embedding cục bộ
        if GLOBAL_MODEL and extract_embedding:
            embeddings_to_save = {}
            for i in range(1, 4):
                audio_file = request.FILES.get(f'audio{i}')
                if not audio_file:
                    continue

                tmp_file_path = None
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                        for chunk in audio_file.chunks():
                            tmp_file.write(chunk)
                        tmp_file_path = tmp_file.name
                    
                    emb_array = extract_embedding(GLOBAL_MODEL, tmp_file_path)
                    embeddings_to_save[f"audio{i}"] = np.array(emb_array, dtype=np.float32).tobytes()

                except Exception as e:
                    # Gặp lỗi khi xử lý file audio
                    pass 
                
                finally:
                    if tmp_file_path and os.path.exists(tmp_file_path):
                        os.remove(tmp_file_path)
            
            # Lưu các embedding vào record
            if embeddings_to_save:
                update_fields = []
                for field, data in embeddings_to_save.items():
                    setattr(record, field, data)
                    update_fields.append(field)
                record.save(update_fields=update_fields)

        # Tạo phòng mới
        room_number = request.POST.get('room_number') or f"R{record.id:04d}"
        password = request.POST.get('password') or "1234"

        while Room.objects.filter(room_number=room_number).exists():
            room_number = f"R{randint(1000, 9999)}"

        new_room = Room.objects.create(
            room_number=room_number,
            password=password,
            owner=record,
            total_members=1
        )

        record.room = new_room.id
        record.save(update_fields=["room"])

        request.session['room_id'] = new_room.id

        return render(request, 'action_room/action_room.html', {'room': new_room})

    return render(request, 'room_registering_page/owner_and_room_register.html')