from django.shortcuts import render, redirect, get_object_or_404
from room_registering_page.models import Room
from .forms import RoomSearchForm
from django.urls import reverse
from django.utils.translation import gettext as _ 

def home(request):
    message = None

    if request.method == 'POST':
        form = RoomSearchForm(request.POST)
        if form.is_valid():
            room_number = form.cleaned_data['room_number']
            room = Room.objects.filter(room_number=room_number).first()

            if room:
                return redirect(reverse('action_room:action_room_view', args=[room.id]))
            else:
                message = _("Căn hộ mã {room_number} chưa được tạo.").format(room_number=room_number)
    else:
        form = RoomSearchForm()

    return render(request, 'main_page/home.html', {
        'form': form,
        'message': message
    })


def room_detail(request, room_id): 
    room = get_object_or_404(Room, id=room_id)

    return render(request, 'main_page/room_detail.html', {
        'room': room
    })
