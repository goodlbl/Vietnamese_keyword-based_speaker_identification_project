from django.shortcuts import render, get_object_or_404
from room_registering_page.models import Room

def action_room_view(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    return render(request, 'action_room/action_room.html', {'room': room})

