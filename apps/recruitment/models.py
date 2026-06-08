from django.db import models
from django.conf import settings
from apps.utils import format_vnd_amount
from apps.employees.models import Department, Position


class JobPosting(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Nháp'),
        ('open', 'Đang tuyển'),
        ('closed', 'Đã đóng'),
    ]

    title = models.CharField(max_length=200, verbose_name='Tiêu đề')
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='job_postings',
        verbose_name='Phòng ban'
    )
    position = models.ForeignKey(
        Position,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='job_postings',
        verbose_name='Chức vụ'
    )
    description = models.TextField(verbose_name='Mô tả công việc')
    requirements = models.TextField(blank=True, verbose_name='Yêu cầu')
    salary_range_min = models.DecimalField(
        max_digits=15, decimal_places=0,
        null=True, blank=True,
        verbose_name='Lương tối thiểu'
    )
    salary_range_max = models.DecimalField(
        max_digits=15, decimal_places=0,
        null=True, blank=True,
        verbose_name='Lương tối đa'
    )
    vacancies = models.PositiveIntegerField(default=1, verbose_name='Số lượng tuyển')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='Trạng thái'
    )
    deadline = models.DateField(null=True, blank=True, verbose_name='Hạn nộp')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name='Người tạo'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')

    class Meta:
        verbose_name = 'Tin tuyển dụng'
        verbose_name_plural = 'Tin tuyển dụng'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def candidate_count(self):
        return self.candidates.count()

    @property
    def salary_range(self):
        if self.salary_range_min and self.salary_range_max:
            return f'{format_vnd_amount(self.salary_range_min)} - {format_vnd_amount(self.salary_range_max)} VNĐ'
        return 'Thỏa thuận'


class Candidate(models.Model):
    STATUS_CHOICES = [
        ('new', 'Mới'),
        ('screening', 'Đang sàng lọc'),
        ('interview', 'Phỏng vấn'),
        ('offer', 'Đề nghị'),
        ('hired', 'Đã tuyển'),
        ('rejected', 'Từ chối'),
    ]

    SOURCE_CHOICES = [
        ('website', 'Website'),
        ('linkedin', 'LinkedIn'),
        ('referral', 'Giới thiệu'),
        ('agency', 'Agency'),
        ('other', 'Khác'),
    ]

    full_name = models.CharField(max_length=150, verbose_name='Họ và tên')
    email = models.EmailField(verbose_name='Email')
    phone = models.CharField(max_length=15, verbose_name='Số điện thoại')
    applied_position = models.ForeignKey(
        JobPosting,
        on_delete=models.CASCADE,
        related_name='candidates',
        verbose_name='Vị trí ứng tuyển'
    )
    cv_file = models.FileField(
        upload_to='cvs/',
        null=True, blank=True,
        verbose_name='CV'
    )
    cover_letter = models.TextField(blank=True, verbose_name='Thư xin việc')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name='Trạng thái'
    )
    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default='other',
        verbose_name='Nguồn'
    )
    note = models.TextField(blank=True, verbose_name='Ghi chú')
    applied_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày ứng tuyển')

    class Meta:
        verbose_name = 'Ứng viên'
        verbose_name_plural = 'Ứng viên'
        ordering = ['-applied_at']

    def __str__(self):
        return f'{self.full_name} - {self.applied_position.title}'


class Interview(models.Model):
    TYPE_CHOICES = [
        ('phone', 'Phỏng vấn điện thoại'),
        ('online', 'Phỏng vấn online'),
        ('in_person', 'Phỏng vấn trực tiếp'),
    ]

    STATUS_CHOICES = [
        ('scheduled', 'Đã lên lịch'),
        ('completed', 'Hoàn thành'),
        ('cancelled', 'Đã hủy'),
    ]

    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name='interviews',
        verbose_name='Ứng viên'
    )
    interviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='interviews',
        verbose_name='Người phỏng vấn'
    )
    scheduled_at = models.DateTimeField(verbose_name='Thời gian phỏng vấn')
    duration_minutes = models.PositiveIntegerField(
        default=60, verbose_name='Thời lượng (phút)'
    )
    interview_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='in_person',
        verbose_name='Hình thức'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled',
        verbose_name='Trạng thái'
    )
    feedback = models.TextField(blank=True, verbose_name='Nhận xét')
    rating = models.PositiveIntegerField(
        null=True, blank=True,
        choices=[(i, f'{i} sao') for i in range(1, 6)],
        verbose_name='Đánh giá (1-5)'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Phỏng vấn'
        verbose_name_plural = 'Phỏng vấn'
        ordering = ['-scheduled_at']

    def __str__(self):
        return f'{self.candidate.full_name} - {self.get_interview_type_display()} ({self.scheduled_at.strftime("%d/%m/%Y")})'
