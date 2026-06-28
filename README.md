# HRM System

Ung dung quan ly nhan su duoc xay dung bang Django. He thong gom cac module chinh cho nhan vien, cham cong, nghi phep, tien luong va tuyen dung.

## Tinh nang

- Quan ly phong ban, chuc vu, ho so nhan vien va hop dong lao dong.
- Quan ly cham cong, ca lam viec va don nghi phep.
- Tao va quan ly bang luong, phieu luong, phu cap va khau tru.
- Quan ly tin tuyen dung, ung vien, pipeline va lich phong van.
- Phan quyen theo nhom nguoi dung Admin, HR, Manager va Employee.

## Yeu cau

- Python 3.10+
- pip
- SQLite, dung san trong cau hinh mac dinh

## Cai dat

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Tao file `.env` tu mau neu can cau hinh rieng:

```bash
cp .env.example .env
```

Chay migrate:

```bash
python manage.py migrate
```

Nap du lieu demo neu can:

```bash
python manage.py seed_data
```

Tao tai khoan quan tri neu chua co:

```bash
python manage.py createsuperuser
```

## Chay ung dung

```bash
python manage.py runserver
```

Mo trinh duyet tai:

```text
http://127.0.0.1:8000
```

Co the dung script co san:

```bash
./start.sh
```

## Tai khoan demo

Sau khi chay `python manage.py seed_data`, co the dang nhap bang:

```text
Admin:     username=admin_demo / password=123456
HR:        username=hr_demo / password=123456
Manager:   username=manager_it, manager_sale, manager_hr / password=123456
Nhan vien: username=nguyen.van.a, tran.thi.b, le.van.c... / password=123456
```

## Kiem tra

```bash
python manage.py check
python manage.py test
```

Luu y: project hien chua co test case tu dong, nen lenh `test` co the bao `Ran 0 tests`.

## Cau truc thu muc

```text
apps/
  accounts/      Tai khoan va phan quyen
  employees/     Nhan vien, phong ban, chuc vu, hop dong
  attendance/    Cham cong, ca lam viec, nghi phep
  payroll/       Bang luong va phieu luong
  recruitment/   Tuyen dung va ung vien
templates/       Giao dien Django templates
static/          CSS va JavaScript tinh
hrm_project/     Cau hinh Django project
```

## Du lieu local

Repository khong commit cac file du lieu va cau hinh local nhu:

- `db.sqlite3`
- `media/`
- `.env`
