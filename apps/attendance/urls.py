from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('', views.AttendanceListView.as_view(), name='attendance_list'),
    path('create/', views.AttendanceCreateView.as_view(), name='attendance_create'),
    path('generate/', views.GenerateAttendanceView.as_view(), name='generate_attendance'),
    path('<int:pk>/edit/', views.AttendanceUpdateView.as_view(), name='attendance_edit'),

    path('leave-requests/', views.LeaveRequestListView.as_view(), name='leave_request_list'),
    path('leave-requests/create/', views.LeaveRequestCreateView.as_view(), name='leave_request_create'),
    path('leave-requests/<int:pk>/approve/', views.approve_leave, name='leave_approve'),
    path('leave-requests/<int:pk>/cancel/', views.cancel_leave, name='leave_cancel'),

    path('schedules/', views.WorkScheduleListView.as_view(), name='work_schedule_list'),
    path('schedules/create/', views.WorkScheduleCreateView.as_view(), name='work_schedule_create'),
]
