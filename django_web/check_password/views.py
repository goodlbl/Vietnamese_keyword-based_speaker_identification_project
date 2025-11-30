from django.shortcuts import render, redirect, get_object_or_404
from .forms import CheckPasswordForm
from room_registering_page.models import Room

def check_password_view(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    error = None

    if request.method == "POST":
        form = CheckPasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            request.session['room_id'] = room.id
            if password == room.password:
                return redirect('member_registering_page:register') 
            else:
                error = "Mật khẩu không đúng."
    else:
        form = CheckPasswordForm()

    return render(request, 'check_password/check_password.html', {
        'form': form,
        'room': room,
        'error': error
    })
