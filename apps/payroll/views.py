from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q, Sum
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, FormView
from django.utils import timezone
from .models import Payroll, AllowanceItem, DeductionItem
from .forms import PayrollForm, GeneratePayrollForm
from apps.employees.models import Employee


class PayrollListView(LoginRequiredMixin, ListView):
    model = Payroll
    template_name = 'payroll/payroll_list.html'
    context_object_name = 'payrolls'
    paginate_by = 20

    def get_queryset(self):
        qs = Payroll.objects.select_related('employee', 'employee__department')
        now = timezone.now()
        month = int(self.request.GET.get('month', now.month))
        year = int(self.request.GET.get('year', now.year))
        qs = qs.filter(month=month, year=year)

        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        now = timezone.now()
        month = int(self.request.GET.get('month', now.month))
        year = int(self.request.GET.get('year', now.year))
        ctx['month'] = month
        ctx['year'] = year
        ctx['years'] = range(now.year - 2, now.year + 2)
        ctx['months'] = range(1, 13)
        ctx['status_choices'] = Payroll.STATUS_CHOICES
        ctx['selected_status'] = self.request.GET.get('status', '')

        # Summary
        qs = self.get_queryset()
        ctx['total_net'] = qs.aggregate(s=Sum('net_salary'))['s'] or 0
        ctx['total_basic'] = qs.aggregate(s=Sum('basic_salary'))['s'] or 0
        return ctx


class PayrollDetailView(LoginRequiredMixin, DetailView):
    model = Payroll
    template_name = 'payroll/payslip.html'
    context_object_name = 'payroll'

    def get_queryset(self):
        return Payroll.objects.select_related(
            'employee', 'employee__department', 'employee__position'
        ).prefetch_related('allowance_items', 'deduction_items')


class PayrollCreateView(LoginRequiredMixin, CreateView):
    model = Payroll
    form_class = PayrollForm
    template_name = 'payroll/payroll_form.html'
    success_url = reverse_lazy('payroll:payroll_list')

    def form_valid(self, form):
        payroll = form.save(commit=False)
        payroll.net_salary = payroll.basic_salary + payroll.allowances_total - payroll.deductions_total
        payroll.save()
        messages.success(self.request, 'Tạo bảng lương thành công!')
        return super().form_valid(form)


class PayrollUpdateView(LoginRequiredMixin, UpdateView):
    model = Payroll
    form_class = PayrollForm
    template_name = 'payroll/payroll_form.html'

    def get_success_url(self):
        return reverse_lazy('payroll:payroll_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        payroll = form.save(commit=False)
        payroll.net_salary = payroll.basic_salary + payroll.allowances_total - payroll.deductions_total
        payroll.save()
        messages.success(self.request, 'Cập nhật bảng lương thành công!')
        return super().form_valid(form)


class GeneratePayrollView(LoginRequiredMixin, FormView):
    template_name = 'payroll/generate_payroll.html'
    form_class = GeneratePayrollForm
    success_url = reverse_lazy('payroll:payroll_list')

    def get_initial(self):
        now = timezone.now()
        return {'month': now.month, 'year': now.year}

    def form_valid(self, form):
        month = int(form.cleaned_data['month'])
        year = int(form.cleaned_data['year'])
        employees = Employee.objects.filter(status='active').select_related('contracts')
        created = 0
        skipped = 0
        for emp in employees:
            if Payroll.objects.filter(employee=emp, month=month, year=year).exists():
                skipped += 1
                continue
            # Get latest contract salary
            contract = emp.contracts.filter(status='active').order_by('-start_date').first()
            basic = contract.salary if contract else 0
            p = Payroll.objects.create(
                employee=emp,
                month=month,
                year=year,
                basic_salary=basic,
                allowances_total=0,
                deductions_total=0,
                net_salary=basic,
                status='draft'
            )
            created += 1
        messages.success(
            self.request,
            f'Đã tạo {created} phiếu lương tháng {month}/{year}. Bỏ qua {skipped} (đã tồn tại).'
        )
        return super().form_valid(form)
