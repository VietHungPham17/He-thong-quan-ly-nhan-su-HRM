from django import forms
from .models import AttendanceRecord, LeaveRequest, WorkSchedule, LeaveType


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


class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['leave_type', 'start_date', 'end_date', 'days_count', 'reason']
        widgets = {
            'leave_type': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'days_count': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'leave_type': 'Loại nghỉ phép',
            'start_date': 'Từ ngày',
            'end_date': 'Đến ngày',
            'days_count': 'Số ngày',
            'reason': 'Lý do',
        }


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
