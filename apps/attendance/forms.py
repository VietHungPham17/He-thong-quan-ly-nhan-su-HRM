import re
from datetime import date, timedelta

from django import forms
from django.core.exceptions import ValidationError

from .models import AttendanceRecord, LeaveRequest, WorkSchedule, LeaveType


# ─── AttendanceRecordForm ──────────────────────────────────────────────────────

class AttendanceRecordForm(forms.ModelForm):
    class Meta:
        model = AttendanceRecord
        fields = ['employee', 'date', 'check_in', 'check_out', 'status', 'note']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'check_in': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'check_out': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        labels = {
            'employee': 'Nhân viên',
            'date': 'Ngày',
            'check_in': 'Giờ vào',
            'check_out': 'Giờ ra',
            'status': 'Trạng thái',
            'note': 'Ghi chú',
        }

    def clean_date(self):
        record_date = self.cleaned_data.get('date')
        if record_date and record_date > date.today():
            raise ValidationError('Ngày chấm công không được là ngày trong tương lai.')
        return record_date

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in')
        check_out = cleaned_data.get('check_out')

        if check_in and check_out:
            if check_out <= check_in:
                self.add_error('check_out', 'Giờ ra phải sau giờ vào.')

        return cleaned_data


# ─── LeaveRequestForm ─────────────────────────────────────────────────────────

class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['leave_type', 'start_date', 'end_date', 'days_count', 'reason']
        widgets = {
            'leave_type': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'id_start_date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'id': 'id_end_date'}),
            'days_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'id': 'id_days_count',
                'readonly': True,
                'step': '0.5',
            }),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'leave_type': 'Loại nghỉ phép',
            'start_date': 'Từ ngày',
            'end_date': 'Đến ngày',
            'days_count': 'Số ngày',
            'reason': 'Lý do',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['days_count'].required = False

    def clean_start_date(self):
        start_date = self.cleaned_data.get('start_date')
        if start_date:
            # Không cho phép đăng ký nghỉ cho ngày đã qua quá 30 ngày
            if start_date < date.today() - timedelta(days=30):
                raise ValidationError(
                    'Ngày bắt đầu nghỉ phép không được sớm hơn 30 ngày so với hôm nay.'
                )
        return start_date

    def clean_reason(self):
        reason = self.cleaned_data.get('reason', '').strip()
        if not reason:
            raise ValidationError('Lý do nghỉ phép không được để trống.')
        if len(reason) < 10:
            raise ValidationError('Lý do nghỉ phép phải có ít nhất 10 ký tự.')
        return reason

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_date')
        end = cleaned_data.get('end_date')

        if start and end:
            if end < start:
                self.add_error('end_date', 'Ngày kết thúc không được trước ngày bắt đầu.')
            else:
                days = (end - start).days + 1
                cleaned_data['days_count'] = days
                if days <= 0:
                    self.add_error('days_count', 'Số ngày nghỉ phải lớn hơn 0.')
                if days > 365:
                    self.add_error('end_date', 'Thời gian nghỉ phép không được vượt quá 365 ngày.')

        return cleaned_data


# ─── WorkScheduleForm ─────────────────────────────────────────────────────────

class WorkScheduleForm(forms.ModelForm):
    class Meta:
        model = WorkSchedule
        fields = [
            'name', 'monday', 'tuesday', 'wednesday', 'thursday',
            'friday', 'saturday', 'sunday', 'start_time', 'end_time',
            'break_duration_minutes'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'break_duration_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Tên ca',
            'monday': 'Thứ 2',
            'tuesday': 'Thứ 3',
            'wednesday': 'Thứ 4',
            'thursday': 'Thứ 5',
            'friday': 'Thứ 6',
            'saturday': 'Thứ 7',
            'sunday': 'Chủ nhật',
            'start_time': 'Giờ bắt đầu',
            'end_time': 'Giờ kết thúc',
            'break_duration_minutes': 'Nghỉ giữa ca (phút)',
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise ValidationError('Tên ca làm việc không được để trống.')
        return name

    def clean_break_duration_minutes(self):
        mins = self.cleaned_data.get('break_duration_minutes')
        if mins is not None:
            if mins < 0:
                raise ValidationError('Thời gian nghỉ giữa ca không được là số âm.')
            if mins > 240:
                raise ValidationError('Thời gian nghỉ giữa ca không được vượt quá 240 phút.')
        return mins

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time:
            if end_time <= start_time:
                self.add_error('end_time', 'Giờ kết thúc phải sau giờ bắt đầu.')

        # Kiểm tra ít nhất 1 ngày làm việc được chọn
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        if not any(cleaned_data.get(day) for day in days):
            raise ValidationError('Ca làm việc phải có ít nhất một ngày làm việc được chọn.')

        return cleaned_data
