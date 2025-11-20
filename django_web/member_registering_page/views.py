from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import MemberRecord
from room_registering_page.models import Room
import json, io, numpy as np
import os, tempfile

try:
    from main_page.utils import GLOBAL_MODEL, extract_embedding, DEVICE
    print(f"✅ Tải model thành công trên {DEVICE} cho đăng ký người dùng views.")
except ImportError:
    print("❌ LỖI IMPORT: Không tìm thấy utils.py hoặc model.")
    GLOBAL_MODEL = None
    extract_embedding = None


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

        member = MemberRecord.objects.create(
            name=name,
            room=room_id,
            buttons=buttons
        )
        
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
        

        if GLOBAL_MODEL is None or extract_embedding is None:
            print("🔥 LỖI: Model chưa được tải. Không thể xử lý audio.")
            return JsonResponse({'success': False, 'error': 'Model service is unavailable'}, status=500)

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
                
                print(f"Đang trích xuất embedding cho {name} - audio{i}...")
                emb_array = extract_embedding(GLOBAL_MODEL, tmp_file_path)
                
                embeddings_to_save[f"audio{i}"] = np.array(emb_array, dtype=np.float32).tobytes()
                print(f"✅ Trích xuất audio{i} thành công.")

            except Exception as e:
                print(f"🔥 Lỗi khi trích xuất embedding cho audio{i}: {e}")
            
            finally:
                if tmp_file_path and os.path.exists(tmp_file_path):
                    os.remove(tmp_file_path)

        if embeddings_to_save:
            update_fields = []
            for field, data in embeddings_to_save.items():
                setattr(member, field, data)
                update_fields.append(field)
            
            member.save(update_fields=update_fields)
            print(f"✅ Đã lưu {len(update_fields)} embeddings vào DB cho {name}")
        else:
            print(f"⚠️ Không có file audio nào được xử lý cho {name}.")

        redirect_url = f"/action_room/{room_id}/"
        return JsonResponse({'success': True, 'redirect_url': redirect_url})

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


def back_to_password(request):
    room_id = request.session.get("room_id")
    room = get_object_or_404(Room, id=room_id)

    if room_id:
        return render(request, 'action_room/action_room.html', {'room': room})
    else:
        return redirect("/")