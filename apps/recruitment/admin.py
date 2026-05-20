from django.contrib import admin
from .models import JobPosting, Candidate, Interview


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ['title', 'department', 'vacancies', 'status', 'deadline', 'created_at']
    list_filter = ['status', 'department']
    search_fields = ['title']


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'applied_position', 'status', 'source', 'applied_at']
    list_filter = ['status', 'source']
    search_fields = ['full_name', 'email']


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'interviewer', 'scheduled_at', 'interview_type', 'status', 'rating']
    list_filter = ['status', 'interview_type']
    search_fields = ['candidate__full_name']
