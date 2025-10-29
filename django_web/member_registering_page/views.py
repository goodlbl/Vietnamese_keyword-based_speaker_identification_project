from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import MemberRecord
import json

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
            room=room_id,  # tương ứng với field room trong model
            buttons=buttons
        )

        for i in range(1, 4):
            file = request.FILES.get(f'audio{i}')
            if file:
                setattr(member, f'audio{i}', file)
        member.save()

        return JsonResponse({'success': True, 'user_id': member.id})

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)