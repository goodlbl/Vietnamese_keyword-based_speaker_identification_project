from django.shortcuts import render, get_object_or_404
from .models import RoomActivity
from room_registering_page.models import Room

def room_history(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    
    sort_by = request.GET.get('sort', 'time')
    order = request.GET.get('order', 'desc')

    ordering_map = {
        'member': 'user__name',
        'action': 'status',
        'role': 'user__is_owner', 
        'time': 'time'
    }

    sort_field = ordering_map.get(sort_by, 'time')
    
    if order == 'desc':
        sort_field = '-' + sort_field

    activities = RoomActivity.objects.filter(room=room)\
        .select_related('user')\
        .order_by(sort_field)
    
    context = {
        'room': room,
        'activities': activities,
        'current_sort': sort_by,
        'current_order': order,
    }
    
    return render(request, 'room_activity/room_activity.html', context)