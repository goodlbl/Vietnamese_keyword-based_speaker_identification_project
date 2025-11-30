from django import forms
from django.utils.translation import gettext_lazy as _

class CheckPasswordForm(forms.Form):
    password = forms.CharField(
        label=_("Nhập mật khẩu căn hộ"),
        widget=forms.PasswordInput(attrs={
            'placeholder': '••••••••',
            'class': 'form-control'
        })
    )
