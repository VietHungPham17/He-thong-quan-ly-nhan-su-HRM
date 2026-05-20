from django.db import models
from django.conf import settings


class Department(models.Model):
    name = models.CharField(max_length=100, verbose_name='Tên phòng ban')
    code = models.CharField(max_length=20, unique=True, verbose_name='Mã phòng ban')
    description = models.TextField(blank=True, verbose_name='Mô tả')
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='managed_departments',
        verbose_name='Trưởng phòng'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')

    class Meta:
        verbose_name = 'Phòng ban'
        verbose_name_plural = 'Phòng ban'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.code})'

    @property
    def employee_count(self):
        return self.employees.filter(status='active').count()


class Position(models.Model):
    LEVEL_CHOICES = [
        ('junior', 'Junior'),
        ('middle', 'Middle'),
        ('senior', 'Senior'),
        ('lead', 'Lead'),
        ('manager', 'Manager'),
        ('director', 'Director'),
    ]

    name = models.CharField(max_length=100, verbose_name='Tên chức vụ')
    code = models.CharField(max_length=20, unique=True, verbose_name='Mã chức vụ')
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='positions',
        verbose_name='Phòng ban'
    )
    level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES,
        default='junior',
        verbose_name='Cấp độ'
    )
    salary_grade = models.CharField(max_length=20, blank=True, verbose_name='Hệ số lương')

    class Meta:
        verbose_name = 'Chức vụ'
        verbose_name_plural = 'Chức vụ'
        ordering = ['department', 'name']

    def __str__(self):
        return f'{self.name} - {self.department.name}'


class Employee(models.Model):
    GENDER_CHOICES = [
        ('male', 'Nam'),
        ('female', 'Nữ'),
        ('other', 'Khác'),
    ]

    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', 'Toàn thời gian'),
        ('part_time', 'Bán thời gian'),
        ('contract', 'Hợp đồng'),
    ]

    STATUS_CHOICES = [
        ('active', 'Đang làm việc'),
        ('inactive', 'Tạm nghỉ'),
        ('resigned', 'Đã nghỉ việc'),
    ]

    employee_id = models.CharField(
        max_length=20, unique=True, blank=True,
        verbose_name='Mã nhân viên'
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='employee_profile',
        verbose_name='Tài khoản'
    )
    full_name = models.CharField(max_length=150, verbose_name='Họ và tên')
    gender = models.CharField(
        max_length=10, choices=GENDER_CHOICES,
        default='male', verbose_name='Giới tính'
    )
    dob = models.DateField(null=True, blank=True, verbose_name='Ngày sinh')
    phone = models.CharField(max_length=15, blank=True, verbose_name='Số điện thoại')
    email = models.EmailField(blank=True, verbose_name='Email')
    address = models.TextField(blank=True, verbose_name='Địa chỉ')
    id_number = models.CharField(max_length=20, blank=True, verbose_name='CCCD/CMND')
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='employees',
        verbose_name='Phòng ban'
    )
    position = models.ForeignKey(
        Position,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='employees',
        verbose_name='Chức vụ'
    )
    hire_date = models.DateField(null=True, blank=True, verbose_name='Ngày vào làm')
    employment_type = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_TYPE_CHOICES,
        default='full_time',
        verbose_name='Loại hình làm việc'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='Trạng thái'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True, blank=True,
        verbose_name='Ảnh đại diện'
    )
    emergency_contact_name = models.CharField(
        max_length=100, blank=True,
        verbose_name='Tên người liên hệ khẩn cấp'
    )
    emergency_contact_phone = models.CharField(
        max_length=15, blank=True,
        verbose_name='SĐT liên hệ khẩn cấp'
    )
    bank_account = models.CharField(max_length=30, blank=True, verbose_name='Số tài khoản')
    bank_name = models.CharField(max_length=100, blank=True, verbose_name='Ngân hàng')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Ngày cập nhật')

    class Meta:
        verbose_name = 'Nhân viên'
        verbose_name_plural = 'Nhân viên'
        ordering = ['employee_id']

    def __str__(self):
        return f'{self.employee_id} - {self.full_name}'

    def save(self, *args, **kwargs):
        if not self.employee_id:
            last = Employee.objects.order_by('id').last()
            if last and last.employee_id:
                try:
                    num = int(last.employee_id.replace('EMP', '')) + 1
                except ValueError:
                    num = 1
            else:
                num = 1
            self.employee_id = f'EMP{num:03d}'
        super().save(*args, **kwargs)

    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return None


class Contract(models.Model):
    CONTRACT_TYPE_CHOICES = [
        ('probation', 'Thử việc'),
        ('fixed_term', 'Có thời hạn'),
        ('indefinite', 'Không thời hạn'),
        ('part_time', 'Bán thời gian'),
    ]

    STATUS_CHOICES = [
        ('active', 'Đang hiệu lực'),
        ('expired', 'Hết hạn'),
        ('terminated', 'Đã chấm dứt'),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='contracts',
        verbose_name='Nhân viên'
    )
    contract_type = models.CharField(
        max_length=20,
        choices=CONTRACT_TYPE_CHOICES,
        verbose_name='Loại hợp đồng'
    )
    start_date = models.DateField(verbose_name='Ngày bắt đầu')
    end_date = models.DateField(null=True, blank=True, verbose_name='Ngày kết thúc')
    salary = models.DecimalField(
        max_digits=15, decimal_places=0,
        verbose_name='Lương cơ bản'
    )
    signed_date = models.DateField(null=True, blank=True, verbose_name='Ngày ký')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='Trạng thái'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')

    class Meta:
        verbose_name = 'Hợp đồng'
        verbose_name_plural = 'Hợp đồng'
        ordering = ['-start_date']

    def __str__(self):
        return f'HĐ {self.get_contract_type_display()} - {self.employee.full_name}'
