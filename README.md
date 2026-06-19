# CNTT-17-03-N11 — Hệ thống Quản lý ERP trên Odoo 15

> **Nhóm:** CNTT-17-03-N11  
> **GitHub:** [huzgnm](https://github.com/huzgnm)  
> **Nền tảng:** Odoo 15 Community  
> **Ngôn ngữ:** Python 3, XML, CSV

---

## Mục lục

1. [Tổng quan dự án](#tổng-quan-dự-án)
2. [Cấu trúc thư mục](#cấu-trúc-thư-mục)
3. [Module Quản lý Tài sản](#module-quản-lý-tài-sản)
4. [Module Quản lý Nhân sự](#module-quản-lý-nhân-sự)
5. [Module Quản lý Văn bản](#module-quản-lý-văn-bản)
6. [Hướng dẫn cài đặt](#hướng-dẫn-cài-đặt)
7. [Hướng dẫn sử dụng](#hướng-dẫn-sử-dụng)

---

## Tổng quan dự án

Dự án gồm **3 module Odoo custom** phục vụ quản lý doanh nghiệp:

| Module | Tên kỹ thuật | Phiên bản | Phụ thuộc |
|--------|-------------|-----------|-----------|
| Quản lý Tài sản | `quan_ly_tai_san` | 0.2 | `base`, `account` |
| Quản lý Nhân sự | `nhan_su` | 0.1 | `base` |
| Quản lý Văn bản | `van_ban` | 0.1 | `base` |

---

## Cấu trúc thư mục

```
addons/
├── quan_ly_tai_san/
│   ├── __manifest__.py
│   ├── __init__.py
│   ├── models/
│   │   ├── tai_san.py                  # Model tài sản cố định
│   │   ├── khau_hao_hang_thang.py      # Khấu hao hàng tháng
│   │   ├── bao_tri.py                  # Bảo trì tài sản
│   │   ├── thanh_ly.py                 # Thanh lý tài sản
│   │   ├── muon_tra.py                 # Mượn/trả tài sản
│   │   ├── dieu_chuyen_tai_san.py      # Điều chuyển tài sản
│   │   ├── don_muon.py                 # Đơn mượn (xuất DOCX)
│   │   ├── ngan_sach_mua_sam.py        # Ngân sách mua sắm
│   │   ├── bao_cao_tai_san.py          # Báo cáo tài chính
│   │   ├── thong_ke.py                 # Thống kê tài sản
│   │   ├── danh_muc_loai_tai_san.py    # Danh mục loại tài sản
│   │   ├── nha_cung_cap.py             # Nhà cung cấp
│   │   ├── lich_su_su_dung_tai_san.py  # Lịch sử sử dụng
│   │   ├── lich_su_quan_ly_tai_san.py  # Lịch sử quản lý
│   │   └── lich_su_dieu_chuyen_tai_san.py
│   ├── views/
│   │   ├── tai_san.xml
│   │   ├── khau_hao_hang_thang.xml
│   │   ├── bao_tri.xml
│   │   ├── thanh_ly.xml
│   │   ├── muon_tra.xml
│   │   ├── dieu_chuyen_tai_san.xml
│   │   ├── ngan_sach_mua_sam.xml
│   │   ├── bao_cao_tai_san.xml
│   │   ├── thong_ke.xml
│   │   ├── danh_muc_loai_tai_san.xml
│   │   ├── nha_cung_cap.xml
│   │   ├── lich_su_su_dung_tai_san.xml
│   │   ├── lich_su_quan_ly_tai_san.xml
│   │   ├── lich_su_dieu_chuyen_tai_san.xml
│   │   └── menu.xml
│   ├── security/
│   │   └── ir.model.access.csv
│   └── data/
│       └── cron.xml
│
├── nhan_su/
│   ├── __manifest__.py
│   ├── models/
│   │   ├── nhan_vien.py        # Nhân viên
│   │   ├── phong_ban.py        # Phòng ban
│   │   ├── chuc_vu.py          # Chức vụ
│   │   ├── lich_su_lam_viec.py # Lịch sử làm việc
│   │   └── so_luong_hon_18.py  # Kiểm tra tuổi
│   └── views/
│
└── van_ban/
    ├── __manifest__.py
    ├── models/
    │   └── van_ban_di.py       # Văn bản đi
    └── views/
```

---

## Module Quản lý Tài sản

### Tính năng chính

#### 1. Quản lý vòng đời tài sản
- Tạo và theo dõi tài sản cố định (mã tự sinh `TS00001`)
- Trạng thái: Chờ sử dụng → Đang sử dụng → Bảo trì → Hỏng → Đã thanh lý
- Lịch sử đầy đủ: sử dụng, quản lý, điều chuyển, bảo trì, thanh lý

#### 2. Kế toán mua tài sản
Khi nhấn **Ghi sổ mua tài sản**, hệ thống tự động tạo bút toán:
```
Nợ TK Tài sản (TK 211)          xxx
    Có TK Phải trả (TK 331)          xxx
```

#### 3. Khấu hao tự động hàng tháng
- Tính khấu hao theo phương pháp đường thẳng
- Cron job tự chạy vào ngày 1 hàng tháng
- Bút toán khấu hao tự động:
```
Nợ TK Chi phí khấu hao (TK 627x/641x/642x)    xxx
    Có TK Hao mòn lũy kế (TK 214x)                 xxx
```

#### 4. Bảo trì tài sản
Quy trình: **Chờ duyệt → Đang bảo trì → Đã xong**

Khi **Ghi sổ chi phí** bảo trì:
```
Nợ TK Chi phí (627x/641x/642x)    xxx
    Có TK Phải trả (TK 331)            xxx
```

#### 5. Thanh lý tài sản
Quy trình: **Nháp → Chờ duyệt → Đã duyệt → Ghi sổ kế toán**

Bút toán thanh lý:
```
Nợ TK Hao mòn lũy kế (TK 214x)      xxx  (phần đã khấu hao)
Nợ TK Thu hồi thanh lý (TK 711)      xxx  (tiền thu về)
Nợ TK Lỗ thanh lý (TK 811)          xxx  (nếu lỗ)
    Có TK Nguyên giá (TK 211)             xxx
    Có TK Lãi thanh lý (TK 711)           xxx  (nếu lãi)
```

#### 6. Mượn / Trả tài sản
- Theo dõi người mượn, ngày mượn, ngày trả dự kiến
- Xuất **đơn mượn định dạng DOCX** có đầy đủ thông tin

#### 7. Điều chuyển tài sản
- Ghi nhận địa điểm cũ → địa điểm mới (mã tự sinh `DC00001`)
- Lưu lịch sử điều chuyển tự động vào tài sản

#### 8. Ngân sách mua sắm
- Lập kế hoạch ngân sách theo năm và loại tài sản
- Cảnh báo khi vượt ngân sách
- Trạng thái: Lập kế hoạch → Chờ duyệt → Đã duyệt → Đang thực hiện → Hoàn thành

#### 9. Báo cáo tài chính tổng hợp
- Tổng nguyên giá, đã khấu hao, giá trị còn lại
- Thống kê hoạt động trong năm: mua mới, bảo trì, thanh lý, mượn
- Chi tiết từng tài sản trong tab riêng

### Danh sách Models

| Model | Bảng DB | Mô tả |
|-------|---------|-------|
| `tai_san` | `tai_san` | Tài sản cố định — model trung tâm |
| `khau_hao_hang_thang` | `khau_hao_hang_thang` | Lịch khấu hao từng tháng |
| `bao_tri` | `bao_tri` | Phiếu bảo trì (mã `BT00001`) |
| `thanh_ly` | `thanh_ly` | Phiếu thanh lý (mã `TL00001`) |
| `muon_tra` | `muon_tra` | Phiếu mượn trả (mã `MT00001`) |
| `dieu_chuyen_tai_san` | `dieu_chuyen_tai_san` | Phiếu điều chuyển (mã `DC00001`) |
| `ngan_sach_mua_sam` | `ngan_sach_mua_sam` | Ngân sách (mã `NS0001`) |
| `ngan_sach_mua_sam_chi_tiet` | `ngan_sach_mua_sam_chi_tiet` | Chi tiết ngân sách |
| `bao_cao_tai_san` | `bao_cao_tai_san` | Báo cáo tổng hợp |
| `bao_cao_tai_san_chi_tiet` | `bao_cao_tai_san_chi_tiet` | Chi tiết báo cáo |
| `thong_ke` | `thong_ke` | Thống kê (mã `MTK001`) |
| `danh_muc_loai_tai_san` | `danh_muc_loai_tai_san` | Loại tài sản |
| `nha_cung_cap` | `nha_cung_cap` | Nhà cung cấp |
| `lich_su_su_dung_tai_san` | `lich_su_su_dung_tai_san` | Lịch sử sử dụng |
| `lich_su_quan_ly_tai_san` | `lich_su_quan_ly_tai_san` | Lịch sử quản lý |
| `lich_su_dieu_chuyen_tai_san` | `lich_su_dieu_chuyen_tai_san` | Lịch sử điều chuyển |

### Cron Job

| Tên | Lịch chạy | Hành động |
|-----|-----------|-----------|
| Tính khấu hao hàng tháng | Ngày 1 mỗi tháng lúc 1:00 sáng | `cron_tinh_khau_hao_hang_thang()` |

---

## Module Quản lý Nhân sự

### Tính năng chính
- Quản lý hồ sơ nhân viên (mã tự sinh `NV00001`)
- Quản lý cơ cấu tổ chức: phòng ban, chức vụ
- Theo dõi lịch sử công tác tự động
- Ràng buộc nghiệp vụ: nhân viên phải trên 18 tuổi (`@api.constrains`)

### Danh sách Models

| Model | Mô tả |
|-------|-------|
| `nhan_vien` | Thông tin nhân viên |
| `phong_ban` | Phòng ban trong tổ chức |
| `chuc_vu` | Chức vụ / chức danh |
| `lich_su_lam_viec` | Lịch sử công tác của nhân viên |

### Trường thông tin nhân viên chính

| Trường | Kiểu | Mô tả |
|--------|------|-------|
| `ma_nhan_vien` | Char | Mã tự sinh NV00001 |
| `ho_ten` | Char | Họ và tên |
| `ngay_sinh` | Date | Ngày sinh (phải > 18 tuổi) |
| `gioi_tinh` | Selection | Nam / Nữ |
| `cccd` | Char | Căn cước công dân |
| `phong_ban_id` | Many2one | Phòng ban |
| `chuc_vu_id` | Many2one | Chức vụ |
| `ngay_vao_lam` | Date | Ngày bắt đầu làm |
| `trang_thai` | Selection | Đang làm / Nghỉ việc |

---

## Module Quản lý Văn bản

### Tính năng chính
- Quản lý văn bản đi trong tổ chức
- Theo dõi số hiệu, ngày ban hành, người ký
- Lưu trữ và tra cứu văn bản

### Danh sách Models

| Model | Mô tả |
|-------|-------|
| `van_ban_di` | Văn bản đi |

### Trường thông tin văn bản chính

| Trường | Kiểu | Mô tả |
|--------|------|-------|
| `so_hieu` | Char | Số hiệu văn bản |
| `ngay_ban_hanh` | Date | Ngày ban hành |
| `trich_yeu` | Text | Trích yếu nội dung |
| `nguoi_ky_id` | Many2one | Người ký (nhân viên) |
| `don_vi_nhan` | Char | Đơn vị nhận |
| `trang_thai` | Selection | Trạng thái xử lý |

---

## Hướng dẫn cài đặt

### Yêu cầu hệ thống

- Odoo 15 Community Edition
- Python 3.8+
- PostgreSQL 12+
- Module `account` (có sẵn trong Odoo 15)
- `python-docx` (cho tính năng xuất DOCX)

### Các bước cài đặt

**Bước 1: Clone repository**
```bash
git clone https://github.com/huzgnm/CNTT-17-03-N11.git
```

**Bước 2: Copy modules vào thư mục addons của Odoo**
```bash
cp -r CNTT-17-03-N11/addons/quan_ly_tai_san /path/to/odoo/addons/
cp -r CNTT-17-03-N11/addons/nhan_su /path/to/odoo/addons/
cp -r CNTT-17-03-N11/addons/van_ban /path/to/odoo/addons/
```

**Bước 3: Cài thư viện Python bổ sung**
```bash
pip install python-docx
```

**Bước 4: Cập nhật danh sách module và khởi động lại**
```bash
./odoo-bin -c odoo.conf -u all
# hoặc
./odoo-bin --addons-path=addons -d your_database -u quan_ly_tai_san,nhan_su,van_ban
```

**Bước 5: Kích hoạt modules trong giao diện**

Vào **Settings → Apps → Update Apps List**, tìm và cài:
- `Quản lý Tài Sản`
- `Quản lý Nhân sự`
- `Quản lý Văn bản`

---

## Hướng dẫn sử dụng

### Module Quản lý Tài sản

#### Tạo tài sản mới
1. Vào **QLTS → Quản lý Tài sản → Tài sản** → nhấn **Tạo mới**
2. Nhập: Tên tài sản, Loại tài sản, Nhà cung cấp, Ngày mua, Nguyên giá, Thời gian sử dụng (năm)
3. Tab **Kế toán mua**: chọn Sổ nhật ký, TK tài sản (211), TK phải trả (331)
4. Tab **Kế toán khấu hao**: chọn TK chi phí KH, TK hao mòn lũy kế (214x)
5. Nhấn **Ghi sổ mua tài sản** để tạo bút toán kế toán

#### Quản lý khấu hao
- **Tự động**: Cron job chạy ngày 1 hàng tháng
- **Thủ công**: Trong form tài sản → nhấn **Tính khấu hao tháng này**
- **Tạo toàn bộ lịch**: Nhấn **Tạo lịch khấu hao**
- Xem lịch sử tại tab **Kế toán khấu hao → Lịch khấu hao hàng tháng**

#### Tạo phiếu bảo trì
1. Vào **QLTS → Bảo trì** → **Tạo mới**
2. Chọn tài sản, nhà cung cấp, nhập chi phí và nội dung
3. Luồng phê duyệt: **Bắt đầu bảo trì → Hoàn thành → Ghi sổ chi phí**
4. Sau khi ghi sổ: nhấn **Xem bút toán** để kiểm tra

#### Thanh lý tài sản
1. Vào **QLTS → Thanh lý** → **Tạo mới**
2. Chọn tài sản, nhập giá trị thu hồi, thiết lập tài khoản kế toán
3. Luồng: **Gửi duyệt → Duyệt → Ghi sổ kế toán**
4. Hệ thống tự tính lãi/lỗ và tạo bút toán tổng hợp

#### Mượn / Trả tài sản
1. Vào **QLTS → Mượn trả** → **Tạo mới**
2. Chọn tài sản, người mượn, ngày mượn, ngày trả dự kiến
3. Nhấn **Xuất đơn mượn** để tải file DOCX
4. Khi trả: cập nhật ngày trả thực tế → **Hoàn thành**

#### Điều chuyển tài sản
1. Vào **QLTS → Điều chuyển** → **Tạo mới**
2. Chọn tài sản, nhập địa điểm cũ, địa điểm mới, lý do
3. Lịch sử điều chuyển tự động cập nhật trong tài sản

#### Lập ngân sách mua sắm
1. Vào **QLTS → Ngân sách → Ngân sách mua sắm** → **Tạo mới**
2. Chọn năm, loại tài sản, nhập số tiền kế hoạch
3. Theo dõi tỷ lệ thực hiện — hệ thống cảnh báo nếu vượt ngân sách

#### Xem báo cáo tài chính
1. Vào **QLTS → Báo cáo → Báo cáo tài chính tài sản**
2. Chọn năm báo cáo → nhấn **Làm mới dữ liệu**
3. Xem tổng quan tài chính và chi tiết từng tài sản

### Module Quản lý Nhân sự

1. **Tạo phòng ban**: Nhân sự → Phòng ban → Tạo mới
2. **Tạo chức vụ**: Nhân sự → Chức vụ → Tạo mới
3. **Tạo nhân viên**: Nhân sự → Nhân viên → Tạo mới
   - Nhập họ tên, ngày sinh (**bắt buộc > 18 tuổi**)
   - Chọn phòng ban và chức vụ
   - Lịch sử làm việc tự động ghi lại khi thay đổi chức vụ/phòng ban

### Module Quản lý Văn bản

1. Vào **Văn bản → Văn bản đi** → **Tạo mới**
2. Nhập số hiệu, ngày ban hành, trích yếu nội dung
3. Chọn người ký, đơn vị nhận
4. Đính kèm file (nếu có) → Lưu

---

## Phân quyền

Tất cả models cấp quyền **đọc/tạo/sửa/xóa** cho `base.group_user` (mọi người dùng đã đăng nhập).

Để phân quyền theo nhóm riêng, chỉnh file `security/ir.model.access.csv` của từng module và thêm group tương ứng.

---

## Thông tin nhóm

**Nhóm:** CNTT-17-03-N11  
**Repository:** https://github.com/huzgnm/CNTT-17-03-N11  
**Email:** huzgnm@gmail.com
