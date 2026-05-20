from django import forms
from .models import JobPosting, Candidate, Interview


class JobPostingForm(forms.ModelForm):
    class Meta:
        model = JobPosting
        fields = [
            'title', 'department', 'position', 'description', 'requirements',
            'salary_range_min', 'salary_range_max', 'vacancies', 'status', 'deadline'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'position': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'salary_range_min': forms.NumberInput(attrs={'class': 'form-control'}),
            'salary_range_max': forms.NumberInput(attrs={'class': 'form-control'}),
            'vacancies': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        labels = {
            'title': 'Tiêu đề',
            'department': 'Phòng ban',
            'position': 'Chức vụ',
            'description': 'Mô tả công việc',
            'requirements': 'Yêu cầu',
            'salary_range_min': 'Lương tối thiểu',
            'salary_range_max': 'Lương tối đa',
            'vacancies': 'Số lượng tuyển',
            'status': 'Trạng thái',
            'deadline': 'Hạn nộp',
        }


class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = [
            'full_name', 'email', 'phone', 'applied_position',
            'cv_file', 'cover_letter', 'status', 'source', 'note'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'applied_position': forms.Select(attrs={'class': 'form-select'}),
            'cv_file': forms.FileInput(attrs={'class': 'form-control'}),
            'cover_letter': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'source': forms.Select(attrs={'class': 'form-select'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        labels = {
            'full_name': 'Họ và tên',
            'email': 'Email',
            'phone': 'Số điện thoại',
            'applied_position': 'Vị trí ứng tuyển',
            'cv_file': 'CV (file)',
            'cover_letter': 'Thư xin việc',
            'status': 'Trạng thái',
            'source': 'Nguồn',
            'note': 'Ghi chú',
        }


class InterviewForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = [
            'candidate', 'interviewer', 'scheduled_at', 'duration_minutes',
            'interview_type', 'status', 'feedback', 'rating'
        ]
        widgets = {
            'candidate': forms.Select(attrs={'class': 'form-select'}),
            'interviewer': forms.Select(attrs={'class': 'form-select'}),
            'scheduled_at': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'}
            ),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'interview_type': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'feedback': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'rating': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'candidate': 'Ứng viên',
            'interviewer': 'Người phỏng vấn',
            'scheduled_at': 'Thời gian',
            'duration_minutes': 'Thời lượng (phút)',
            'interview_type': 'Hình thức',
            'status': 'Trạng thái',
            'feedback': 'Nhận xét',
            'rating': 'Đánh giá',
        }
