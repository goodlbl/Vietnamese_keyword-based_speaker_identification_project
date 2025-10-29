from django.shortcuts import render, redirect
from .forms import CheckPasswordForm
from room_registering_page.models import Room  # Model Room hiện tại chứa số phòng và password

def check_password_view(request):
    error = None
    if request.method == "POST":
        form = CheckPasswordForm(request.POST)
        if form.is_valid():
            room_number = form.cleaned_data['room_number']
            password = form.cleaned_data['password']
            
            try:
                room = Room.objects.get(room_number=room_number, password=password)
                return redirect('room_registering_page:create_owner')  # Trang tiếp theo
            except Room.DoesNotExist:
                error = "Số phòng hoặc mật khẩu không đúng."
    else:
        form = CheckPasswordForm()
    
    return render(request, 'check_password/check_password.html', {'form': form, 'error': error})
