from django.shortcuts import render, redirect, get_object_or_404
from member_registering_page.models import MemberRecord
from .models import Room

def create_owner_and_room(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        buttons = [1, 1, 1, 1, 1, 1]

        record = MemberRecord.objects.create(name=name, buttons=buttons)

        for i in range(1, 4):
            audio = request.FILES.get(f'audio{i}')
            if audio:
                setattr(record, f'audio{i}', audio)
        record.save()

        room_number = request.POST.get('room_number')
        password = request.POST.get('password')

        if not room_number:
            room_number = f"R{record.id:04d}" 
        if not password:
            password = "1234"

        new_room = Room.objects.create(
            room_number=room_number,
            password=password,
            owner=record,
            total_members=1
        )

        record.room = new_room.id
        record.save()
        room = get_object_or_404(Room, id=new_room.id)

        return render(request, 'action_room/action_room.html', {
        'room': room
    })

    return render(request, 'room_registering_page/owner_and_room_register.html')
