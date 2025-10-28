from django.shortcuts import render, redirect
from room_registering_page.models import Room
from .forms import RoomSearchForm

# 👇 bạn không gọi trực tiếp create_owner() mà redirect đến URL của nó
# vì hàm đó render riêng trang khác
def home(request):
    if request.method == 'POST':
        form = RoomSearchForm(request.POST)
        if form.is_valid():
            room_number = form.cleaned_data['room_number']
            room = Room.objects.filter(room_number=room_number).first()
            if room:
                message = f"Phòng {room_number} đã tồn tại!"
            else:
                message = f"Phòng {room_number} chưa được tạo."
            return render(request, 'main_page/room_detail.html', {
                'message': message,
                'room_number': room_number
            })
    else:
        form = RoomSearchForm()

    return render(request, 'main_page/home.html', {'form': form})
