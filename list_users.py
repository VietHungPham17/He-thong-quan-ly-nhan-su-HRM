import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrm_project.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

print(f"{'Username':<20} | {'Role':<15} | {'Can Manage':<10} | {'Employee Profile'}")
print("-" * 70)
for u in User.objects.all():
    has_profile = hasattr(u, 'employee_profile')
    print(f"{u.username:<20} | {u.role:<15} | {str(u.can_manage):<10} | {has_profile}")
