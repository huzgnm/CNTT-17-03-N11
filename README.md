![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)
![Odoo](https://img.shields.io/badge/Odoo%2015-714B67?style=for-the-badge&logo=odoo&logoColor=white)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Python](https://img.shields.io/badge/python-v3.10+-blue.svg)
![AI](https://img.shields.io/badge/AI%20Agent-Gemini-4285F4?style=for-the-badge&logo=googlegemini&logoColor=white)

# Hệ thống Quản lý Tài sản & Tài chính — CNTT-17-03-N11

> **Nhóm:** CNTT-17-03-N11 &nbsp;|&nbsp; **Nền tảng:** Odoo 15 Community (Python 3.10) &nbsp;|&nbsp; **Dựa trên bản gốc (K15):** [thang0305/TTDN-15-02-N3](https://github.com/thang0305/TTDN-15-02-N3)

Từ một module quản lý tài sản CRUD cơ bản của khoá 15, nhóm K17-N11 đã **tối ưu, sửa lỗi kế thừa** và **mở rộng thành hệ thống 3 module liên thông**, quản lý trọn vẹn vòng đời *tài sản → chi phí → dòng tiền → kế toán*, tích hợp **tự động hoá**, **thông báo real-time (Telegram + Email)** và **AI Agent (Gemini)** biết tự thao tác dữ liệu.

---

## Mục lục

1. [Giới thiệu & Kiến trúc](#1-giới-thiệu--kiến-trúc)
2. [Cài đặt & Triển khai](#2-cài-đặt--triển-khai)
3. [Chi tiết 3 module](#3-chi-tiết-3-module)
4. [Tối ưu & sửa lỗi kế thừa từ K15](#4-tối-ưu--sửa-lỗi-kế-thừa-từ-k15)
5. [Chức năng chính mới thêm](#5-chức-năng-chính-mới-thêm)
6. [Cấu hình (Telegram / Email / AI)](#6-cấu-hình-telegram--email--ai)
7. [Hướng dẫn dùng AI Agent](#7-hướng-dẫn-dùng-ai-agent)
8. [Tự động hoá (Triggers)](#8-tự-động-hoá-triggers)
9. [Xử lý sự cố thường gặp](#9-xử-lý-sự-cố-thường-gặp)

---

## 1. Giới thiệu & Kiến trúc

Hệ thống gồm **3 module tuỳ chỉnh** liên thông qua cơ chế `depends` của Odoo:

```
addons/
├── nhan_su/              # Quản lý Nhân sự (nhân viên, phòng ban, chức vụ)
├── quan_ly_tai_san/      # Quản lý Tài sản (vòng đời tài sản — module trung tâm)
└── quan_ly_tai_chinh/    # Quản lý Tài chính (thu/chi, ngân sách, khấu hao, AI)
```

| Module | Phụ thuộc | Vai trò |
|--------|-----------|---------|
| `nhan_su` | `base` | Hồ sơ nhân sự, phòng ban, chức vụ, lịch sử làm việc |
| `quan_ly_tai_san` | `base, mail, nhan_su, account` | Vòng đời tài sản: mua → dùng → bảo trì → thanh lý |
| `quan_ly_tai_chinh` | `base, mail, nhan_su, quan_ly_tai_san` | Thu/chi, ngân sách, khấu hao, báo cáo, AI |

---

## 2. Cài đặt & Triển khai

### 2.1. Thư viện hệ thống (Ubuntu)

```bash
sudo apt-get install libxml2-dev libxslt-dev libldap2-dev libsasl2-dev \
  libssl-dev python3.10-distutils python3.10-dev build-essential \
  libffi-dev zlib1g-dev python3.10-venv libpq-dev
```

### 2.2. Môi trường ảo & thư viện Python

```bash
git clone https://github.com/huzgnm/CNTT-17-03-N11.git
cd CNTT-17-03-N11
python3.10 -m venv ./venv
source venv/bin/activate
pip3 install -r requirements.txt
pip install python-docx requests
```

> `python-docx` cần cho xuất đơn mượn `.docx`; `requests` cần cho Telegram và AI.

### 2.3. Cấu hình `odoo.conf`

```ini
[options]
addons_path = addons
db_host = localhost
db_password = odoo
db_user = odoo
db_port = 5432
xmlrpc_port = 8069
```

### 2.4. Chạy & cài module

```bash
source venv/bin/activate
python3 odoo-bin -c odoo.conf
```

Truy cập **http://localhost:8069** → **Settings → Apps → Update Apps List**, cài theo thứ tự:

1. `nhan_su` (Quản lý Nhân sự)
2. `quan_ly_tai_san` (Quản lý Tài sản)
3. `quan_ly_tai_chinh` (Quản lý Tài chính)

Nâng cấp sau khi sửa code:
```bash
python3 odoo-bin -c odoo.conf -u nhan_su,quan_ly_tai_san,quan_ly_tai_chinh
```

---

## 3. Chi tiết 3 module

### 3.1. Quản lý Nhân sự (`nhan_su`)
Nhân viên (mã định danh, phòng ban, chức vụ, email, SĐT), phòng ban, chức vụ; lịch sử làm việc; ràng buộc nhân viên trên 18 tuổi; thống kê theo độ tuổi.

### 3.2. Quản lý Tài sản (`quan_ly_tai_san`) — module trung tâm

| Model | Mô tả | Mã tự sinh |
|-------|-------|-----------|
| `tai_san` | Tài sản cố định | `TS00001` |
| `bao_tri` | Phiếu bảo trì | `BC00001` |
| `thanh_ly` | Phiếu thanh lý | `TL00001` |
| `muon_tra` | Phiếu mượn/trả | `MT00001` |
| `dieu_chuyen_tai_san` | Phiếu điều chuyển | `DC00001` |
| `danh_muc_loai_tai_san`, `nha_cung_cap`, `thong_ke` | Danh mục, NCC, thống kê | — |

**Nghiệp vụ:** vòng đời `Đang dùng → Bảo trì → Hỏng → Thanh lý`; khấu hao đường thẳng (năm/tháng/giá trị còn lại); cảnh báo quá hạn bảo trì (>180 ngày) & hết bảo hành; barcode; hình ảnh; Kanban; xuất đơn mượn `.docx`; lịch sử sử dụng/điều chuyển/thanh lý.

### 3.3. Quản lý Tài chính (`quan_ly_tai_chinh`)

| Model | Mô tả |
|-------|-------|
| `tai_chinh.phieu_thu_chi` | Phiếu thu/chi (`PT/PC00001`) |
| `tai_chinh.ngan_sach` | Ngân sách thu/chi theo tháng |
| `tai_chinh.ngan_sach_mua_sam` | Ngân sách mua sắm theo năm/loại |
| `tai_chinh.khau_hao` | Khấu hao hàng tháng (+ cron ngày 1) |
| `tai_chinh.bao_cao_tai_san` | Báo cáo tài sản (+ phân tích AI) |
| `tai_chinh.dashboard` | Dashboard KPI (TransientModel) |
| `tai_chinh.cau_hinh` | Trang cấu hình tập trung |

**utils/:** `telegram_helper.py`, `notify_helper.py` (Telegram + Email), `ai_client.py` (OpenAI-compatible), `gemini_agent.py` (AI Agent function calling), `gemini_helper.py` (phân tích báo cáo).

---

## 4. Tối ưu & sửa lỗi kế thừa từ K15

Bản gốc K15 là 1 module tài sản CRUD đơn giản, còn nhiều lỗi và thiếu chuẩn hoá. Nhóm đã:

| # | Tối ưu / Sửa lỗi |
|---|------------------|
| 1 | **Tách kiến trúc** từ code lộn xộn thành 3 module rõ ràng, liên thông bằng `depends` |
| 2 | Sửa hàng loạt **lỗi field/model không tồn tại** trong view (bảo trì, thanh lý, tài sản) do refactor dang dở |
| 3 | Sửa **`@depends` sai** (`bao_tri.trang_thai` → `tinh_trang`), thêm field `tong_gia_tri`, sửa ghi lịch sử điều chuyển |
| 4 | Sửa **Dashboard không hiển thị số** (compute rỗng trên TransientModel → chuyển sang `default_get`, khoá readonly) |
| 5 | Sửa **Thống kê tài sản đếm sai** (chỉ đếm bản ghi link One2many → đếm toàn bộ tài sản theo trạng thái) |
| 6 | Dọn **quyền truy cập & menu trỏ tới model đã xoá**; thêm phụ thuộc `account` còn thiếu |
| 7 | Chuẩn hoá **mã tự sinh** (TS/BC/TL/DC/PT/PC…), trạng thái vòng đời, tính lãi/lỗ thanh lý |
| 8 | **Việt hoá toàn bộ giao diện có dấu**; gom cấu hình rải rác về một trang duy nhất |

---

## 5. Chức năng chính mới thêm

### 5.1. Module Tài chính (hoàn toàn mới)
Phiếu thu/chi có luồng duyệt `Nháp → Chờ duyệt → Đã duyệt` · ngân sách theo tháng + cảnh báo vượt · ngân sách mua sắm · khấu hao hàng tháng + **cron tự chạy ngày 1** · sinh **bút toán kế toán** (`account.move`) · báo cáo tài sản tổng hợp.

### 5.2. Tự động hoá liên module
- Bảo trì hoàn thành → **tự tạo Phiếu chi** (chi phí bảo trì)
- Thanh lý được duyệt → **tự tạo Phiếu thu** (thu hồi tài sản)

### 5.3. Thông báo real-time
**Telegram Bot** + **Email (SMTP)** gửi khi tạo/duyệt phiếu, bảo trì, thanh lý; bật/tắt từng kênh trong trang Cấu hình.

### 5.4. Dashboard KPI trực quan
Thẻ KPI có màu + icon, nhóm theo Tài sản / Bảo trì & Thanh lý / Thu chi tháng / Khấu hao; số liệu tính real-time khi mở, hiển thị tiền tệ VND.

### 5.5. AI Agent (Gemini) — điểm nhấn
- **Chat widget nổi** góc màn hình, hỏi đáp bằng tiếng Việt.
- **AI Agent tự thao tác** qua *function calling*: tra cứu số liệu thật, **tạo / sửa / xoá bản ghi, duyệt phiếu** trên mọi model bằng ngôn ngữ tự nhiên.
- **Phân tích AI** trên báo cáo tài sản (nhận xét & khuyến nghị).
- Gọi AI qua endpoint **OpenAI-compatible (9Router)** — cấu hình base URL / key / model linh hoạt, tự fallback về chat thường nếu lỗi.

### 5.6. Tiện ích khác
Kanban view, chatter (`mail.thread`), quét barcode, xuất đơn mượn `.docx`, dữ liệu mẫu ngành linh kiện điện tử, trang Cấu hình tập trung.

---

## 6. Cấu hình (Telegram / Email / AI)

Vào **Quản lý Tài chính → Cấu hình → Cài đặt**:

| Mục | Giá trị / Ghi chú |
|-----|-------------------|
| Bật Telegram + Bot Token + Chat ID | Token lấy từ @BotFather; Chat ID lấy qua `getUpdates` |
| Bật Email + Email nhận | Cần cấu hình **Outgoing Mail Server** (Settings → Technical) để gửi thật |
| AI Base URL | `http://localhost:20128/v1` (9Router chạy local: `npm i -g 9router`) hoặc URL tunnel |
| AI API Key | Token dạng `sk-...` |
| AI Model | `gemini-2.5-flash`, `gpt-4o-mini`… |

---

## 7. Hướng dẫn dùng AI Agent

1. Cấu hình AI ở bước (6).
2. Bấm **bong bóng 🤖** góc dưới màn hình (mọi trang).
3. Gõ yêu cầu bằng tiếng Việt, ví dụ:
   - *"Có bao nhiêu tài sản đang bảo trì?"* → tra cứu số liệu thật
   - *"Tạo 5 phiếu chi ngẫu nhiên"* / *"Duyệt tất cả phiếu thu đang nháp"* → tự thao tác
   - *"Tạo 10 nhân viên ngẫu nhiên"* / *"Đổi trạng thái TS00001 sang bảo trì"*

**Phân tích báo cáo:** Báo cáo → Báo cáo tài sản → New → *Tính toán* → *Phân tích AI (Gemini)*.

---

## 8. Tự động hoá (Triggers)

| Sự kiện | Kết quả tự động |
|---------|-----------------|
| Bảo trì hoàn thành | Tạo Phiếu chi (chi phí bảo trì) |
| Thanh lý được duyệt | Tạo Phiếu thu (thu hồi tài sản) |
| Tạo / duyệt phiếu | Gửi thông báo Telegram + Email |
| Ngày 1 hàng tháng | Tự tạo bản ghi khấu hao (cron) |

---

## 9. Xử lý sự cố thường gặp

| Triệu chứng | Nguyên nhân & cách xử lý |
|-------------|--------------------------|
| Dashboard toàn số 0 | Chưa có dữ liệu, hoặc chưa `-u`. Tạo tài sản/phiếu rồi mở lại menu Dashboard |
| Menu bị trùng/rác | Bản ghi menu cũ trong DB — chạy `-u` để Odoo dọn tự động |
| AI báo `404` | Sai Base URL/model — kiểm tra 9Router đang chạy, sửa trong trang Cài đặt |
| AI báo `401/403` | Sai API Key — nhập lại key `sk-...` |
| Email không gửi | Chưa cấu hình Outgoing Mail Server (Settings → Technical) |
| `ValueError: source code ... null bytes` | Lỗi ghi file trên NTFS — strip null bytes / ghi lại file |

---

## Thông tin nhóm

| | |
|-|-|
| **Nhóm** | CNTT-17-03-N11 |
| **Trường** | Đại học Đại Nam — Khoa Công nghệ Thông tin |
| **Repository** | https://github.com/huzgnm/CNTT-17-03-N11 |
| **Dựa trên** | https://github.com/thang0305/TTDN-15-02-N3 |
