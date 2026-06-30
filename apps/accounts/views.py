from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, UpdateView, TemplateView
from .forms import LoginForm, ProfileForm
from .models import User


class LoginView(FormView):
    template_name = 'accounts/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('employees:dashboard')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('employees:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        messages.success(self.request, f'Chào mừng {user.get_full_name() or user.username}!')
        next_url = self.request.GET.get('next', '')
        if next_url:
            return redirect(next_url)
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Tên đăng nhập hoặc mật khẩu không đúng.')
        return super().form_invalid(form)


class LogoutView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/logout_confirm.html'

    def post(self, request, *args, **kwargs):
        logout(request)
        messages.info(request, 'Bạn đã đăng xuất thành công.')
        return redirect('accounts:login')

    def get(self, request, *args, **kwargs):
        # Hiển thị trang xác nhận đăng xuất (fallback an toàn)
        return super().get(request, *args, **kwargs)


class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Cập nhật hồ sơ thành công!')
        return super().form_valid(form)
