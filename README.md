---
![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)
![GitLab](https://img.shields.io/badge/gitlab-%23181717.svg?style=for-the-badge&logo=gitlab&logoColor=white)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)

> **Nhóm:** CNTT-17-03-N11 &nbsp;|&nbsp; **GitHub:** [huzgnm](https://github.com/huzgnm) &nbsp;|&nbsp; **Nền tảng:** Odoo 15 Community

---

# Mục lục

1. [Cài đặt môi trường](#1-cài-đặt-công-cụ-môi-trường-và-các-thư-viện-cần-thiết)
2. [Cài đặt database](#2-cài-đặt-database)
3. [Thiết lập tham số chạy](#3-thiết-lập-tham-số-chạy-cho-hệ-thống)
4. [Chạy hệ thống](#4-chạy-hệ-thống-và-cài-đặt-các-ứng-dụng-cần-thiết)
5. [Module Quản lý Tài sản](#5-module-quản-lý-tài-sản-quan_ly_tai_san)
6. [Module Quản lý Nhân sự](#6-module-quản-lý-nhân-sự-nhan_su)
7. [Module Quản lý Tài chính](#7-module-quản-lý-tài-chính-quan_ly_tai_chinh)
8. [Tính năng nâng cấp so với bản gốc](#8-tính-năng-nâng-cấp-so-với-bản-gốc)

---

# 1. Cài đặt công cụ, môi trường và các thư viện cần thiết

## 1.1. Clone project

```bash
git clone https://github.com/huzgnm/CNTT-17-03-N11.git
cd CNTT-17-03-N11
```

## 1.2. Cài đặt các thư viện cần thiết

```bash
sudo apt-get install libxml2-dev libxslt-dev libldap2-dev libsasl2-dev \
  libssl-dev python3.10-distutils python3.10-dev build-essential \
  libssl-dev libffi-dev zlib1g-dev python3.10-venv libpq-dev
```

## 1.3. Khởi tạo môi trường ảo

```bash
python3.10 -m venv ./venv
source venv/bin/activate
pip3 install -r requirements.txt
pip install requests
```

## 1.4. Cài đặt thư viện bổ sung

```bash
pip install python-docx
```

> **Lưu ý:** `python-docx` cần thiết cho tính năng xuất đơn mượn tài sản ra file `.docx`.

---

# 2. Cài đặt database

Khởi tạo database trên Docker:

```bash
sudo apt install docker-compose
sudo docker-compose up -d
```

---

# 3. Thiết lập tham số chạy cho hệ thống

Tạo tệp **odoo.conf**:

```ini
[options]
addons_path = addons
db_host = localhost
db_password = odoo
db_user = odoo
db_port = 5432
xmlrpc_port = 8069
```

---

# 4. Chạy hệ thống và cài đặt các ứng dụng cần thiết

```bash
python3 odoo-bin.py -c odoo.conf -u all
```

Truy cập: **http://localhost:8069/**

Sau khi đăng nhập, vào **Settings → Apps → Update Apps List** và cài theo thứ tự:

1. `Quản lý Nhân sự` (`nhan_su`)
2. `Quản lý Tài sản` (`quan_ly_tai_san`)
3. `Quản lý Tài chính` (`quan_ly_tai_chinh`)

---

# 5. Module Quản lý Tài sản (`quan_ly_tai_san`)

> **Phiên bản:** 0.2 &nbsp;|&nbsp; **Phụ thuộc:** `base`, `mail`, `nhan_su`

Module quản lý toàn bộ vòng đời tài sản cố định của doanh nghiệp.

## 5.1. Cấu trúc thư mục

```
addons/quan_ly_tai_san/
├── models/
│   ├── tai_san.py                      # Tài sản cố định (model trung tâm)
│   ├── bao_tri.py                      # Bảo trì tài sản
│   ├── thanh_ly.py                     # Thanh lý tài sản
│   ├── muon_tra.py                     # Mượn / trả tài sản
│   ├── dieu_chuyen_tai_san.py          # Điều chuyển tài sản
│   ├── don_muon.py                     # Xuất đơn mượn DOCX
│   ├── thong_ke.py                     # Thống kê tài sản
│   ├── danh_muc_loai_tai_san.py        # Danh mục loại tài sản
│   ├── nha_cung_cap.py                 # Nhà cung cấp
│   ├── lich_su_su_dung_tai_san.py      # Lịch sử sử dụng
│   ├── lich_su_quan_ly_tai_san.py      # Lịch sử quản lý
│   └── lich_su_dieu_chuyen_tai_san.py  # Lịch sử điều chuyển
├── views/                              # 13 file XML views
├── demo/demo.xml                       # Dữ liệu mẫu
├── security/ir.model.access.csv
└── __manifest__.py
```

## 5.2. Tính năng chính

### Quản lý tài sản cơ bản
- Tạo tài sản với mã tự sinh (`TS00001`, `TS00002`, ...)
- Trạng thái vòng đời: `Đang sử dụng → Bảo trì → Hỏng → Đã thanh lý`
- Cảnh báo bảo trì tự động khi tài sản chưa bảo trì > 180 ngày
- Lưu lịch sử đầy đủ: sử dụng, quản lý, điều chuyển
- Scan mã vạch / barcode

### Khấu hao tài sản
- Phương pháp đường thẳng: `Giá trị / Thời gian sử dụng / 12`
- Tính toán tự động: khấu hao mỗi năm, mỗi tháng, giá trị còn lại
- Tỷ lệ khấu hao lấy từ danh mục loại tài sản

### Bảo trì tài sản
Luồng: **Chờ duyệt → Đang bảo trì → Đã xong**

- Ghi nhận chi phí bảo trì, đơn vị thực hiện
- **Trigger Mức 2:** Hoàn thành bảo trì → tự động tạo Phiếu chi trong module Tài chính
- Cảnh báo lịch sử bảo trì trên form tài sản

### Thanh lý tài sản
Luồng: **Chờ duyệt → Đã duyệt**

- Tính toán lãi/lỗ thanh lý tự động
- **Trigger Mức 2:** Duyệt thanh lý → tự động tạo Phiếu thu trong module Tài chính
- Cập nhật trạng thái tài sản → "Đã thanh lý"

### Mượn / Trả tài sản
- Theo dõi người mượn, ngày mượn, ngày trả dự kiến / thực tế
- Xuất **đơn mượn định dạng `.docx`** (dùng `python-docx`)
- Kanban view theo trạng thái

### Điều chuyển tài sản
- Ghi nhận địa điểm cũ → mới, người phê duyệt
- Mã tự sinh `DC00001`

### Thống kê & Lịch sử
- Thống kê số lượng tài sản theo trạng thái
- 3 loại lịch sử: sử dụng, quản lý, điều chuyển

---

# 6. Module Quản lý Nhân sự (`nhan_su`)

> **Phiên bản:** 0.1 &nbsp;|&nbsp; **Phụ thuộc:** `base`

## 6.1. Cấu trúc

```
addons/nhan_su/
├── models/
│   ├── nhan_vien.py       # Nhân viên
│   ├── phong_ban.py       # Phòng ban
│   └── chuc_vu.py         # Chức vụ
├── demo/demo.xml           # Dữ liệu mẫu (4 nhân viên, 4 phòng ban)
└── views/
```

## 6.2. Tính năng chính

- Quản lý nhân viên: họ tên, mã định danh, phòng ban, chức vụ, email, số điện thoại
- Lịch sử làm việc: chuyển phòng ban, thay đổi chức vụ
- Phân loại theo phòng ban và chức vụ
- Thống kê nhân viên theo độ tuổi

---

# 7. Module Quản lý Tài chính (`quan_ly_tai_chinh`)

> **Phiên bản:** 0.1 &nbsp;|&nbsp; **Phụ thuộc:** `base`, `mail`, `nhan_su`, `quan_ly_tai_san`

Module quản lý thu chi, ngân sách và báo cáo tài chính. Nhận dữ liệu tự động từ các sự kiện tài sản.

## 7.1. Cấu trúc thư mục

```
addons/quan_ly_tai_chinh/
├── models/
│   ├── phieu_thu_chi.py         # Phiếu thu / chi
│   ├── ngan_sach.py             # Ngân sách tài chính
│   ├── bao_cao_tai_chinh.py     # Báo cáo tài chính tổng hợp
│   ├── khau_hao_hang_thang.py   # Khấu hao hàng tháng
│   ├── ngan_sach_mua_sam.py     # Ngân sách mua sắm tài sản
│   └── bao_cao_tai_san.py       # Báo cáo tài sản tổng hợp
├── utils/
│   └── telegram_helper.py       # Gửi thông báo Telegram (Mức 3)
├── views/
└── security/ir.model.access.csv
```

## 7.2. Tính năng chính

### Phiếu Thu / Chi
- Luồng: **Nháp → Chờ duyệt → Đã duyệt** (có thể Hủy)
- Phân loại nguồn gốc: Bảo trì / Mua sắm / Thanh lý / Lương / Khác
- Liên kết trực tiếp với tài sản, phiếu bảo trì, phiếu thanh lý
- Mã tự sinh: `PT00001` (thu), `PC00001` (chi)
- Tích hợp chatter để theo dõi lịch sử duyệt

### Ngân sách
- Đặt ngân sách thu / chi theo tháng
- Theo dõi % sử dụng ngân sách (progressbar)
- Cảnh báo khi vượt ngân sách

### Khấu hao hàng tháng
- G