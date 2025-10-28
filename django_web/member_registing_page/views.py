from django.shortcuts import render, redirect
from .models import ButtonState

def home(request):
    # Khởi tạo 6 nút nếu chưa có
    if ButtonState.objects.count() == 0:
        for i in range(1, 7):
            ButtonState.objects.create(index=i, state=False)

    buttons = ButtonState.objects.all().order_by('index')

    return render(request, 'member_registing_page/index.html', {'buttons': buttons})


def toggle_button(request, idx):
    try:
        btn = ButtonState.objects.get(index=idx)
        btn.state = not btn.state
        btn.save()
    except ButtonState.DoesNotExist:
        pass
    return redirect('home')  # quay lại trang chính
