import random
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.employees.models import Department, Position, Employee, Contract
from apps.attendance.models import WorkSchedule, AttendanceRecord, LeaveType, LeaveBalance, LeaveRequest
from apps.payroll.models import SalaryStructure, InsuranceRate, Payroll, AllowanceItem, DeductionItem
from apps.recruitment.models import JobPosting, Candidate, Interview


class Command(BaseCommand):
    help = "Seed dữ liệu demo cho hệ thống HRM"

    def handle(self, *args, **kwargs):
        User = get_user_model()

        self.stdout.write(self.style.WARNING("Đang tạo dữ liệu demo..."))

        admin, _ = User.objects.update_or_create(
            username="admin_demo",
            defaults={
                "email": "admin.demo@hrm.com",
                "first_name": "Admin",
                "last_name": "Demo",
                "role": "admin",
                "is_staff": True,
                "is_superuser": True,
            }
        )
        admin.set_password("123456")
        admin.save()

        hr, _ = User.objects.update_or_create(
            username="hr_demo",
            defaults={
                "email": "hr.demo@hrm.com",
                "first_name": "HR",
                "last_name": "Demo",
                "role": "hr",
                "is_staff": True,
            }
        )
        hr.set_password("123456")
        hr.save()

        departments_data = [
            ("Nhân sự", "HR"),
            ("Công nghệ thông tin", "IT"),
            ("Kế toán", "ACC"),
            ("Kinh doanh", "SALE"),
            ("Marketing", "MKT"),
            ("Hành chính", "ADMIN"),
        ]

        departments = []
        for name, code in departments_data:
            dept, _ = Department.objects.update_or_create(
                code=code,
                defaults={
                    "name": name,
                    "description": f"Phòng ban {name}",
                    "manager": hr,
                }
            )
            departments.append(dept)

        position_names = [
            ("Nhân viên", "junior"),
            ("Chuyên viên", "middle"),
            ("Chuyên viên cao cấp", "senior"),
            ("Trưởng nhóm", "lead"),
            ("Trưởng phòng", "manager"),
        ]

        positions = []
        for dept in departments:
            for idx, (name, level) in enumerate(position_names, start=1):
                pos, _ = Position.objects.update_or_create(
                    code=f"{dept.code}-{idx}",
                    defaults={
                        "name": f"{name} {dept.name}",
                        "department": dept,
                        "level": level,
                        "salary_grade": f"B{idx}",
                    }
                )
                positions.append(pos)

        WorkSchedule.objects.get_or_create(
            name="Ca hành chính",
            defaults={
                "monday": True,
                "tuesday": True,
                "wednesday": True,
                "thursday": True,
                "friday": True,
                "saturday": False,
                "sunday": False,
                "start_time": time(8, 0),
                "end_time": time(17, 0),
                "break_duration_minutes": 60,
            }
        )

        leave_types = []
        for name, days, paid in [
            ("Nghỉ phép năm", 12, True),
            ("Nghỉ ốm", 10, True),
            ("Nghỉ việc riêng", 5, False),
            ("Nghỉ thai sản", 180, True),
        ]:
            lt, _ = LeaveType.objects.get_or_create(
                name=name,
                defaults={
                    "days_per_year": days,
                    "is_paid": paid,
                }
            )
            leave_types.append(lt)

        SalaryStructure.objects.get_or_create(
            name="Cấu trúc lương cơ bản",
            defaults={
                "basic_salary_percentage": Decimal("100.00"),
                "description": "Lương cơ bản + phụ cấp - khấu trừ",
            }
        )

        for name, emp_rate, employer_rate in [
            ("Bảo hiểm xã hội", "8.00", "17.50"),
            ("Bảo hiểm y tế", "1.50", "3.00"),
            ("Bảo hiểm thất nghiệp", "1.00", "1.00"),
        ]:
            InsuranceRate.objects.get_or_create(
                name=name,
                defaults={
                    "employee_rate": Decimal(emp_rate),
                    "employer_rate": Decimal(employer_rate),
                    "effective_from": date(2026, 1, 1),
                }
            )

        last_names = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Đỗ", "Vũ", "Bùi", "Đặng", "Đinh"]
        middle_names = ["Văn", "Thị", "Minh", "Quang", "Hữu", "Thanh", "Gia", "Tuấn", "Khánh", "Hoài"]
        first_names = ["An", "Bình", "Chi", "Dũng", "Hà", "Hải", "Hưng", "Linh", "Nam", "Phương", "Quân", "Trang"]

        employees = []

        for i in range(1, 51):
            full_name = f"{random.choice(last_names)} {random.choice(middle_names)} {random.choice(first_names)}"
            username = f"demo{i:03d}"
            email = f"demo{i:03d}@hrm.com"

            user, _ = User.objects.update_or_create(
                username=username,
                defaults={
                    "email": email,
                    "first_name": full_name.split()[-1],
                    "last_name": " ".join(full_name.split()[:-1]),
                    "role": random.choice(["employee", "employee", "employee", "manager"]),
                    "phone": f"09{random.randint(10000000, 99999999)}",
                }
            )
            user.set_password("123456")
            user.save()

            position = random.choice(positions)
            department = position.department

            employee, _ = Employee.objects.update_or_create(
                user=user,
                defaults={
                    "full_name": full_name,
                    "gender": random.choice(["male", "female"]),
                    "dob": date(random.randint(1985, 2002), random.randint(1, 12), random.randint(1, 28)),
                    "phone": user.phone,
                    "email": email,
                    "address": f"Số {random.randint(1, 200)}, Hà Nội",
                    "id_number": f"0{random.randint(10000000000, 99999999999)}",
                    "department": department,
                    "position": position,
                    "hire_date": date(random.randint(2020, 2025), random.randint(1, 12), random.randint(1, 28)),
                    "employment_type": random.choice(["full_time", "full_time", "contract", "part_time"]),
                    "status": random.choice(["active", "active", "active", "inactive"]),
                    "emergency_contact_name": "Người thân",
                    "emergency_contact_phone": f"09{random.randint(10000000, 99999999)}",
                    "bank_account": f"{random.randint(1000000000, 9999999999)}",
                    "bank_name": random.choice(["Vietcombank", "Techcombank", "BIDV", "MB Bank", "ACB"]),
                }
            )
            employees.append(employee)

            salary = random.choice([
                8000000, 10000000, 12000000, 15000000,
                18000000, 20000000, 25000000, 30000000
            ])

            Contract.objects.update_or_create(
                employee=employee,
                defaults={
                    "contract_type": random.choice(["fixed_term", "indefinite", "probation"]),
                    "start_date": employee.hire_date or date(2024, 1, 1),
                    "end_date": None,
                    "salary": Decimal(salary),
                    "signed_date": employee.hire_date or date(2024, 1, 1),
                    "status": "active",
                }
            )

        today = date.today()
        current_year = today.year
        current_month = today.month

        for employee in employees:
            for lt in leave_types:
                LeaveBalance.objects.update_or_create(
                    employee=employee,
                    leave_type=lt,
                    year=current_year,
                    defaults={
                        "allocated_days": Decimal(lt.days_per_year),
                        "used_days": Decimal(random.randint(0, min(5, lt.days_per_year))),
                    }
                )

            for d in range(1, 23):
                work_date = date(current_year, current_month, min(d, 28))

                if work_date.weekday() >= 5:
                    continue

                status = random.choice(["present", "present", "present", "late", "absent"])
                check_in = None if status == "absent" else random.choice([time(8, 0), time(8, 10), time(8, 30), time(9, 0)])
                check_out = None if status == "absent" else random.choice([time(17, 0), time(17, 30), time(18, 0)])

                AttendanceRecord.objects.update_or_create(
                    employee=employee,
                    date=work_date,
                    defaults={
                        "check_in": check_in,
                        "check_out": check_out,
                        "status": status,
                        "note": "Dữ liệu demo",
                    }
                )

            leave_type = random.choice(leave_types)
            start_date = today + timedelta(days=random.randint(1, 20))
            end_date = start_date + timedelta(days=random.randint(0, 2))
            days_count = (end_date - start_date).days + 1

            if LeaveRequest.objects.filter(employee=employee, start_date=start_date).count() == 0:
                LeaveRequest.objects.create(
                    employee=employee,
                    leave_type=leave_type,
                    start_date=start_date,
                    end_date=end_date,
                    days_count=Decimal(days_count),
                    reason=random.choice([
                        "Nghỉ việc cá nhân",
                        "Nghỉ ốm",
                        "Gia đình có việc",
                        "Nghỉ phép năm",
                    ]),
                    status=random.choice(["pending", "approved", "rejected"]),
                    approved_by=hr,
                    approved_at=timezone.now(),
                )

            contract = employee.contracts.first()
            basic_salary = contract.salary if contract else Decimal("10000000")
            allowance = Decimal(random.choice([500000, 1000000, 1500000, 2000000]))
            deduction = Decimal(random.choice([300000, 500000, 800000, 1000000]))
            net_salary = basic_salary + allowance - deduction

            payroll, _ = Payroll.objects.update_or_create(
                employee=employee,
                month=current_month,
                year=current_year,
                defaults={
                    "basic_salary": basic_salary,
                    "allowances_total": allowance,
                    "deductions_total": deduction,
                    "net_salary": net_salary,
                    "working_days": 22,
                    "actual_working_days": random.randint(18, 22),
                    "status": random.choice(["draft", "approved", "paid"]),
                    "note": "Bảng lương demo",
                }
            )

            payroll.allowance_items.all().delete()
            payroll.deduction_items.all().delete()

            AllowanceItem.objects.create(
                payroll=payroll,
                name="Phụ cấp ăn trưa",
                amount=allowance,
            )

            DeductionItem.objects.create(
                payroll=payroll,
                name="Khấu trừ bảo hiểm",
                amount=deduction,
            )

        job_postings = []
        for i in range(1, 11):
            position = random.choice(positions)

            job, _ = JobPosting.objects.update_or_create(
                title=f"Tuyển dụng {position.name}",
                defaults={
                    "department": position.department,
                    "position": position,
                    "description": f"Tuyển dụng vị trí {position.name}",
                    "requirements": "Có kinh nghiệm, kỹ năng giao tiếp tốt, tinh thần trách nhiệm cao.",
                    "salary_range_min": Decimal(random.choice([8000000, 10000000, 12000000])),
                    "salary_range_max": Decimal(random.choice([18000000, 22000000, 30000000])),
                    "vacancies": random.randint(1, 5),
                    "status": random.choice(["open", "open", "draft", "closed"]),
                    "deadline": today + timedelta(days=random.randint(10, 60)),
                    "created_by": hr,
                }
            )
            job_postings.append(job)

        for i in range(1, 31):
            full_name = f"{random.choice(last_names)} {random.choice(middle_names)} {random.choice(first_names)}"
            email = f"candidate{i:03d}@gmail.com"
            job = random.choice(job_postings)

            candidate, _ = Candidate.objects.update_or_create(
                email=email,
                defaults={
                    "full_name": full_name,
                    "phone": f"08{random.randint(10000000, 99999999)}",
                    "applied_position": job,
                    "cover_letter": "Tôi mong muốn được ứng tuyển vào vị trí này.",
                    "status": random.choice(["new", "screening", "interview", "offer", "hired", "rejected"]),
                    "source": random.choice(["website", "linkedin", "referral", "agency", "other"]),
                    "note": "Ứng viên demo",
                }
            )

            if Interview.objects.filter(candidate=candidate).count() == 0:
                Interview.objects.create(
                    candidate=candidate,
                    interviewer=hr,
                    scheduled_at=timezone.make_aware(
                        datetime.combine(today + timedelta(days=random.randint(1, 20)), time(random.randint(9, 16), 0))
                    ),
                    duration_minutes=random.choice([30, 45, 60]),
                    interview_type=random.choice(["phone", "online", "in_person"]),
                    status=random.choice(["scheduled", "completed", "cancelled"]),
                    feedback="Dữ liệu phỏng vấn demo",
                    rating=random.randint(1, 5),
                )

        self.stdout.write(self.style.SUCCESS("Tạo dữ liệu demo thành công!"))
        self.stdout.write(self.style.SUCCESS("Tài khoản admin_demo / 123456"))
        self.stdout.write(self.style.SUCCESS("Tài khoản hr_demo / 123456"))
        self.stdout.write(self.style.SUCCESS("Tài khoản nhân viên demo001 -> demo050 / 123456"))