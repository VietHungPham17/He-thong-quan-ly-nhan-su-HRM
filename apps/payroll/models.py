from django.db import models
from apps.employees.models import Employee


class SalaryStructure(models.Model):
    name = models.CharField(max_length=100, verbose_name='Tên cấu trúc lương')
    basic_salary_percentage = models.DecimalField(
        max_digits=5, decimal_places=2,
        default=100, verbose_name='% lương cơ bản'
    )
    description = models.TextField(blank=True, verbose_name='Mô tả')

    class Meta:
        verbose_name = 'Cấu trúc lương'
        verbose_name_plural = 'Cấu trúc lương'

    def __str__(self):
        return self.name


class InsuranceRate(models.Model):
    name = models.CharField(max_length=100, verbose_name='Tên loại bảo hiểm')
    employee_rate = models.DecimalField(
        max_digits=5, decimal_places=2,
        verbose_name='Tỷ lệ NLĐ (%)'
    )
    employer_rate = models.DecimalField(
        max_digits=5, decimal_places=2,
        verbose_name='Tỷ lệ NSDLĐ (%)'
    )
    effective_from = models.DateField(verbose_name='Hiệu lực từ ngày')

    class Meta:
        verbose_name = 'Mức đóng bảo hiểm'
        verbose_name_plural = 'Mức đóng bảo hiểm'

    def __str__(self):
        return f'{self.name} (NLĐ: {self.employee_rate}%)'


class Payroll(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Nháp'),
        ('approved', 'Đã duyệt'),
        ('paid', 'Đã thanh toán'),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='payrolls',
        verbose_name='Nhân viên'
    )
    month = models.PositiveIntegerField(verbose_name='Tháng')
    year = models.PositiveIntegerField(verbose_name='Năm')
    basic_salary = models.DecimalField(
        max_digits=15, decimal_places=0,
        verbose_name='Lương cơ bản'
    )
    allowances_total = models.DecimalField(
        max_digits=15, decimal_places=0,
        default=0, verbose_name='Tổng phụ cấp'
    )
    deductions_total = models.DecimalField(
        max_digits=15, decimal_places=0,
        default=0, verbose_name='Tổng khấu trừ'
    )
    net_salary = models.DecimalField(
        max_digits=15, decimal_places=0,
        default=0, verbose_name='Lương thực lĩnh'
    )
    working_days = models.PositiveIntegerField(default=0, verbose_name='Ngày công chuẩn')
    actual_working_days = models.PositiveIntegerField(default=0, verbose_name='Ngày công thực tế')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='Trạng thái'
    )
    note = models.TextField(blank=True, verbose_name='Ghi chú')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Ngày cập nhật')

    class Meta:
        verbose_name = 'Bảng lương'
        verbose_name_plural = 'Bảng lương'
        unique_together = ['employee', 'month', 'year']
        ordering = ['-year', '-month']

    def __str__(self):
        return f'{self.employee.full_name} - {self.month}/{self.year}'

    def calculate_net(self):
        self.net_salary = self.basic_salary + self.allowances_total - self.deductions_total
        return self.net_salary


class AllowanceItem(models.Model):
    payroll = models.ForeignKey(
        Payroll,
        on_delete=models.CASCADE,
        related_name='allowance_items',
        verbose_name='Bảng lương'
    )
    name = models.CharField(max_length=100, verbose_name='Tên phụ cấp')
    amount = models.DecimalField(
        max_digits=15, decimal_places=0,
        verbose_name='Số tiền'
    )

    class Meta:
        verbose_name = 'Khoản phụ cấp'
        verbose_name_plural = 'Khoản phụ cấp'

    def __str__(self):
        return f'{self.name}: {self.amount:,}'


class DeductionItem(models.Model):
    payroll = models.ForeignKey(
        Payroll,
        on_delete=models.CASCADE,
        related_name='deduction_items',
        verbose_name='Bảng lương'
    )
    name = models.CharField(max_length=100, verbose_name='Tên khấu trừ')
    amount = models.DecimalField(
        max_digits=15, decimal_places=0,
        verbose_name='Số tiền'
    )

    class Meta:
        verbose_name = 'Khoản khấu trừ'
        verbose_name_plural = 'Khoản khấu trừ'

    def __str__(self):
        return f'{self.name}: {self.amount:,}'
