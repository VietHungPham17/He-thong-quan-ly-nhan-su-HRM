from django.contrib import admin
from .models import Department, Position, Employee, Contract


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'manager', 'employee_count', 'created_at']
    search_fields = ['name', 'code']
    list_filter = ['created_at']


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'department', 'level', 'salary_grade']
    search_fields = ['name', 'code']
    list_filter = ['department', 'level']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'full_name', 'department', 'position', 'status', 'hire_date']
    search_fields = ['employee_id', 'full_name', 'email', 'phone']
    list_filter = ['department', 'status', 'employment_type', 'gender']
    readonly_fields = ['employee_id', 'created_at', 'updated_at']


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ['employee', 'contract_type', 'start_date', 'end_date', 'salary', 'status']
    search_fields = ['employee__full_name', 'employee__employee_id']
    list_filter = ['contract_type', 'status']
