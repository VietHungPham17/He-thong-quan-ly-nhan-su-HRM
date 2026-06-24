import re
from datetime import date

from django import forms
from django.core.exceptions import ValidationError

from .models import Department, Position, Employee, Contract


# ─── Helpers ──────────────────────────────────────────────────────────────────

PHONE_VN_REGEX = re.compile(r'^(0|\+84)[0-9]{9,10}$')


def validate_phone_vn(value):
    """Kiểm tra định dạng số điện thoại Việt Nam."""
    if value and not PHONE_VN_REGEX.match(value.strip()):
        raise ValidationError(
            'Số điện thoại không hợp lệ. Vui lòng nhập đúng định dạng Việt Nam (vd: 0901234567).'
        )


# ─── DepartmentForm ────────────────────────────────────────────────────────────

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

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise ValidationError('Tên phòng ban không được để trống.')
        if len(name) < 2:
            raise ValidationError('Tên phòng ban phải có ít nhất 2 ký tự.')
        return name

    def clean_code(self):
        code = self.cleaned_data.get('code', '').strip().upper()
        if not code:
            raise ValidationError('Mã phòng ban không được để trống.')
        if not re.match(r'^[A-Z0-9_]{2,20}$', code):
            raise ValidationError(
                'Mã phòng ban chỉ được chứa chữ in hoa, số và dấu gạch dưới (2–20 ký tự).'
            )
        # Unique check (bỏ qua bản ghi hiện tại khi cập nhật)
        qs = Department.objects.filter(code=code)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError(f'Mã phòng ban "{code}" đã tồn tại.')
        return code


# ─── PositionForm ──────────────────────────────────────────────────────────────

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

    def clean_code(self):
        code = self.cleaned_data.get('code', '').strip().upper()
        if not code:
            raise ValidationError('Mã chức vụ không được để trống.')
        if not re.match(r'^[A-Z0-9_]{2,20}$', code):
            raise ValidationError(
                'Mã chức vụ chỉ được chứa chữ in hoa, số và dấu gạch dưới (2–20 ký tự).'
            )
        qs = Position.objects.filter(code=code)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError(f'Mã chức vụ "{code}" đã tồn tại.')
        return code

    def clean_salary_grade(self):
        grade = self.cleaned_data.get('salary_grade', '').strip()
        if grade:
            try:
                val = float(grade)
                if val <= 0:
                    raise ValidationError('Hệ số lương phải là số dương (> 0).')
            except ValueError:
                raise ValidationError('Hệ số lương phải là một con số hợp lệ (vd: 1.5, 2.0).')
        return grade


# ─── EmployeeForm ──────────────────────────────────────────────────────────────

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

    def clean_full_name(self):
        name = self.cleaned_data.get('full_name', '').strip()
        if not name:
            raise ValidationError('Họ và tên không được để trống.')
        if len(name) < 2:
            raise ValidationError('Họ và tên phải có ít nhất 2 ký tự.')
        # Không được chứa số hoặc ký tự đặc biệt (cho phép chữ có dấu, khoảng trắng và dấu gạch ngang)
        if re.search(r'[0-9!@#$%^&*()_+=\[\]{};:\'",.<>?/\\|`~]', name):
            raise ValidationError('Họ và tên không được chứa số hoặc ký tự đặc biệt.')
        return name

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if phone:
            validate_phone_vn(phone)
        return phone

    def clean_dob(self):
        dob = self.cleaned_data.get('dob')
        if dob:
            today = date.today()
            if dob >= today:
                raise ValidationError('Ngày sinh phải là ngày trong quá khứ.')
            age = (today - dob).days // 365
            if age < 15:
                raise ValidationError('Nhân viên phải đủ 15 tuổi trở lên.')
            if age > 80:
                raise ValidationError('Ngày sinh không hợp lệ (tuổi không được vượt quá 80).')
        return dob

    def clean_id_number(self):
        id_num = self.cleaned_data.get('id_number', '').strip()
        if id_num:
            if not re.match(r'^\d{9}$|^\d{12}$', id_num):
                raise ValidationError(
                    'CCCD/CMND không hợp lệ. Vui lòng nhập 9 chữ số (CMND cũ) hoặc 12 chữ số (CCCD mới).'
                )
        return id_num

    def clean_emergency_contact_phone(self):
        phone = self.cleaned_data.get('emergency_contact_phone', '').strip()
        if phone:
            validate_phone_vn(phone)
        return phone

    def clean_bank_account(self):
        account = self.cleaned_data.get('bank_account', '').strip()
        if account:
            if not re.match(r'^\d{6,20}$', account):
                raise ValidationError('Số tài khoản ngân hàng chỉ được chứa chữ số (6–20 chữ số).')
        return account

    def clean(self):
        cleaned_data = super().clean()
        dob = cleaned_data.get('dob')
        hire_date = cleaned_data.get('hire_date')

        if dob and hire_date:
            if hire_date <= dob:
                self.add_error('hire_date', 'Ngày vào làm phải sau ngày sinh.')
            age_at_hire = (hire_date - dob).days // 365
            if age_at_hire < 15:
                self.add_error('hire_date', 'Nhân viên phải đủ 15 tuổi vào ngày vào làm.')

        return cleaned_data


# ─── ContractForm ──────────────────────────────────────────────────────────────

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

    def clean_salary(self):
        salary = self.cleaned_data.get('salary')
        if salary is not None and salary <= 0:
            raise ValidationError('Lương cơ bản phải lớn hơn 0.')
        return salary

    def clean(self):
        cleaned_data = super().clean()
        contract_type = cleaned_data.get('contract_type')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        signed_date = cleaned_data.get('signed_date')

        # Hợp đồng có thời hạn bắt buộc phải có ngày kết thúc
        if contract_type in ('probation', 'fixed_term', 'part_time') and not end_date:
            self.add_error('end_date', 'Loại hợp đồng này bắt buộc phải có ngày kết thúc.')

        if start_date and end_date:
            if end_date <= start_date:
                self.add_error('end_date', 'Ngày kết thúc phải sau ngày bắt đầu.')

        if signed_date and start_date:
            if signed_date > start_date:
                self.add_error('signed_date', 'Ngày ký không được sau ngày bắt đầu hợp đồng.')

        return cleaned_data
