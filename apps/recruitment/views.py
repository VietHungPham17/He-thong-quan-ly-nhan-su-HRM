from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q, Count
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from .models import JobPosting, Candidate, Interview
from .forms import JobPostingForm, CandidateForm, InterviewForm


class JobPostingListView(LoginRequiredMixin, ListView):
    model = JobPosting
    template_name = 'recruitment/job_posting_list.html'
    context_object_name = 'job_postings'
    paginate_by = 10

    def get_queryset(self):
        qs = JobPosting.objects.select_related(
            'department', 'position', 'created_by'
        ).annotate(cand_count=Count('candidates'))
        status = self.request.GET.get('status', '')
        q = self.request.GET.get('q', '')
        if status:
            qs = qs.filter(status=status)
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(department__name__icontains=q))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['status_choices'] = JobPosting.STATUS_CHOICES
        ctx['selected_status'] = self.request.GET.get('status', '')
        ctx['q'] = self.request.GET.get('q', '')
        return ctx


class JobPostingCreateView(LoginRequiredMixin, CreateView):
    model = JobPosting
    form_class = JobPostingForm
    template_name = 'recruitment/job_posting_form.html'
    success_url = reverse_lazy('recruitment:job_posting_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Tạo tin tuyển dụng thành công!')
        return super().form_valid(form)


class JobPostingUpdateView(LoginRequiredMixin, UpdateView):
    model = JobPosting
    form_class = JobPostingForm
    template_name = 'recruitment/job_posting_form.html'
    success_url = reverse_lazy('recruitment:job_posting_list')

    def form_valid(self, form):
        messages.success(self.request, 'Cập nhật tin tuyển dụng thành công!')
        return super().form_valid(form)


class JobPostingDeleteView(LoginRequiredMixin, DeleteView):
    model = JobPosting
    template_name = 'recruitment/job_posting_confirm_delete.html'
    success_url = reverse_lazy('recruitment:job_posting_list')

    def form_valid(self, form):
        messages.success(self.request, 'Xóa tin tuyển dụng thành công!')
        return super().form_valid(form)


class CandidatePipelineView(LoginRequiredMixin, TemplateView):
    template_name = 'recruitment/candidate_pipeline.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        job_id = self.request.GET.get('job', '')
        qs = Candidate.objects.select_related('applied_position')
        if job_id:
            qs = qs.filter(applied_position_id=job_id)

        ctx['job_postings'] = JobPosting.objects.filter(status='open')
        ctx['selected_job'] = job_id
        ctx['pipeline'] = {
            'new': qs.filter(status='new'),
            'screening': qs.filter(status='screening'),
            'interview': qs.filter(status='interview'),
            'offer': qs.filter(status='offer'),
            'hired': qs.filter(status='hired'),
            'rejected': qs.filter(status='rejected'),
        }
        ctx['status_labels'] = {
            'new': 'Mới',
            'screening': 'Sàng lọc',
            'interview': 'Phỏng vấn',
            'offer': 'Đề nghị',
            'hired': 'Đã tuyển',
            'rejected': 'Từ chối',
        }
        return ctx


class CandidateListView(LoginRequiredMixin, ListView):
    model = Candidate
    template_name = 'recruitment/candidate_list.html'
    context_object_name = 'candidates'
    paginate_by = 15

    def get_queryset(self):
        qs = Candidate.objects.select_related('applied_position')
        status = self.request.GET.get('status', '')
        q = self.request.GET.get('q', '')
        job = self.request.GET.get('job', '')
        if status:
            qs = qs.filter(status=status)
        if q:
            qs = qs.filter(Q(full_name__icontains=q) | Q(email__icontains=q))
        if job:
            qs = qs.filter(applied_position_id=job)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['status_choices'] = Candidate.STATUS_CHOICES
        ctx['job_postings'] = JobPosting.objects.all()
        ctx['selected_status'] = self.request.GET.get('status', '')
        ctx['selected_job'] = self.request.GET.get('job', '')
        ctx['q'] = self.request.GET.get('q', '')
        return ctx


class CandidateCreateView(LoginRequiredMixin, CreateView):
    model = Candidate
    form_class = CandidateForm
    template_name = 'recruitment/candidate_form.html'
    success_url = reverse_lazy('recruitment:candidate_list')

    def form_valid(self, form):
        messages.success(self.request, 'Thêm ứng viên thành công!')
        return super().form_valid(form)


class CandidateUpdateView(LoginRequiredMixin, UpdateView):
    model = Candidate
    form_class = CandidateForm
    template_name = 'recruitment/candidate_form.html'
    success_url = reverse_lazy('recruitment:candidate_list')

    def form_valid(self, form):
        messages.success(self.request, 'Cập nhật ứng viên thành công!')
        return super().form_valid(form)


class InterviewListView(LoginRequiredMixin, ListView):
    model = Interview
    template_name = 'recruitment/interview_list.html'
    context_object_name = 'interviews'
    paginate_by = 15

    def get_queryset(self):
        return Interview.objects.select_related(
            'candidate', 'candidate__applied_position', 'interviewer'
        )


class InterviewCreateView(LoginRequiredMixin, CreateView):
    model = Interview
    form_class = InterviewForm
    template_name = 'recruitment/interview_form.html'
    success_url = reverse_lazy('recruitment:interview_list')

    def form_valid(self, form):
        messages.success(self.request, 'Lên lịch phỏng vấn thành công!')
        return super().form_valid(form)
