from django.urls import path
from . import views

app_name = 'recruitment'

urlpatterns = [
    path('jobs/', views.JobPostingListView.as_view(), name='job_posting_list'),
    path('jobs/create/', views.JobPostingCreateView.as_view(), name='job_posting_create'),
    path('jobs/<int:pk>/edit/', views.JobPostingUpdateView.as_view(), name='job_posting_edit'),
    path('jobs/<int:pk>/delete/', views.JobPostingDeleteView.as_view(), name='job_posting_delete'),

    path('candidates/', views.CandidateListView.as_view(), name='candidate_list'),
    path('candidates/pipeline/', views.CandidatePipelineView.as_view(), name='candidate_pipeline'),
    path('candidates/create/', views.CandidateCreateView.as_view(), name='candidate_create'),
    path('candidates/<int:pk>/edit/', views.CandidateUpdateView.as_view(), name='candidate_edit'),

    path('interviews/', views.InterviewListView.as_view(), name='interview_list'),
    path('interviews/create/', views.InterviewCreateView.as_view(), name='interview_create'),
    path('interviews/<int:pk>/edit/', views.InterviewUpdateView.as_view(), name='interview_edit'),
    path('interviews/<int:pk>/cancel/', views.InterviewCancelView.as_view(), name='interview_cancel'),
]
