from django.contrib import admin
from .models import SalaryStructure, InsuranceRate, Payroll, AllowanceItem, DeductionItem


@admin.register(SalaryStructure)
class SalaryStructureAdmin(admin.ModelAdmin):
    list_display = ['name', 'basic_salary_percentage']


@admin.register(InsuranceRate)
class InsuranceRateAdmin(admin.ModelAdmin):
    list_display = ['name', 'employee_rate', 'employer_rate', 'effective_from']


class AllowanceItemInline(admin.TabularInline):
    model = AllowanceItem
    extra = 0


class DeductionItemInline(admin.TabularInline):
    model = DeductionItem
    extra = 0


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ['employee', 'month', 'year', 'basic_salary', 'net_salary', 'status']
    list_filter = ['status', 'month', 'year']
    search_fields = ['employee__full_name', 'employee__employee_id']
    inlines = [AllowanceItemInline, DeductionItemInline]
    readonly_fields = ['net_salary', 'created_at', 'updated_at']
