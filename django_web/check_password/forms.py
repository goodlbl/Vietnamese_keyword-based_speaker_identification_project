from django import forms

class CheckPasswordForm(forms.Form):
    room_number = forms.CharField(label="Số phòng", max_length=20)
    password = forms.CharField(label="Mật khẩu", widget=forms.PasswordInput)
