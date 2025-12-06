from django.shortcuts import render, get_object_or_404
from member_registering_page.models import MemberRecord
from .models import Room
import io, numpy as np
from random import randint
import os, tempfile
from django.http import JsonResponse
from django.urls import reverse
from django.utils.translation import gettext as _
from django.contrib import messages

try:
    from main_page.utils import GLOBAL_MODEL, extract_embedding, DEVICE
    print(f"✅ Tải model thành công trên {DEVICE} cho đăng ký căn hộ views.")
except ImportError:
    print("❌ LỖI IMPORT: Không tìm thấy utils.py hoặc model.")
    GLOBAL_MODEL = None
    extract_embedding = None

def create_owner_and_room(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        name = request.POST.get('name')
        room_number = request.POST.get('room_number')
        password = request.POST.get('password') or "1234"

        if Room.objects.filter(room_number=room_number).exists():
            return JsonResponse({
                'success': False,
                'message': _('Số căn hộ %(room)s đã tồn tại.') % {'room': room_number}
            })
        buttons = [1, 1, 1, 1, 1, 1]
        record = MemberRecord.objects.create(name=name, buttons=buttons, is_owner=True)

        missing_audio = False
        for i in range(1, 4):
            if not request.FILES.get(f'audio{i}'):
                missing_audio = True
                break
        
        if missing_audio:
            return JsonResponse({
                'success': False,
                'message': _('Vui lòng thu đủ file audio')
            })
        
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
                except Exception:
                    pass
                finally:
                    if tmp_file_path and os.path.exists(tmp_file_path):
                        os.remove(tmp_file_path)
            if embeddings_to_save:
                update_fields = []
                for field, data in embeddings_to_save.items():
                    setattr(record, field, data)
                    update_fields.append(field)
                record.save(update_fields=update_fields)

        new_room = Room.objects.create(
            room_number=room_number,
            password=password,
            owner=record,
            total_members=1
        )
        record.room = new_room.id
        record.save(update_fields=["room"])
        request.session['room_id'] = new_room.id

        return JsonResponse({
            'success': True,
            'message': f'Căn hộ {room_number} đã tạo thành công!',
            'redirect_url': reverse('action_room:action_room_view', args=[new_room.id])
        })

    return render(request, 'room_registering_page/owner_and_room_register.html')