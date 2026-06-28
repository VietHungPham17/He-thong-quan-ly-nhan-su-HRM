from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_ADMIN = 'admin'
    ROLE_HR = 'hr'
    ROLE_MANAGER = 'manager'
    ROLE_EMPLOYEE = 'employee'

    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Quản trị viên'),
        (ROLE_HR, 'HR'),
        (ROLE_MANAGER, 'Quản lý'),
        (ROLE_EMPLOYEE, 'Nhân viên'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_EMPLOYEE,
        verbose_name='Vai trò'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        verbose_name='Ảnh đại diện'
    )
    phone = models.CharField(
        max_length=15,
        blank=True,
        verbose_name='Số điện thoại'
    )

    class Meta:
        verbose_name = 'Người dùng'
        verbose_name_plural = 'Người dùng'

    def __str__(self):
        return f'{self.get_full_name() or self.username} ({self.get_role_display()})'

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN

    @property
    def is_hr(self):
        return self.role == self.ROLE_HR

    @property
    def is_manager(self):
        return self.role == self.ROLE_MANAGER

    @property
    def can_manage(self):
        return self.role in [self.ROLE_ADMIN, self.ROLE_HR, self.ROLE_MANAGER]
