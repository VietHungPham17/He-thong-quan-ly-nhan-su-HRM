"""
Unit Tests cho HRM System — Form Validation
============================================
Chạy bằng lệnh: python manage.py test apps.employees.tests -v 2
"""

from datetime import date, timedelta

from django.test import TestCase
from django.contrib.auth import get_user_model

from apps.employees.models import Department, Position
from apps.employees.forms import (
    DepartmentForm,
    PositionForm,
    EmployeeForm,
)
from apps.accounts.forms import ProfileForm

User = get_user_model()


# ══════════════════════════════════════════════════════════════════════════════
# 1. TEST DepartmentForm
# ══════════════════════════════════════════════════════════════════════════════

class DepartmentFormTest(TestCase):
    """Kiểm thử form tạo/sửa Phòng ban."""

    def _valid_data(self):
        return {'name': 'Phòng Kỹ thuật', 'code': 'KT', 'description': ''}

    # --- Trường hợp HỢP LỆ ---

    def test_valid_form_passes(self):
        """Form với dữ liệu hợp lệ phải pass."""
        form = DepartmentForm(data=self._valid_data())
        self.assertTrue(form.is_valid(), msg=form.errors)

    def test_code_auto_uppercased(self):
        """Mã phòng ban được tự động chuyển thành chữ hoa."""
        data = self._valid_data()
        data['code'] = 'kt'
        form = DepartmentForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['code'], 'KT')

    # --- Trường hợp KHÔNG HỢP LỆ ---

    def test_name_empty_is_invalid(self):
        """Tên phòng ban không được để trống."""
        data = self._valid_data()
        data['name'] = ''
        form = DepartmentForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_name_too_short_is_invalid(self):
        """Tên phòng ban phải có ít nhất 2 ký tự."""
        data = self._valid_data()
        data['name'] = 'A'
        form = DepartmentForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_code_empty_is_invalid(self):
        """Mã phòng ban không được để trống."""
        data = self._valid_data()
        data['code'] = ''
        form = DepartmentForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('code', form.errors)

    def test_code_with_special_chars_is_invalid(self):
        """Mã phòng ban không được chứa ký tự đặc biệt."""
        data = self._valid_data()
        data['code'] = 'KT@#!'
        form = DepartmentForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('code', form.errors)

    def test_duplicate_code_is_invalid(self):
        """Mã phòng ban không được trùng với bản ghi khác."""
        Department.objects.create(name='Nhân sự', code='HR')
        data = {'name': 'Phòng Khác', 'code': 'HR', 'description': ''}
        form = DepartmentForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('code', form.errors)


# ══════════════════════════════════════════════════════════════════════════════
# 2. TEST EmployeeForm — validation họ tên, ngày sinh, số điện thoại
# ══════════════════════════════════════════════════════════════════════════════

class EmployeeFormValidationTest(TestCase):
    """Kiểm thử validation các trường cơ bản của EmployeeForm."""

    def setUp(self):
        """Tạo dữ liệu phòng ban và chức vụ cần thiết cho form."""
        self.dept = Department.objects.create(name='IT', code='IT')
        self.pos = Position.objects.create(
            name='Nhân viên IT', code='IT-1',
            department=self.dept, level='junior',
        )

    def _base_data(self):
        return {
            'full_name':      'Nguyễn Văn An',
            'gender':         'male',
            'dob':            str(date.today() - timedelta(days=365 * 25)),
            'phone':          '0901234567',
            'email':          'an@hrm.com',
            'address':        'Hà Nội',
            'id_number':      '012345678901',
            'department':     self.dept.pk,
            'position':       self.pos.pk,
            'hire_date':      str(date.today()),
            'employment_type': 'full_time',
            'status':         'active',
            'emergency_contact_name':  'Mẹ',
            'emergency_contact_phone': '0901111111',
            'bank_account':   '1234567890',
            'bank_name':      'Vietcombank',
        }

    # --- Trường hợp HỢP LỆ ---

    def test_valid_employee_form(self):
        """Form nhân viên với đầy đủ dữ liệu hợp lệ phải pass."""
        form = EmployeeForm(data=self._base_data())
        self.assertTrue(form.is_valid(), msg=form.errors)

    # --- Họ tên ---

    def test_full_name_empty_is_invalid(self):
        """Họ và tên không được để trống."""
        data = self._base_data()
        data['full_name'] = ''
        form = EmployeeForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('full_name', form.errors)

    def test_full_name_with_numbers_is_invalid(self):
        """Họ và tên không được chứa số."""
        data = self._base_data()
        data['full_name'] = 'Nguyễn Văn 4n'
        form = EmployeeForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('full_name', form.errors)

    def test_full_name_with_special_chars_is_invalid(self):
        """Họ và tên không được chứa ký tự đặc biệt."""
        data = self._base_data()
        data['full_name'] = 'Nguyễn@Văn'
        form = EmployeeForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('full_name', form.errors)

    # --- Ngày sinh ---

    def test_dob_in_future_is_invalid(self):
        """Ngày sinh không được là ngày trong tương lai."""
        data = self._base_data()
        data['dob'] = str(date.today() + timedelta(days=1))
        form = EmployeeForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('dob', form.errors)

    def test_dob_under_15_is_invalid(self):
        """Nhân viên phải đủ 15 tuổi trở lên."""
        data = self._base_data()
        data['dob'] = str(date.today() - timedelta(days=365 * 14))
        form = EmployeeForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('dob', form.errors)

    # --- Số điện thoại ---

    def test_invalid_phone_format(self):
        """Số điện thoại sai định dạng Việt Nam bị từ chối."""
        data = self._base_data()
        data['phone'] = '12345'
        form = EmployeeForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('phone', form.errors)

    def test_valid_phone_with_country_code(self):
        """Số điện thoại dạng +84 vẫn hợp lệ."""
        data = self._base_data()
        data['phone'] = '+84901234567'
        form = EmployeeForm(data=data)
        self.assertTrue(form.is_valid(), msg=form.errors)


# ══════════════════════════════════════════════════════════════════════════════
# 3. TEST ProfileForm — validation họ, tên và email
# ══════════════════════════════════════════════════════════════════════════════

class ProfileFormTest(TestCase):
    """Kiểm thử form cập nhật hồ sơ cá nhân."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='pass123', email='test@hrm.com'
        )

    def _valid_data(self):
        return {
            'first_name': 'An',
            'last_name':  'Nguyễn',
            'email':      'an.updated@hrm.com',
            'phone':      '0901234567',
        }

    def test_valid_profile_form(self):
        """Form profile hợp lệ phải pass."""
        form = ProfileForm(data=self._valid_data(), instance=self.user)
        self.assertTrue(form.is_valid(), msg=form.errors)

    def test_first_name_with_numbers_is_invalid(self):
        """Tên không được chứa số."""
        data = self._valid_data()
        data['first_name'] = 'An123'
        form = ProfileForm(data=data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('first_name', form.errors)

    def test_last_name_with_special_chars_is_invalid(self):
        """Họ không được chứa ký tự đặc biệt."""
        data = self._valid_data()
        data['last_name'] = 'Nguyễn@'
        form = ProfileForm(data=data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('last_name', form.errors)

    def test_duplicate_email_is_invalid(self):
        """Email trùng với người dùng khác bị từ chối."""
        User.objects.create_user(
            username='other', password='pass', email='other@hrm.com'
        )
        data = self._valid_data()
        data['email'] = 'other@hrm.com'
        form = ProfileForm(data=data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_same_email_for_same_user_is_valid(self):
        """Cập nhật profile với chính email hiện tại của mình phải pass."""
        data = self._valid_data()
        data['email'] = self.user.email
        form = ProfileForm(data=data, instance=self.user)
        self.assertTrue(form.is_valid(), msg=form.errors)
