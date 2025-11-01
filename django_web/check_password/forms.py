from django import forms

class CheckPasswordForm(forms.Form):
    password = forms.CharField(
        label="Nhập mật khẩu phòng",
        widget=forms.PasswordInput(attrs={
            'placeholder': '••••••••',
            'class': 'form-control'
        })
    )
