from django import forms

class CheckPasswordForm(forms.Form):
    password = forms.CharField(
        label="Nhập mật khẩu căn hộ",
        widget=forms.PasswordInput(attrs={
            'placeholder': '••••••••',
            'class': 'form-control'
        })
    )
