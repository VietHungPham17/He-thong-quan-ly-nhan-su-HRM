from django import forms
from .models import Department, Position, Employee, Contract


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'code', 'description', 'manager']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'manager': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'name': 'Tên phòng ban',
            'code': 'Mã phòng ban',
            'description': 'Mô tả',
            'manager': 'Trưởng phòng',
        }


class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = ['name', 'code', 'department', 'level', 'salary_grade']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'level': forms.Select(attrs={'class': 'form-select'}),
            'salary_grade': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Tên chức vụ',
            'code': 'Mã chức vụ',
            'department': 'Phòng ban',
            'level': 'Cấp độ',
            'salary_grade': 'Hệ số lương',
        }


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'full_name', 'gender', 'dob', 'phone', 'email', 'address',
            'id_number', 'department', 'position', 'hire_date',
            'employment_type', 'status', 'avatar',
            'emergency_contact_name', 'emergency_contact_phone',
            'bank_account', 'bank_name'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'dob': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'id_number': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'position': forms.Select(attrs={'class': 'form-select'}),
            'hire_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'employment_type': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_account': forms.TextInput(attrs={'class': 'form-control'}),
            'bank_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'full_name': 'Họ và tên',
            'gender': 'Giới tính',
            'dob': 'Ngày sinh',
            'phone': 'Số điện thoại',
            'email': 'Email',
            'address': 'Địa chỉ',
            'id_number': 'CCCD/CMND',
            'department': 'Phòng ban',
            'position': 'Chức vụ',
            'hire_date': 'Ngày vào làm',
            'employment_type': 'Loại hình làm việc',
            'status': 'Trạng thái',
            'avatar': 'Ảnh đại diện',
            'emergency_contact_name': 'Người liên hệ khẩn cấp',
            'emergency_contact_phone': 'SĐT khẩn cấp',
            'bank_account': 'Số tài khoản',
            'bank_name': 'Tên ngân hàng',
        }


class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = ['contract_type', 'start_date', 'end_date', 'salary', 'signed_date', 'status']
        widgets = {
            'contract_type': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'salary': forms.NumberInput(attrs={'class': 'form-control'}),
            'signed_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'contract_type': 'Loại hợp đồng',
            'start_date': 'Ngày bắt đầu',
            'end_date': 'Ngày kết thúc',
            'salary': 'Lương cơ bản (VNĐ)',
            'signed_date': 'Ngày ký',
            'status': 'Trạng thái',
        }
