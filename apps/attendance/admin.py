from django.contrib import admin
from .models import WorkSchedule, AttendanceRecord, LeaveType, LeaveBalance, LeaveRequest


@admin.register(WorkSchedule)
class WorkScheduleAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_time', 'end_time', 'break_duration_minutes']


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'check_in', 'check_out', 'status', 'work_hours']
    list_filter = ['status', 'date']
    search_fields = ['employee__full_name', 'employee__employee_id']
    date_hierarchy = 'date'


@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'days_per_year', 'is_paid']


@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'year', 'allocated_days', 'used_days']
    list_filter = ['year', 'leave_type']


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'start_date', 'end_date', 'days_count', 'status']
    list_filter = ['status', 'leave_type']
    search_fields = ['employee__full_name']
