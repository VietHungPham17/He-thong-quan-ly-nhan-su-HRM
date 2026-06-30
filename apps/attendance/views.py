from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, FormView
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from .models import AttendanceRecord, LeaveRequest, LeaveType, WorkSchedule
from .forms import AttendanceRecordForm, LeaveRequestForm, WorkScheduleForm, GenerateAttendanceForm
from apps.employees.models import Employee, Department
from apps.accounts.mixins import HRRequiredMixin, ManagerRequiredMixin


class AttendanceListView(ManagerRequiredMixin, ListView):
    model = AttendanceRecord
    template_name = 'attendance/attendance_list.html'
    context_object_name = 'records'
    paginate_by = 20

    def get_queryset(self):
        qs = AttendanceRecord.objects.select_related('employee', 'employee__department')
        now = timezone.now()
        month = int(self.request.GET.get('month', now.month))
        year = int(self.request.GET.get('year', now.year))
        qs = qs.filter(date__month=month, date__year=year)

        dept = self.request.GET.get('department', '')
        if dept:
            qs = qs.filter(employee__department_id=dept)

        emp = self.request.GET.get('employee', '')
        if emp:
            qs = qs.filter(employee_id=emp)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        now = timezone.now()
        ctx['month'] = int(self.request.GET.get('month', now.month))
        ctx['year'] = int(self.request.GET.get('year', now.year))
        ctx['departments'] = Department.objects.all()
        ctx['employees'] = Employee.objects.filter(status='active').select_related('department')
        ctx['selected_dept'] = self.request.GET.get('department', '')
        ctx['selected_emp'] = self.request.GET.get('employee', '')
        ctx['years'] = range(now.year - 2, now.year + 2)
        ctx['months'] = range(1, 13)
        return ctx


class AttendanceCreateView(ManagerRequiredMixin, CreateView):
    model = AttendanceRecord
    form_class = AttendanceRecordForm
    template_name = 'attendance/attendance_form.html'
    success_url = reverse_lazy('attendance:attendance_list')

    def form_valid(self, form):
        messages.success(self.request, 'Ghi nhận chấm công thành công!')
        return super().form_valid(form)


class AttendanceUpdateView(ManagerRequiredMixin, UpdateView):
    model = AttendanceRecord
    form_class = AttendanceRecordForm
    template_name = 'attendance/attendance_form.html'
    success_url = reverse_lazy('attendance:attendance_list')

    def form_valid(self, form):
        messages.success(self.request, 'Cập nhật chấm công thành công!')
        return super().form_valid(form)


class LeaveRequestListView(LoginRequiredMixin, ListView):
    model = LeaveRequest
    template_name = 'attendance/leave_request_list.html'
    context_object_name = 'leave_requests'
    paginate_by = 15

    def get_queryset(self):
        qs = LeaveRequest.objects.select_related(
            'employee', 'employee__department', 'leave_type', 'approved_by'
        )
        user = self.request.user

        # Phân quyền hiển thị đơn nghỉ phép
        if user.role in ('admin', 'hr'):
            # Admin và HR được xem toàn bộ hệ thống
            dept = self.request.GET.get('department', '')
            if dept:
                qs = qs.filter(employee__department_id=dept)
        elif user.role == 'manager':
            # Manager chỉ được xem đơn của bản thân và nhân viên trong phòng ban của họ
            try:
                emp_profile = user.employee_profile
                dept = emp_profile.department
                if dept:
                    from django.db.models import Q
                    qs = qs.filter(Q(employee=emp_profile) | Q(employee__department=dept))
                else:
                    qs = qs.filter(employee=emp_profile)
            except Exception:
                qs = qs.none()
        else:
            # Nhân viên thường (role='employee') chỉ xem được đơn của chính mình
            try:
                qs = qs.filter(employee=user.employee_profile)
            except Exception:
                qs = qs.none()

        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['departments'] = Department.objects.all()
        ctx['status_choices'] = LeaveRequest.STATUS_CHOICES
        ctx['selected_status'] = self.request.GET.get('status', '')
        ctx['selected_dept'] = self.request.GET.get('department', '')
        return ctx


class LeaveRequestCreateView(LoginRequiredMixin, CreateView):
    model = LeaveRequest
    form_class = LeaveRequestForm
    template_name = 'attendance/leave_request_form.html'
    success_url = reverse_lazy('attendance:leave_request_list')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        # Kiểm tra user có hồ sơ nhân viên không
        if not hasattr(request.user, 'employee_profile'):
            messages.error(request, 'Tài khoản của bạn chưa được liên kết với hồ sơ nhân viên. Vui lòng liên hệ HR.')
            return redirect('attendance:leave_request_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.employee = self.request.user.employee_profile
        employee = form.instance.employee
        leave_type = form.cleaned_data.get('leave_type')
        days_count = form.cleaned_data.get('days_count') or 0
        year = form.cleaned_data.get('start_date').year if form.cleaned_data.get('start_date') else None

        # Kiểm tra số dư nghỉ phép
        if leave_type and year:
            from .models import LeaveBalance
            try:
                balance = LeaveBalance.objects.get(
                    employee=employee, leave_type=leave_type, year=year
                )
                if days_count > balance.remaining_days:
                    form.add_error(
                        None,
                        f'Số ngày nghỉ ({days_count}) vượt quá số dư còn lại '
                        f'({balance.remaining_days} ngày) của loại "{leave_type.name}".'
                    )
                    return self.form_invalid(form)
            except LeaveBalance.DoesNotExist:
                pass  # Chưa có bản ghi số dư — cho phép gửi đơn

        messages.success(self.request, 'Gửi đơn nghỉ phép thành công!')
        return super().form_valid(form)



def approve_leave(request, pk):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    if not request.user.can_manage:
        messages.error(request, 'Bạn không có quyền duyệt đơn nghỉ phép.')
        return redirect('attendance:leave_request_list')
    leave = get_object_or_404(LeaveRequest, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            leave.status = 'approved'
            leave.approved_by = request.user
            leave.approved_at = timezone.now()
            leave.save()
            messages.success(request, 'Đã duyệt đơn nghỉ phép.')
        elif action == 'reject':
            leave.status = 'rejected'
            leave.approved_by = request.user
            leave.approved_at = timezone.now()
            leave.save()
            messages.warning(request, 'Đã từ chối đơn nghỉ phép.')
    return redirect('attendance:leave_request_list')


def cancel_leave(request, pk):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    leave = get_object_or_404(LeaveRequest, pk=pk)
    
    # Chỉ chủ sở hữu đơn mới có quyền huỷ đơn của mình
    if not hasattr(request.user, 'employee_profile') or leave.employee != request.user.employee_profile:
        messages.error(request, 'Bạn không có quyền huỷ đơn này.')
        return redirect('attendance:leave_request_list')
        
    # Chỉ được huỷ đơn khi ở trạng thái chờ duyệt (pending)
    if leave.status != 'pending':
        messages.error(request, 'Chỉ có thể huỷ đơn nghỉ phép ở trạng thái chờ duyệt.')
        return redirect('attendance:leave_request_list')
        
    if request.method == 'POST':
        leave.delete()
        messages.success(request, 'Đã huỷ đơn nghỉ phép thành công.')
        
    return redirect('attendance:leave_request_list')


class WorkScheduleListView(HRRequiredMixin, ListView):
    model = WorkSchedule
    template_name = 'attendance/work_schedule_list.html'
    context_object_name = 'schedules'


class WorkScheduleCreateView(HRRequiredMixin, CreateView):
    model = WorkSchedule
    form_class = WorkScheduleForm
    template_name = 'attendance/work_schedule_form.html'
    success_url = reverse_lazy('attendance:work_schedule_list')

    def form_valid(self, form):
        messages.success(self.request, 'Tạo ca làm việc thành công!')
        return super().form_valid(form)


class GenerateAttendanceView(ManagerRequiredMixin, FormView):
    """Tạo chấm công hàng loạt cho toàn bộ nhân viên active trong 1 ngày."""
    template_name = 'attendance/generate_attendance.html'
    form_class = GenerateAttendanceForm
    success_url = reverse_lazy('attendance:attendance_list')

    def get_initial(self):
        from datetime import date
        return {
            'date': date.today(),
            'default_check_in': '08:00',
            'default_check_out': '17:00',
            'default_status': 'present',
        }

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['employee_count'] = Employee.objects.filter(status='active').count()
        return ctx

    def form_valid(self, form):
        target_date   = form.cleaned_data['date']
        status        = form.cleaned_data['default_status']
        check_in      = form.cleaned_data.get('default_check_in')
        check_out     = form.cleaned_data.get('default_check_out')

        # Nếu trạng thái là vắng thì không điền giờ
        if status == 'absent':
            check_in = None
            check_out = None

        employees = Employee.objects.filter(status='active')
        created = skipped = 0

        for emp in employees:
            _, new = AttendanceRecord.objects.get_or_create(
                employee=emp,
                date=target_date,
                defaults={
                    'check_in': check_in,
                    'check_out': check_out,
                    'status': status,
                    'note': 'Tạo hàng loạt',
                },
            )
            if new:
                created += 1
            else:
                skipped += 1

        messages.success(
            self.request,
            f'Đã tạo {created} bản ghi chấm công ngày {target_date.strftime("%d/%m/%Y")}. '
            f'Bỏ qua {skipped} (đã tồn tại). '
            f'Vào bảng chấm công để chỉnh sửa những nhân viên vắng/muộn.'
        )
        return super().form_valid(form)
