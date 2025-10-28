from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import MemberRecord
import json

def home(request):
    return render(request, 'member_registing_page/index.html')

@csrf_exempt
def submit_all(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        buttons = json.loads(request.POST.get('buttons'))  # chuyển từ JSON string sang list

        record = MemberRecord.objects.create(name=name, buttons=buttons)

        for i in range(1,4):
            audio = request.FILES.get(f'audio{i}')
            if audio:
                setattr(record, f'audio{i}', audio)

        record.save()
        return JsonResponse({'status': 'ok'})
    
    return JsonResponse({'error': 'invalid request'}, status=400)
