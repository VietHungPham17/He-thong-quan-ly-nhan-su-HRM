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

        self.stdout.write(self.style.SUCCESS("✓ Tạo tài khoản admin và HR demo."))

        # ── Các tài khoản nhân viên có tên thực ──────────────────────
        named_employees = [
            # (username, first_name, last_name, phone, role)
            ("nguyen.van.a", "An",    "Nguyễn Văn",  "0912345001", "employee"),
            ("tran.thi.b",   "Bình",  "Trần Thị",   "0912345002", "employee"),
            ("le.van.c",     "Cường", "Lê Văn",     "0912345003", "employee"),
            ("pham.thi.d",   "Dung",  "Phạm Thị",   "0912345004", "employee"),
            ("hoang.van.e",  "Em",    "Hoàng Văn",  "0912345005", "employee"),
            ("vu.thi.f",     "Fư",    "Vũ Thị",     "0912345006", "employee"),
            ("do.van.g",     "Gia",   "Đỗ Văn",     "0912345007", "manager"),
            ("bui.thi.h",    "Hoa",   "Bùi Thị",    "0912345008", "employee"),
            ("dang.van.i",   "Ích",   "Đặng Văn",   "0912345009", "employee"),
            ("dinh.thi.j",   "Jade",  "Đinh Thị",   "0912345010", "hr"),
        ]
        named_users = []
        for username, first, last, phone, role in named_employees:
            u, _ = User.objects.update_or_create(
                username=username,
                defaults={
                    "email": f"{username}@hrm.com",
                    "first_name": first,
                    "last_name": last,
                    "role": role,
                    "is_staff": role in ("admin", "hr"),
                    "phone": phone,
                }
            )
            u.set_password("123456")
            u.save()
            named_users.append((username, first, last, role))

        self.stdout.write(self.style.SUCCESS(f"✓ Tạo {len(named_employees)} tài khoản nhân viên có tên thực."))

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
                        "salary_grade": str(min(idx, 3)),
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

        # ── 3 tài khoản Manager cố định ────────────────────────────────────────
        managers_data = [
            # (username, first_name, last_name, phone, dept_code)
            ("manager_it",   "Khoa",  "Nguyễn Văn",  "0912100001", "IT"),
            ("manager_sale", "Hùng",  "Trần Quốc",   "0912100002", "SALE"),
            ("manager_hr",   "Lan",   "Phạm Thị",   "0912100003", "HR"),
        ]
        managers = []
        dept_map = {d.code: d for d in departments}
        pos_map  = {p.department.code: p for p in positions if p.level == "manager"}

        for username, first, last, phone, dept_code in managers_data:
            full_name = f"{last} {first}"
            u, _ = User.objects.update_or_create(
                username=username,
                defaults={
                    "email": f"{username}@hrm.com",
                    "first_name": first,
                    "last_name": last,
                    "role": "manager",
                    "phone": phone,
                }
            )
            u.set_password("123456")
            u.save()

            dept = dept_map.get(dept_code)
            pos  = pos_map.get(dept_code)
            hire = date(2021, random.randint(1, 12), random.randint(1, 28))

            emp, _ = Employee.objects.update_or_create(
                user=u,
                defaults={
                    "full_name": full_name,
                    "gender": random.choice(["male", "female"]),
                    "dob": date(random.randint(1980, 1990), random.randint(1, 12), random.randint(1, 28)),
                    "phone": phone,
                    "email": f"{username}@hrm.com",
                    "address": f"Số {random.randint(1, 200)}, Hà Nội",
                    "id_number": f"0{random.randint(10000000000, 99999999999)}",
                    "department": dept,
                    "position": pos,
                    "hire_date": hire,
                    "employment_type": "full_time",
                    "status": "active",
                    "emergency_contact_name": "Người thân",
                    "emergency_contact_phone": f"09{random.randint(10000000, 99999999)}",
                    "bank_account": f"{random.randint(1000000000, 9999999999)}",
                    "bank_name": random.choice(["Vietcombank", "Techcombank", "BIDV"]),
                }
            )
            managers.append(emp)

            Contract.objects.update_or_create(
                employee=emp,
                defaults={
                    "contract_type": "indefinite",
                    "start_date": hire,
                    "end_date": None,
                    "salary": Decimal(random.choice([20000000, 25000000, 30000000])),
                    "signed_date": hire,
                    "status": "active",
                }
            )

        employees = managers
        self.stdout.write(self.style.SUCCESS(f"✓ Tạo 3 tài khoản Manager."))

        # ── 20 nhân viên demo cố định ──────────────────────────────────────────
        demo_employees_data = [
            # (username, first_name, last_name, gender, phone, dept_code, level, salary, contract_type, year_start)
            ("nv.minh.tuan",    "Tuấn",   "Nguyễn Minh",  "male",   "0901111001", "IT",    "junior",  10000000, "probation",  2025),
            ("nv.thu.huong",    "Hương",  "Trần Thị Thu", "female", "0901111002", "IT",    "middle",  15000000, "fixed_term", 2024),
            ("nv.duc.anh",      "Anh",    "Lê Đức",       "male",   "0901111003", "IT",    "senior",  20000000, "indefinite", 2022),
            ("nv.bao.chau",     "Châu",   "Phạm Thị Bảo", "female", "0901111004", "IT",    "lead",    22000000, "indefinite", 2021),
            ("nv.quoc.hung",    "Hùng",   "Vũ Quốc",      "male",   "0901111005", "SALE",  "junior",  9000000,  "probation",  2025),
            ("nv.lan.anh",      "Anh",    "Bùi Thị Lan",  "female", "0901111006", "SALE",  "middle",  13000000, "fixed_term", 2024),
            ("nv.manh.cuong",   "Cường",  "Đỗ Mạnh",      "male",   "0901111007", "SALE",  "senior",  18000000, "indefinite", 2023),
            ("nv.kim.oanh",     "Oanh",   "Hoàng Thị Kim","female", "0901111008", "SALE",  "middle",  14000000, "fixed_term", 2023),
            ("nv.thi.mai",      "Mai",    "Đinh Thị",     "female", "0901111009", "HR",    "junior",  9500000,  "fixed_term", 2025),
            ("nv.van.thanh",    "Thành",  "Đặng Văn",     "male",   "0901111010", "HR",    "middle",  13500000, "indefinite", 2023),
            ("nv.ngoc.linh",    "Linh",   "Trần Ngọc",    "female", "0901111011", "ACC",   "junior",  10000000, "probation",  2025),
            ("nv.duc.trung",    "Trung",  "Nguyễn Đức",   "male",   "0901111012", "ACC",   "middle",  14000000, "indefinite", 2023),
            ("nv.phuong.thao",  "Thảo",   "Lê Phương",    "female", "0901111013", "ACC",   "senior",  19000000, "indefinite", 2022),
            ("nv.hong.son",     "Sơn",    "Phạm Hồng",    "male",   "0901111014", "ACC",   "lead",    21000000, "indefinite", 2021),
            ("nv.thanh.hoa",    "Hoa",    "Vũ Thị Thanh", "female", "0901111015", "MKT",   "junior",  9000000,  "probation",  2025),
            ("nv.quang.minh",   "Minh",   "Bùi Quang",    "male",   "0901111016", "MKT",   "middle",  13000000, "fixed_term", 2024),
            ("nv.thu.trang",    "Trang",  "Đỗ Thị Thu",   "female", "0901111017", "MKT",   "senior",  17000000, "indefinite", 2023),
            ("nv.hoai.nam",     "Nam",    "Hoàng Hoài",   "male",   "0901111018", "ADMIN", "junior",  9500000,  "fixed_term", 2024),
            ("nv.bich.ngoc",    "Ngọc",   "Đinh Thị Bích","female", "0901111019", "ADMIN", "middle",  12000000, "indefinite", 2023),
            ("nv.tuan.kiet",    "Kiệt",   "Đặng Tuấn",    "male",   "0901111020", "ADMIN", "senior",  16000000, "indefinite", 2022),
        ]

        level_pos_map = {}
        for pos in positions:
            key = (pos.department.code, pos.level)
            level_pos_map[key] = pos

        demo_emps = []
        demo_emps_info = []
        for (username, first, last, gender, phone, dept_code, level, salary,
             contract_type, year_start) in demo_employees_data:
            full_name = f"{last} {first}"
            u, _ = User.objects.update_or_create(
                username=username,
                defaults={
                    "email": f"{username}@hrm.com",
                    "first_name": first,
                    "last_name": last,
                    "role": "employee",
                    "phone": phone,
                },
            )
            u.set_password("123456")
            u.save()

            dept = dept_map.get(dept_code)
            pos  = level_pos_map.get((dept_code, level))
            hire = date(year_start, random.randint(1, 12), random.randint(1, 20))

            emp, _ = Employee.objects.update_or_create(
                user=u,
                defaults={
                    "full_name": full_name,
                    "gender": gender,
                    "dob": date(random.randint(1985, 2000), random.randint(1, 12), random.randint(1, 20)),
                    "phone": phone,
                    "email": f"{username}@hrm.com",
                    "address": f"Số {random.randint(1, 300)}, {random.choice(['Hà Nội', 'TP.HCM', 'Đà Nẵng', 'Hải Phòng'])}",
                    "id_number": f"0{random.randint(10000000000, 99999999999)}",
                    "department": dept,
                    "position": pos,
                    "hire_date": hire,
                    "employment_type": "full_time" if contract_type != "part_time" else "part_time",
                    "status": "active",
                    "emergency_contact_name": random.choice(["Bố", "Mẹ", "Vợ", "Chồng", "Anh", "Chị"]),
                    "emergency_contact_phone": f"09{random.randint(10000000, 99999999)}",
                    "bank_account": f"{random.randint(1000000000, 9999999999)}",
                    "bank_name": random.choice(["Vietcombank", "Techcombank", "BIDV", "MB Bank", "VPBank"]),
                },
            )
            demo_emps.append(emp)
            demo_emps_info.append((username, first, last))

            end_date = None
            if contract_type in ("probation", "fixed_term"):
                end_date = date(hire.year + 1, hire.month, min(hire.day, 28))

            Contract.objects.update_or_create(
                employee=emp,
                defaults={
                    "contract_type": contract_type,
                    "start_date": hire,
                    "end_date": end_date,
                    "salary": Decimal(salary),
                    "signed_date": hire,
                    "status": "active",
                },
            )

        employees = employees + demo_emps
        self.stdout.write(self.style.SUCCESS(f"✓ Tạo {len(demo_emps)} nhân viên demo."))


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

        last_names = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Đỗ", "Vũ", "Bùi", "Đặng", "Đinh"]
        middle_names = ["Văn", "Thị", "Minh", "Quang", "Hữu", "Thanh", "Gia", "Tuấn", "Khánh", "Hoài"]
        first_names = ["An", "Bình", "Chi", "Dũng", "Hà", "Hải", "Hưng", "Linh", "Nam", "Phương", "Quân", "Trang"]

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

        # ── In bảng tài khoản / mật khẩu ──────────────────────────────
        self.stdout.write("")
        self.stdout.write(self.style.HTTP_INFO("=" * 62))
        self.stdout.write(self.style.HTTP_INFO("   DANH SÁCH TÀI KHOẢN MẪU  (mật khẩu: 123456)   "))
        self.stdout.write(self.style.HTTP_INFO("=" * 62))
        self.stdout.write(self.style.WARNING(f"  {'Tài khoản':<22} {'Vai trò':<12} {'Mật khẩu'}"))
        self.stdout.write(self.style.WARNING("-" * 62))

        # Tài khoản đặc biệt
        for uname, role in [("admin_demo", "admin"), ("hr_demo", "hr")]:
            self.stdout.write(self.style.SUCCESS(f"  {uname:<22} {role:<12} 123456"))

        self.stdout.write("")
        # Tài khoản tên thực
        self.stdout.write("  --- Nhân viên tên thực ---")
        for username, first, last, role in named_users:
            full = f"{last} {first}"
            self.stdout.write(self.style.SUCCESS(f"  {username:<22} {role:<12} 123456   [{full}]"))

        self.stdout.write("")
        # Tài khoản Manager
        self.stdout.write("  --- Manager ---")
        for username, first, last, phone, dept in managers_data:
            full = f"{last} {first}"
            self.stdout.write(self.style.SUCCESS(f"  {username:<22} {'manager':<12} 123456   [{full} - {dept}]"))

        self.stdout.write("")
        # Tài khoản nhân viên demo
        self.stdout.write("  --- Nhân viên demo (20 người) ---")
        for username, first, last in demo_emps_info:
            full = f"{last} {first}"
            self.stdout.write(self.style.SUCCESS(f"  {username:<22} {'employee':<12} 123456   [{full}]"))

        self.stdout.write(self.style.HTTP_INFO("=" * 62))
        self.stdout.write("")