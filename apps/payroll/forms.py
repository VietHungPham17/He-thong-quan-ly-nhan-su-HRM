import re
from datetime import date

from django import forms
from django.core.exceptions import ValidationError

from .models import Payroll


# ─── PayrollForm ──────────────────────────────────────────────────────────────

class PayrollForm(forms.ModelForm):
    class Meta:
        model = Payroll
        fields = [
            'employee', 'month', 'year', 'basic_salary',
            'allowances_total', 'deductions_total',
            'working_days', 'actual_working_days', 'status', 'note'
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'month': forms.Select(
                choices=[(i, f'Tháng {i}') for i in range(1, 13)],
                attrs={'class': 'form-select'}
            ),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'basic_salary': forms.NumberInput(attrs={'class': 'form-control'}),
            'allowances_total': forms.NumberInput(attrs={'class': 'form-control'}),
            'deductions_total': forms.NumberInput(attrs={'class': 'form-control'}),
            'working_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'actual_working_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        labels = {
            'employee': 'Nhân viên',
            'month': 'Tháng',
            'year': 'Năm',
            'basic_salary': 'Lương cơ bản (VNĐ)',
            'allowances_total': 'Tổng phụ cấp (VNĐ)',
            'deductions_total': 'Tổng khấu trừ (VNĐ)',
            'working_days': 'Ngày công chuẩn',
            'actual_working_days': 'Ngày công thực tế',
            'status': 'Trạng thái',
            'note': 'Ghi chú',
        }

    def clean_year(self):
        year = self.cleaned_data.get('year')
        if year is not None:
            current_year = date.today().year
            if year < 2000:
                raise ValidationError('Năm không được nhỏ hơn 2000.')
            if year > current_year + 1:
                raise ValidationError(f'Năm không được vượt quá {current_year + 1}.')
        return year

    def clean_basic_salary(self):
        salary = self.cleaned_data.get('basic_salary')
        if salary is not None and salary <= 0:
            raise ValidationError('Lương cơ bản phải lớn hơn 0.')
        return salary

    def clean_allowances_total(self):
        allowances = self.cleaned_data.get('allowances_total')
        if allowances is not None and allowances < 0:
            raise ValidationError('Tổng phụ cấp không được là số âm.')
        return allowances

    def clean_deductions_total(self):
        deductions = self.cleaned_data.get('deductions_total')
        if deductions is not None and deductions < 0:
            raise ValidationError('Tổng khấu trừ không được là số âm.')
        return deductions

    def clean_working_days(self):
        days = self.cleaned_data.get('working_days')
        if days is not None:
            if days < 0:
                raise ValidationError('Ngày công chuẩn không được âm.')
            if days > 31:
                raise ValidationError('Ngày công chuẩn không được vượt quá 31 ngày.')
        return days

    def clean(self):
        cleaned_data = super().clean()
        working_days = cleaned_data.get('working_days')
        actual_working_days = cleaned_data.get('actual_working_days')

        if actual_working_days is not None and actual_working_days < 0:
            self.add_error('actual_working_days', 'Ngày công thực tế không được là số âm.')

        if working_days and actual_working_days is not None:
            if actual_working_days > working_days:
                self.add_error(
                    'actual_working_days',
                    f'Ngày công thực tế ({actual_working_days}) không được vượt quá ngày công chuẩn ({working_days}).'
                )

        return cleaned_data


# ─── GeneratePayrollForm ──────────────────────────────────────────────────────

class GeneratePayrollForm(forms.Form):
    month = forms.ChoiceField(
        choices=[(i, f'Tháng {i}') for i in range(1, 13)],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Tháng'
    )
    year = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label='Năm'
    )

    def clean_year(self):
        year = self.cleaned_data.get('year')
        if year is not None:
            current_year = date.today().year
            if year < 2000:
                raise ValidationError('Năm không được nhỏ hơn 2000.')
            if year > current_year + 1:
                raise ValidationError(f'Năm không được vượt quá {current_year + 1}.')
        return year
