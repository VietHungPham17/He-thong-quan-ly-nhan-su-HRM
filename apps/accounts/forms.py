import re

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

from .models import User


# ─── Helpers ──────────────────────────────────────────────────────────────────

PHONE_VN_REGEX = re.compile(r'^(0|\+84)[0-9]{9,10}$')


# ─── LoginForm ────────────────────────────────────────────────────────────────

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Tên đăng nhập',
            'autofocus': True,
        }),
        label='Tên đăng nhập'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Mật khẩu',
        }),
        label='Mật khẩu'
    )


# ─── ProfileForm ──────────────────────────────────────────────────────────────

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'avatar']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'first_name': 'Tên',
            'last_name': 'Họ',
            'email': 'Email',
            'phone': 'Số điện thoại',
            'avatar': 'Ảnh đại diện',
        }

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name', '').strip()
        if first_name and re.search(r'[0-9!@#$%^&*()\[\]{};:\'",.<>?/\\|`~]', first_name):
            raise ValidationError('Tên không được chứa số hoặc ký tự đặc biệt.')
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name', '').strip()
        if last_name and re.search(r'[0-9!@#$%^&*()\[\]{};:\'",.<>?/\\|`~]', last_name):
            raise ValidationError('Họ không được chứa số hoặc ký tự đặc biệt.')
        return last_name

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if email:
            # Kiểm tra email không trùng với người dùng khác
            qs = User.objects.filter(email=email)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError('Địa chỉ email này đã được sử dụng bởi tài khoản khác.')
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if phone:
            if not PHONE_VN_REGEX.match(phone):
                raise ValidationError(
                    'Số điện thoại không hợp lệ. Vui lòng nhập đúng định dạng Việt Nam (vd: 0901234567).'
                )
        return phone

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar and hasattr(avatar, 'name'):
            ext = '.' + avatar.name.rsplit('.', 1)[-1].lower() if '.' in avatar.name else ''
            allowed_exts = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
            if ext not in allowed_exts:
                raise ValidationError(
                    f'Định dạng ảnh không hợp lệ. Chỉ chấp nhận: {", ".join(allowed_exts).upper()}.'
                )
            # Giới hạn kích thước file 5MB
            if avatar.size > 5 * 1024 * 1024:
                raise ValidationError('Kích thước ảnh đại diện không được vượt quá 5MB.')
        return avatar
