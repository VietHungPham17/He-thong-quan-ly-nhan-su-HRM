from django.urls import path
from . import views

app_name = 'payroll'

urlpatterns = [
    path('', views.PayrollListView.as_view(), name='payroll_list'),
    path('create/', views.PayrollCreateView.as_view(), name='payroll_create'),
    path('<int:pk>/', views.PayrollDetailView.as_view(), name='payroll_detail'),
    path('<int:pk>/edit/', views.PayrollUpdateView.as_view(), name='payroll_edit'),
    path('generate/', views.GeneratePayrollView.as_view(), name='generate_payroll'),
]
