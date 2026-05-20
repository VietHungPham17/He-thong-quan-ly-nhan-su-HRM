from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, TemplateView
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from .models import AttendanceRecord, LeaveRequest, LeaveType, WorkSchedule
from .forms import AttendanceRecordForm, LeaveRequestForm, WorkScheduleForm
from apps.employees.models import Employee, Department


class AttendanceListView(LoginRequiredMixin, ListView):
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


class AttendanceCreateView(LoginRequiredMixin, CreateView):
    model = AttendanceRecord
    form_class = AttendanceRecordForm
    template_name = 'attendance/attendance_form.html'
    success_url = reverse_lazy('attendance:attendance_list')

    def form_valid(self, form):
        messages.success(self.request, 'Ghi nhận chấm công thành công!')
        return super().form_valid(form)


class AttendanceUpdateView(LoginRequiredMixin, UpdateView):
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
        status = self.request.GET.get('status', '')
        dept = self.request.GET.get('department', '')
        if status:
            qs = qs.filter(status=status)
        if dept:
            qs = qs.filter(employee__department_id=dept)
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

    def form_valid(self, form):
        # Try to link to requesting user's employee profile
        try:
            form.instance.employee = self.request.user.employee_profile
        except Exception:
            pass
        messages.success(self.request, 'Gửi đơn nghỉ phép thành công!')
        return super().form_valid(form)


def approve_leave(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            leave.status = 'approved'
            leave.approved_by = request.user
            leave.save()
            messages.success(request, 'Đã duyệt đơn nghỉ phép.')
        elif action == 'reject':
            leave.status = 'rejected'
            leave.approved_by = request.user
            leave.save()
            messages.warning(request, 'Đã từ chối đơn nghỉ phép.')
    return redirect('attendance:leave_request_list')


class WorkScheduleListView(LoginRequiredMixin, ListView):
    model = WorkSchedule
    template_name = 'attendance/work_schedule_list.html'
    context_object_name = 'schedules'


class WorkScheduleCreateView(LoginRequiredMixin, CreateView):
    model = WorkSchedule
    form_class = WorkScheduleForm
    template_name = 'attendance/work_schedule_form.html'
    success_url = reverse_lazy('attendance:work_schedule_list')

    def form_valid(self, form):
        messages.success(self.request, 'Tạo ca làm việc thành công!')
        return super().form_valid(form)
