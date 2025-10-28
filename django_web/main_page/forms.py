from django import forms
from room_registering_page.models import Room

class RoomSearchForm(forms.Form):
    room_number = forms.CharField(label='Nhập số phòng', max_length=10)

class RoomCreateForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['room_number', 'password']
        labels = {
            'room_number': 'Số phòng',
            'password': 'Mật khẩu phòng',
        }
