---
![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)
![GitLab](https://img.shields.io/badge/gitlab-%23181717.svg?style=for-the-badge&logo=gitlab&logoColor=white)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)

> **Nhóm:** CNTT-17-03-N11 &nbsp;|&nbsp; **GitHub:** [huzgnm](https://github.com/huzgnm) &nbsp;|&nbsp; **Nền tảng:** Odoo 15 Community

---

# Mục lục

1. [Cài đặt môi trường](#1-cài-đặt-công-cụ-môi-trường-và-các-thư-viện-cần-thiết)
2. [Setup database](#2-setup-database)
3. [Setup tham số chạy](#3-setup-tham-số-chạy-cho-hệ-thống)
4. [Chạy hệ thống](#4-chạy-hệ-thống-và-cài-đặt-các-ứng-dụng-cần-thiết)
5. [Module Quản lý Tài sản](#5-module-quản-lý-tài-sản-quan_ly_tai_san)
6. [Module Quản lý Nhân sự](#6-module-quản-lý-nhân-sự-nhan_su)
7. [Module Quản lý Văn bản](#7-module-quản-lý-văn-bản-van_ban)
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
```

## 1.4. Cài đặt thư viện bổ sung cho module tùy chỉnh

```bash
pip install python-docx
```

> **Lưu ý:** `python-docx` cần thiết cho tính năng xuất đơn mượn tài sản ra file `.docx`.

---

# 2. Setup database

Khởi tạo database trên Docker:

```bash
sudo apt install docker-compose
sudo docker-compose up -d
```

---

# 3. Setup tham số chạy cho hệ thống

## 3.1. Khởi tạo odoo.conf

Tạo tệp **odoo.conf** với nội dung:

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

Sau khi đăng nhập, vào **Settings → Apps → Update Apps List** và cài:
- `Quản lý Tài Sản`
- `Quản lý Nhân sự`
- `Quản lý Văn bản`

---

# 5. Module Quản lý Tài sản (`quan_ly_tai_san`)

> **Phiên bản:** 0.2 &nbsp;|&nbsp; **Phụ thuộc:** `base`, `account`

Module quản lý toàn bộ vòng đời tài sản cố định, tích hợp đầy đủ với kế toán Odoo.

## 5.1. Cấu trúc thư mục

```
addons/quan_ly_tai_san/
├── models/
│   ├── tai_san.py                   # Tài sản cố định (model trung tâm)
│   ├── khau_hao_hang_thang.py       # Khấu hao hàng tháng
│   ├── bao_tri.py                   # Bảo trì tài sản
│   ├── thanh_ly.py                  # Thanh lý tài sản
│   ├── muon_tra.py                  # Mượn / trả tài sản
│   ├── dieu_chuyen_tai_san.py       # Điều chuyển tài sản
│   ├── don_muon.py                  # Xuất đơn mượn DOCX
│   ├── ngan_sach_mua_sam.py         # Ngân sách mua sắm
│   ├── bao_cao_tai_san.py           # Báo cáo tài chính tổng hợp
│   ├── thong_ke.py                  # Thống kê tài sản
│   ├── danh_muc_loai_tai_san.py     # Danh mục loại tài sản
│   ├── nha_cung_cap.py              # Nhà cung cấp
│   ├── lich_su_su_dung_tai_san.py   # Lịch sử sử dụng
│   ├── lich_su_quan_ly_tai_san.py   # Lịch sử quản lý
│   └── lich_su_dieu_chuyen_tai_san.py
├── views/                           # 15 file XML views
├── security/ir.model.access.csv
└── data/cron.xml                    # Cron job khấu hao tự động
```

## 5.2. Tính năng

### Quản lý tài sản cơ bản
- Tạo tài sản với mã tự sinh (`TS00001`, `TS00002`, ...)
- Trạng thái vòng đời: `Chờ sử dụng → Đang sử dụng → Bảo trì → Hỏng → Đã thanh lý`
- Lưu lịch sử đầy đủ: sử dụng, quản lý, điều chuyển

### Kế toán mua tài sản
Nhấn **Ghi sổ mua tài sản** → tự động tạo bút toán:
```
Nợ  TK Tài sản cố định (211)      xxx
    Có  TK Phải trả người bán (331)    xxx
```

### Khấu hao tự động hàng tháng
- Phương pháp: đường thẳng (`Nguyên giá ÷ Thời gian sử dụng ÷ 12`)
- Cron job tự chạy ngày **1 hàng tháng lúc 1:00 sáng**
- Bút toán khấu hao:
```
Nợ  TK Chi phí khấu hao (627x/641x/642x)    xxx
    Có  TK Hao mòn lũy kế (214x)                 xxx
```

### Bảo trì tài sản
Luồng: **Chờ duyệt → Đang bảo trì → Đã xong**

Nhấn **Ghi sổ chi phí**:
```
Nợ  TK Chi phí sửa chữa (627x)    xxx
    Có  TK Phải trả (331)              xxx
```

### Thanh lý tài sản
Luồng: **Nháp → Chờ duyệt → Đã duyệt → Ghi sổ kế toán**

Bút toán thanh lý (tự tính lãi/lỗ):
```
Nợ  TK Hao mòn lũy kế (214x)         xxx
Nợ  TK Thu hồi / Chi phí (711/811)    xxx
    Có  TK Nguyên giá TSCĐ (211)          xxx
    Có  TK Thu nhập khác (711)            xxx  ← nếu lãi
```

### Mượn / Trả tài sản
- Theo dõi người mượn, ngày mượn, ngày trả
- Xuất **đơn mượn định dạng `.docx`** (dùng thư viện `python-docx`)

### Điều chuyển tài sản
- Ghi nhận địa điểm cũ → mới, lý do điều chuyển
- Mã tự sinh `DC00001`, lịch sử lưu tự động vào tài sản

### Ngân sách mua sắm
- Lập kế hoạch ngân sách theo năm và loại tài sản
- Tính tỷ lệ thực hiện tự động
- Cảnh báo vượt ngân sách
- Trạng thái: `Lập kế hoạch → Chờ duyệt → Đã duyệt → Đang thực hiện → Hoàn thành`

### Báo cáo tài chính tổng hợp
- Tổng nguyên giá, tổng đã khấu hao, giá trị còn lại
- Thống kê hoạt động trong năm: mua mới, bảo trì, thanh lý, mượn
- Chi tiết từng tài sản

## 5.3. Danh sách Models

| Model | Mô tả | Mã tự sinh |
|-------|-------|-----------|
| `tai_san` | Tài sản cố định | `TS00001` |
| `khau_hao_hang_thang` | Lịch khấu hao hàng tháng | — |
| `bao_tri` | Phiếu bảo trì | `BT00001` |
| `thanh_ly` | Phiếu thanh lý | `TL00001` |
| `muon_tra` | Phiếu mượn trả | `MT00001` |
| `dieu_chuyen_tai_san` | Phiếu điều chuyển | `DC00001` |
| `ngan_sach_mua_sam` | Kế hoạch ngân sách | `NS0001` |
| `ngan_sach_mua_sam_chi_tiet` | Chi tiết ngân sách | — |
| `bao_cao_tai_san` | Báo cáo tổng hợp | — |
| `bao_cao_tai_san_chi_tiet` | Chi tiết báo cáo | — |
| `thong_ke` | Thống kê tài sản | `MTK001` |
| `danh_muc_loai_tai_san` | Loại tài sản | — |
| `nha_cung_cap` | Nhà cung cấp | — |
| `lich_su_su_dung_tai_san` | Lịch sử sử dụng | — |
| `lich_su_quan_ly_tai_san` | Lịch sử quản lý | — |
| `lich_su_dieu_chuyen_tai_san` | Lịch sử điều chuyển | — |

## 5.4. Menu hệ thống

```
QLTS
├── Thống kê tài sản
├── Quản lý Tài sản
│   ├── Tài sản
│   └── Danh mục loại tài sản
├── Bảo trì
├── Thanh lý
├── Mượn trả
├── Điều chuyển
├── Lịch sử
│   ├── Lịch sử sử dụng tài sản
│   ├── Lịch sử quản lý tài sản
│   └── Lịch sử điều chuyển tài sản
├── Nhà cung cấp
├── Kế toán
│   └── Khấu hao hàng tháng
├── Ngân sách
│   └── Ngân sách mua sắm
└── Báo cáo
    └── Báo cáo tài chính tài sản
```

---

# 6. Module Quản lý Nhân sự (`nhan_su`)

> **Phiên bản:** 0.1 &nbsp;|&nbsp; **Phụ thuộc:** `base`

## 6.1. Tính năng

- Quản lý hồ sơ nhân viên (mã tự sinh `NV00001`)
- Quản lý phòng ban và chức vụ
- Tự động ghi lịch sử làm việc khi thay đổi chức vụ/phòng ban
- Ràng buộc nghiệp vụ: **nhân viên phải trên 18 tuổi** (`@api.constrains`)

## 6.2. Danh sách Models

| Model | Mô tả |
|-------|-------|
| `nhan_vien` | Hồ sơ nhân viên |
| `phong_ban` | Phòng ban |
| `chuc_vu` | Chức vụ / chức danh |
| `lich_su_lam_viec` | Lịch sử công tác |

## 6.3. Trường thông tin chính

| Trường | Kiểu | Mô tả |
|--------|------|-------|
| `ma_nhan_vien` | Char | Mã tự sinh `NV00001` |
| `ho_ten` | Char | Họ và tên đầy đủ |
| `ngay_sinh` | Date | Ngày sinh (validate > 18 tuổi) |
| `gioi_tinh` | Selection | Nam / Nữ |
| `cccd` | Char | Số căn cước công dân |
| `phong_ban_id` | Many2one | Phòng ban |
| `chuc_vu_id` | Many2one | Chức vụ |
| `ngay_vao_lam` | Date | Ngày bắt đầu làm việc |
| `trang_thai` | Selection | Đang làm / Nghỉ việc |
| `lich_su_lam_viec_ids` | One2many | Lịch sử công tác |

---

# 7. Module Quản lý Văn bản (`van_ban`)

> **Phiên bản:** 0.1 &nbsp;|&nbsp; **Phụ thuộc:** `base`

## 7.1. Tính năng

- Quản lý văn bản đi trong tổ chức
- Theo dõi số hiệu, ngày ban hành, người ký, đơn vị nhận
- Lưu trữ và tra cứu văn bản

## 7.2. Model `van_ban_di`

| Trường | Kiểu | Mô tả |
|--------|------|-------|
| `so_hieu` | Char | Số hiệu văn bản |
| `ngay_ban_hanh` | Date | Ngày ban hành |
| `trich_yeu` | Text | Trích yếu nội dung |
| `nguoi_ky_id` | Many2one | Người ký (liên kết nhân viên) |
| `don_vi_nhan` | Char | Đơn vị / cá nhân nhận |
| `trang_thai` | Selection | Trạng thái xử lý |

---

# 8. Tính năng nâng cấp so với bản gốc

Bản này được phát triển dựa trên [TTDN-15-02-N3](https://github.com/thang0305/TTDN-15-02-N3) với các nâng cấp sau:

## 8.1. Module Quản lý Tài sản — Tính năng MỚI

| # | Tính năng | Mô tả |
|---|-----------|-------|
| 1 | **Kế toán mua tài sản** | Tự động tạo bút toán Nợ TK211 / Có TK331 khi mua |
| 2 | **Khấu hao hàng tháng tự động** | Cron job ngày 1 mỗi tháng, tạo bút toán KH vào sổ cái |
| 3 | **Kế toán bảo trì** | Ghi nhận chi phí bảo trì vào TK chi phí / TK phải trả |
| 4 | **Kế toán thanh lý** | Bút toán đầy đủ: xóa nguyên giá, xóa hao mòn, ghi nhận lãi/lỗ |
| 5 | **Ngân sách mua sắm** | Lập và theo dõi ngân sách, cảnh báo vượt ngân sách |
| 6 | **Báo cáo tài chính tổng hợp** | Báo cáo theo năm: nguyên giá, đã KH, còn lại, hoạt động |
| 7 | **Xuất đơn mượn DOCX** | Xuất phiếu mượn tài sản ra file Word |
| 8 | **Lịch sử điều chuyển** | Ghi nhận đầy đủ lịch sử điều chuyển tài sản giữa địa điểm |
| 9 | **Thống kê tài sản** | Dashboard thống kê số lượng, tình trạng theo loại tài sản |

## 8.2. Sửa lỗi so với bản gốc

| # | Lỗi | Giải pháp |
|---|-----|-----------|
| 1 | Duplicate method `_compute_so_lan_dieu_chuyen` | Gộp lại, chỉ giữ một method |
| 2 | Conflict `related` + `compute` trên field `khau_hao_moi_nam` | Chuyển hoàn toàn sang `compute` |
| 3 | `write()` ghi vào computed field `trang_thai` trong `muon_tra.py` | Dùng `sudo().write()` đúng cách |
| 4 | Sử dụng `.bold` sai trong `don_muon.py` | Sửa thành `run.bold = True` (python-docx đúng chuẩn) |
| 5 | Logic compute sai trong `thong_ke.py` (đếm toàn bộ tài sản) | Dùng `filtered()` chỉ đếm tài sản liên kết |
| 6 | Kiểu dữ liệu `Char` sai cho các field số | Chuyển sang `Float`/`Integer` phù hợp |
| 7 | Thiếu dependency `account` trong manifest | Thêm `account` vào `depends` |
| 8 | File manifest bị truncate (thiếu `]` và `}`) | Rewrite hoàn chỉnh |

## 8.3. Tài khoản kế toán Việt Nam được áp dụng

| TK | Tên tài khoản | Sử dụng |
|----|--------------|---------|
| 211 | Tài sản cố định hữu hình | Nợ khi mua, Có khi thanh lý |
| 214x | Hao mòn lũy kế TSCĐ | Có khi khấu hao, Nợ khi thanh lý |
| 331 | Phải trả người bán | Có khi mua/bảo trì |
| 627x/641x/642x | Chi phí sản xuất/bán hàng/QLDN | Nợ khi KH và bảo trì |
| 711 | Thu nhập khác | Có khi lãi thanh lý |
| 811 | Chi phí khác | Nợ khi lỗ thanh lý |

---

## Thông tin nhóm

| | |
|-|-|
| **Nhóm** | CNTT-17-03-N11 |
| **Trường** | Đại học Đại Nam — Khoa Công nghệ Thông tin |
| **Repository** | https://github.com/huzgnm/CNTT-17-03-N11 |
| **Dựa trên** | https://github.com/thang0305/TTDN-15-02-N3 |
| **Email** | huzgnm@gmail.com |
