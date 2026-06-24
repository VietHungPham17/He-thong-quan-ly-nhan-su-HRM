import re
from datetime import date
from datetime import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import JobPosting, Candidate, Interview


# ─── Helpers ──────────────────────────────────────────────────────────────────

PHONE_VN_REGEX = re.compile(r'^(0|\+84)[0-9]{9,10}$')
ALLOWED_CV_EXTENSIONS = ['.pdf', '.doc', '.docx']


# ─── JobPostingForm ────────────────────────────────────────────────────────────

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

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if not title:
            raise ValidationError('Tiêu đề tuyển dụng không được để trống.')
        if len(title) < 5:
            raise ValidationError('Tiêu đề phải có ít nhất 5 ký tự.')
        return title

    def clean_vacancies(self):
        vacancies = self.cleaned_data.get('vacancies')
        if vacancies is not None and vacancies < 1:
            raise ValidationError('Số lượng tuyển phải ít nhất là 1 vị trí.')
        return vacancies

    def clean_deadline(self):
        deadline = self.cleaned_data.get('deadline')
        if deadline and deadline < date.today():
            raise ValidationError('Hạn nộp hồ sơ phải là ngày trong tương lai.')
        return deadline

    def clean_salary_range_min(self):
        salary_min = self.cleaned_data.get('salary_range_min')
        if salary_min is not None and salary_min < 0:
            raise ValidationError('Lương tối thiểu không được là số âm.')
        return salary_min

    def clean(self):
        cleaned_data = super().clean()
        salary_min = cleaned_data.get('salary_range_min')
        salary_max = cleaned_data.get('salary_range_max')

        if salary_min is not None and salary_max is not None:
            if salary_max < 0:
                self.add_error('salary_range_max', 'Lương tối đa không được là số âm.')
            elif salary_max < salary_min:
                self.add_error(
                    'salary_range_max',
                    'Lương tối đa phải lớn hơn hoặc bằng lương tối thiểu.'
                )

        return cleaned_data


# ─── CandidateForm ─────────────────────────────────────────────────────────────

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

    def clean_full_name(self):
        name = self.cleaned_data.get('full_name', '').strip()
        if not name:
            raise ValidationError('Họ và tên ứng viên không được để trống.')
        if len(name) < 2:
            raise ValidationError('Họ và tên phải có ít nhất 2 ký tự.')
        return name

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if phone:
            if not PHONE_VN_REGEX.match(phone):
                raise ValidationError(
                    'Số điện thoại không hợp lệ. Vui lòng nhập đúng định dạng Việt Nam (vd: 0901234567).'
                )
        return phone

    def clean_cv_file(self):
        cv_file = self.cleaned_data.get('cv_file')
        if cv_file and hasattr(cv_file, 'name'):
            ext = '.' + cv_file.name.rsplit('.', 1)[-1].lower() if '.' in cv_file.name else ''
            if ext not in ALLOWED_CV_EXTENSIONS:
                raise ValidationError(
                    f'Định dạng file CV không hợp lệ. Chỉ chấp nhận: {", ".join(ALLOWED_CV_EXTENSIONS).upper()}.'
                )
            # Giới hạn kích thước file 10MB
            if cv_file.size > 10 * 1024 * 1024:
                raise ValidationError('Kích thước file CV không được vượt quá 10MB.')
        return cv_file


# ─── InterviewForm ─────────────────────────────────────────────────────────────

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

    def clean_scheduled_at(self):
        scheduled_at = self.cleaned_data.get('scheduled_at')
        if scheduled_at:
            now = timezone.now()
            # Chỉ kiểm tra tương lai nếu đây là bản ghi mới hoặc thời gian thay đổi
            if not self.instance.pk and scheduled_at < now:
                raise ValidationError('Thời gian phỏng vấn không được là thời điểm trong quá khứ.')
        return scheduled_at

    def clean_duration_minutes(self):
        duration = self.cleaned_data.get('duration_minutes')
        if duration is not None:
            if duration < 15:
                raise ValidationError('Thời lượng phỏng vấn phải ít nhất 15 phút.')
            if duration > 480:
                raise ValidationError('Thời lượng phỏng vấn không được vượt quá 480 phút (8 tiếng).')
        return duration

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        rating = cleaned_data.get('rating')
        feedback = cleaned_data.get('feedback', '').strip() if cleaned_data.get('feedback') else ''

        # Nếu trạng thái là "Đã hoàn thành" thì bắt buộc phải có đánh giá và nhận xét
        if status == 'completed':
            if not rating:
                self.add_error('rating', 'Vui lòng nhập đánh giá khi phỏng vấn đã hoàn thành.')
            if not feedback:
                self.add_error('feedback', 'Vui lòng nhập nhận xét khi phỏng vấn đã hoàn thành.')

        return cleaned_data
