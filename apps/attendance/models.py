from django.db import models
from django.conf import settings
from apps.employees.models import Employee


class WorkSchedule(models.Model):
    name = models.CharField(max_length=100, verbose_name='Tên ca làm việc')
    monday = models.BooleanField(default=True, verbose_name='Thứ 2')
    tuesday = models.BooleanField(default=True, verbose_name='Thứ 3')
    wednesday = models.BooleanField(default=True, verbose_name='Thứ 4')
    thursday = models.BooleanField(default=True, verbose_name='Thứ 5')
    friday = models.BooleanField(default=True, verbose_name='Thứ 6')
    saturday = models.BooleanField(default=False, verbose_name='Thứ 7')
    sunday = models.BooleanField(default=False, verbose_name='Chủ nhật')
    start_time = models.TimeField(verbose_name='Giờ bắt đầu')
    end_time = models.TimeField(verbose_name='Giờ kết thúc')
    break_duration_minutes = models.PositiveIntegerField(
        default=60, verbose_name='Thời gian nghỉ (phút)'
    )

    class Meta:
        verbose_name = 'Ca làm việc'
        verbose_name_plural = 'Ca làm việc'

    def __str__(self):
        return self.name

    @property
    def work_days_display(self):
        days = []
        if self.monday: days.append('T2')
        if self.tuesday: days.append('T3')
        if self.wednesday: days.append('T4')
        if self.thursday: days.append('T5')
        if self.friday: days.append('T6')
        if self.saturday: days.append('T7')
        if self.sunday: days.append('CN')
        return ', '.join(days)


class AttendanceRecord(models.Model):
    STATUS_CHOICES = [
        ('present', 'Có mặt'),
        ('absent', 'Vắng mặt'),
        ('late', 'Đi muộn'),
        ('half_day', 'Nửa ngày'),
        ('leave', 'Nghỉ phép'),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='attendance_records',
        verbose_name='Nhân viên'
    )
    date = models.DateField(verbose_name='Ngày')
    check_in = models.TimeField(null=True, blank=True, verbose_name='Giờ vào')
    check_out = models.TimeField(null=True, blank=True, verbose_name='Giờ ra')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='present',
        verbose_name='Trạng thái'
    )
    work_hours = models.DecimalField(
        max_digits=4, decimal_places=2,
        default=0, verbose_name='Số giờ làm việc'
    )
    note = models.TextField(blank=True, verbose_name='Ghi chú')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Bản ghi chấm công'
        verbose_name_plural = 'Bản ghi chấm công'
        unique_together = ['employee', 'date']
        ordering = ['-date']

    def __str__(self):
        return f'{self.employee.full_name} - {self.date}'

    def save(self, *args, **kwargs):
        if self.check_in and self.check_out:
            from datetime import datetime, date
            dt_in = datetime.combine(date.today(), self.check_in)
            dt_out = datetime.combine(date.today(), self.check_out)
            diff = (dt_out - dt_in).total_seconds() / 3600
            self.work_hours = round(max(0, diff), 2)
        super().save(*args, **kwargs)


class LeaveType(models.Model):
    name = models.CharField(max_length=100, verbose_name='Loại nghỉ phép')
    days_per_year = models.PositiveIntegerField(
        default=12, verbose_name='Số ngày/năm'
    )
    is_paid = models.BooleanField(default=True, verbose_name='Có hưởng lương')

    class Meta:
        verbose_name = 'Loại nghỉ phép'
        verbose_name_plural = 'Loại nghỉ phép'

    def __str__(self):
        return self.name


class LeaveBalance(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='leave_balances',
        verbose_name='Nhân viên'
    )
    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.CASCADE,
        verbose_name='Loại nghỉ phép'
    )
    year = models.PositiveIntegerField(verbose_name='Năm')
    allocated_days = models.DecimalField(
        max_digits=5, decimal_places=1,
        default=0, verbose_name='Ngày được phân bổ'
    )
    used_days = models.DecimalField(
        max_digits=5, decimal_places=1,
        default=0, verbose_name='Ngày đã dùng'
    )

    class Meta:
        verbose_name = 'Số dư nghỉ phép'
        verbose_name_plural = 'Số dư nghỉ phép'
        unique_together = ['employee', 'leave_type', 'year']

    def __str__(self):
        return f'{self.employee.full_name} - {self.leave_type.name} ({self.year})'

    @property
    def remaining_days(self):
        return self.allocated_days - self.used_days


class LeaveRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Từ chối'),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='leave_requests',
        verbose_name='Nhân viên'
    )
    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.CASCADE,
        verbose_name='Loại nghỉ phép'
    )
    start_date = models.DateField(verbose_name='Từ ngày')
    end_date = models.DateField(verbose_name='Đến ngày')
    days_count = models.DecimalField(
        max_digits=5, decimal_places=1,
        verbose_name='Số ngày'
    )
    reason = models.TextField(verbose_name='Lý do')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Trạng thái'
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='approved_leaves',
        verbose_name='Người duyệt'
    )
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name='Ngày duyệt')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')

    class Meta:
        verbose_name = 'Đơn nghỉ phép'
        verbose_name_plural = 'Đơn nghỉ phép'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.employee.full_name} - {self.leave_type.name} ({self.start_date} ~ {self.end_date})'
