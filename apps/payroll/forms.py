from django import forms
from .models import Payroll


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
