from django.shortcuts import render, redirect, get_object_or_404
from member_registering_page.models import MemberRecord
from .models import Room
import json

def create_owner(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        buttons = [1, 1, 1, 1, 1, 1]

        record = MemberRecord.objects.create(name=name, buttons=buttons)

        for i in range(1, 4):
            audio = request.FILES.get(f'audio{i}')
            if audio:
                setattr(record, f'audio{i}', audio)

        record.save()

        return redirect('create_room', owner_id=record.id)

    return render(request, 'room_registering_page/owner_register.html')


def create_room(request, owner_id):
    owner = get_object_or_404(MemberRecord, id=owner_id)

    if request.method == 'POST':
        room_number = request.POST.get('room_number')
        password = request.POST.get('password')
        total_members = 1

        new_room = Room.objects.create(
            room_number=room_number,
            password=password,
            owner=owner,
            total_members=total_members
        )

        owner.room = new_room.id
        owner.save()

        return render(request, 'room_registering_page/owner_register.html')

    return render(request, 'room_registering_page/room_register.html', {'owner': owner})



