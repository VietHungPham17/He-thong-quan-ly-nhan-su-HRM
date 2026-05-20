from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q, Count
from django.urls import reverse_lazy
from django.views.generic import (
    TemplateView, ListView, DetailView,
    CreateView, UpdateView, DeleteView
)
from django.utils import timezone
from .models import Department, Position, Employee, Contract
from .forms import DepartmentForm, PositionForm, EmployeeForm, ContractForm


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'employees/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        now = timezone.now()
        ctx['total_employees'] = Employee.objects.filter(status='active').count()
        ctx['new_this_month'] = Employee.objects.filter(
            hire_date__year=now.year,
            hire_date__month=now.month
        ).count()
        ctx['departments'] = Department.objects.annotate(
            emp_count=Count('employees', filter=Q(employees__status='active'))
        )[:5]
        ctx['recent_employees'] = Employee.objects.select_related(
            'department', 'position'
        ).order_by('-created_at')[:5]

        try:
            from apps.attendance.models import LeaveRequest
            ctx['pending_leaves'] = LeaveRequest.objects.filter(status='pending').count()
        except Exception:
            ctx['pending_leaves'] = 0

        try:
            from apps.payroll.models import Payroll
            ctx['payroll_this_month'] = Payroll.objects.filter(
                month=now.month, year=now.year
            ).count()
        except Exception:
            ctx['payroll_this_month'] = 0

        return ctx


# ── Department Views ──────────────────────────────────────────────────────────

class DepartmentListView(LoginRequiredMixin, ListView):
    model = Department
    template_name = 'employees/department_list.html'
    context_object_name = 'departments'
    paginate_by = 10

    def get_queryset(self):
        qs = Department.objects.annotate(
            emp_count=Count('employees', filter=Q(employees__status='active'))
        ).select_related('manager')
        q = self.request.GET.get('q', '')
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(code__icontains=q))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q'] = self.request.GET.get('q', '')
        return ctx


class DepartmentCreateView(LoginRequiredMixin, CreateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'employees/department_form.html'
    success_url = reverse_lazy('employees:department_list')

    def form_valid(self, form):
        messages.success(self.request, 'Tạo phòng ban thành công!')
        return super().form_valid(form)


class DepartmentUpdateView(LoginRequiredMixin, UpdateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'employees/department_form.html'
    success_url = reverse_lazy('employees:department_list')

    def form_valid(self, form):
        messages.success(self.request, 'Cập nhật phòng ban thành công!')
        return super().form_valid(form)


class DepartmentDeleteView(LoginRequiredMixin, DeleteView):
    model = Department
    template_name = 'employees/department_confirm_delete.html'
    success_url = reverse_lazy('employees:department_list')

    def form_valid(self, form):
        messages.success(self.request, 'Xóa phòng ban thành công!')
        return super().form_valid(form)


# ── Position Views ────────────────────────────────────────────────────────────

class PositionListView(LoginRequiredMixin, ListView):
    model = Position
    template_name = 'employees/position_list.html'
    context_object_name = 'positions'
    paginate_by = 10

    def get_queryset(self):
        qs = Position.objects.select_related('department')
        dept = self.request.GET.get('department', '')
        if dept:
            qs = qs.filter(department_id=dept)
        q = self.request.GET.get('q', '')
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(code__icontains=q))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['departments'] = Department.objects.all()
        ctx['q'] = self.request.GET.get('q', '')
        ctx['selected_dept'] = self.request.GET.get('department', '')
        return ctx


class PositionCreateView(LoginRequiredMixin, CreateView):
    model = Position
    form_class = PositionForm
    template_name = 'employees/position_form.html'
    success_url = reverse_lazy('employees:position_list')

    def form_valid(self, form):
        messages.success(self.request, 'Tạo chức vụ thành công!')
        return super().form_valid(form)


class PositionUpdateView(LoginRequiredMixin, UpdateView):
    model = Position
    form_class = PositionForm
    template_name = 'employees/position_form.html'
    success_url = reverse_lazy('employees:position_list')

    def form_valid(self, form):
        messages.success(self.request, 'Cập nhật chức vụ thành công!')
        return super().form_valid(form)


class PositionDeleteView(LoginRequiredMixin, DeleteView):
    model = Position
    template_name = 'employees/position_confirm_delete.html'
    success_url = reverse_lazy('employees:position_list')

    def form_valid(self, form):
        messages.success(self.request, 'Xóa chức vụ thành công!')
        return super().form_valid(form)


# ── Employee Views ────────────────────────────────────────────────────────────

class EmployeeListView(LoginRequiredMixin, ListView):
    model = Employee
    template_name = 'employees/employee_list.html'
    context_object_name = 'employees'
    paginate_by = 15

    def get_queryset(self):
        qs = Employee.objects.select_related('department', 'position', 'user')
        q = self.request.GET.get('q', '')
        dept = self.request.GET.get('department', '')
        status = self.request.GET.get('status', '')

        if q:
            qs = qs.filter(
                Q(full_name__icontains=q) |
                Q(employee_id__icontains=q) |
                Q(email__icontains=q) |
                Q(phone__icontains=q)
            )
        if dept:
            qs = qs.filter(department_id=dept)
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['departments'] = Department.objects.all()
        ctx['status_choices'] = Employee.STATUS_CHOICES
        ctx['q'] = self.request.GET.get('q', '')
        ctx['selected_dept'] = self.request.GET.get('department', '')
        ctx['selected_status'] = self.request.GET.get('status', '')
        return ctx


class EmployeeDetailView(LoginRequiredMixin, DetailView):
    model = Employee
    template_name = 'employees/employee_detail.html'
    context_object_name = 'employee'

    def get_queryset(self):
        return Employee.objects.select_related('department', 'position', 'user')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['contracts'] = self.object.contracts.order_by('-start_date')
        return ctx


class EmployeeCreateView(LoginRequiredMixin, CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'employees/employee_form.html'
    success_url = reverse_lazy('employees:employee_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Thêm nhân viên mới'
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Thêm nhân viên thành công!')
        return super().form_valid(form)


class EmployeeUpdateView(LoginRequiredMixin, UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'employees/employee_form.html'

    def get_success_url(self):
        return reverse_lazy('employees:employee_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = f'Cập nhật: {self.object.full_name}'
        return ctx

    def form_valid(self, form):
        messages.success(self.request, 'Cập nhật nhân viên thành công!')
        return super().form_valid(form)


class EmployeeDeleteView(LoginRequiredMixin, DeleteView):
    model = Employee
    template_name = 'employees/employee_confirm_delete.html'
    success_url = reverse_lazy('employees:employee_list')

    def form_valid(self, form):
        messages.success(self.request, 'Xóa nhân viên thành công!')
        return super().form_valid(form)


# ── Contract Views ────────────────────────────────────────────────────────────

class ContractCreateView(LoginRequiredMixin, CreateView):
    model = Contract
    form_class = ContractForm
    template_name = 'employees/contract_form.html'

    def get_employee(self):
        return Employee.objects.get(pk=self.kwargs['employee_pk'])

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['employee'] = self.get_employee()
        return ctx

    def form_valid(self, form):
        employee = self.get_employee()
        form.instance.employee = employee
        messages.success(self.request, 'Thêm hợp đồng thành công!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('employees:employee_detail', kwargs={'pk': self.kwargs['employee_pk']})
