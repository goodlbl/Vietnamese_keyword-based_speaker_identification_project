from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import MemberRecord
import json
from room_registering_page.models import Room

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

        for i in range(1, 4):
            file = request.FILES.get(f'audio{i}')
            if file:
                setattr(member, f'audio{i}', file)
        member.save()

        redirect_url = f"/room/{room_id}/"

        return JsonResponse({'success': True, 'redirect_url': redirect_url})

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)