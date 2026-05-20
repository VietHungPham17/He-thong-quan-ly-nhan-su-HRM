from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect


class HRRequiredMixin(LoginRequiredMixin):
    """Chỉ Admin và HR được truy cập."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.role not in ('admin', 'hr'):
            messages.error(request, 'Bạn không có quyền thực hiện chức năng này.')
            return redirect('employees:dashboard')
        return super().dispatch(request, *args, **kwargs)


class ManagerRequiredMixin(LoginRequiredMixin):
    """Admin, HR và Manager được truy cập."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.can_manage:
            messages.error(request, 'Bạn không có quyền truy cập chức năng này.')
            return redirect('employees:dashboard')
        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(LoginRequiredMixin):
    """Chỉ Admin được truy cập."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.role != 'admin':
            messages.error(request, 'Chỉ quản trị viên mới có quyền thực hiện chức năng này.')
            return redirect('employees:dashboard')
        return super().dispatch(request, *args, **kwargs)
