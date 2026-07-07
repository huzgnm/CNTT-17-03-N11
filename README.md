![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)
![Odoo](https://img.shields.io/badge/Odoo%2015-714B67?style=for-the-badge&logo=odoo&logoColor=white)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Python](https://img.shields.io/badge/python-v3.10+-blue.svg)

# Hệ thống Quản lý Tài sản & Tài chính — CNTT-17-03-N11

> **Nhóm:** CNTT-17-03-N11 &nbsp;|&nbsp; **Nền tảng:** Odoo 15 Community &nbsp;|&nbsp; **Dựa trên bản gốc (K15):** [thang0305/TTDN-15-02-N3](https://github.com/thang0305/TTDN-15-02-N3)

Từ một module quản lý tài sản CRUD cơ bản của khoá 15, nhóm K17-N11 đã **tối ưu, sửa lỗi kế thừa** và **mở rộng thành hệ thống 3 module liên thông** quản lý toàn bộ vòng đời *tài sản → chi phí → dòng tiền → kế toán*, có tự động hoá, thông báo real-time và AI Agent.

---

## 1. Cài đặt & chạy

```bash
git clone https://github.com/huzgnm/CNTT-17-03-N11.git
cd CNTT-17-03-N11
python3.10 -m venv ./venv && source venv/bin/activate
pip3 install -r requirements.txt
pip install python-docx requests
python3 odoo-bin -c odoo.conf   # odoo.conf: addons_path = addons
```

Truy cập http://localhost:8069 → **Settings → Apps → Update Apps List**, cài theo thứ tự:
`nhan_su` → `quan_ly_tai_san` → `quan_ly_tai_chinh` (Odoo tự lo phụ thuộc).

---

## 2. Ba module

| Thư mục | Tên | Vai trò |
|---------|-----|---------|
| `nhan_su` | Quản lý Nhân sự | Nhân viên, phòng ban, chức vụ, lịch sử làm việc |
| `quan_ly_tai_san` | Quản lý Tài sản | Vòng đời tài sản: mua → dùng → bảo trì → thanh lý |
| `quan_ly_tai_chinh` | Quản lý Tài chính | Thu/chi, ngân sách, khấu hao, báo cáo, kế toán, AI |

---

## 3. Tối ưu & sửa lỗi kế thừa từ bản gốc K15

Bản gốc K15 là 1 module tài sản CRUD đơn giản, còn nhiều lỗi và thiếu chuẩn hoá. Nhóm đã:

| # | Tối ưu / Sửa lỗi |
|---|------------------|
| 1 | **Tách kiến trúc** từ 1 module lộn xộn thành 3 module rõ ràng, liên thông bằng `depends` |
| 2 | Sửa hàng loạt **lỗi field/model không tồn tại** trong view (bảo trì, thanh lý, tài sản) do refactor dang dở |
| 3 | Sửa **`@depends` sai** (`bao_tri.trang_thai` → `tinh_trang`), thêm field `tong_gia_tri`, sửa ghi lịch sử điều chuyển |
| 4 | Sửa **Dashboard không hiển thị số** (compute rỗng trên TransientModel → chuyển sang `default_get`) |
| 5 | Sửa **Thống kê tài sản đếm sai** (chỉ đếm bản ghi link One2many → đếm toàn bộ tài sản theo trạng thái) |
| 6 | Dọn **quyền truy cập & menu trỏ model đã xoá**, thêm phụ thuộc `account` còn thiếu |
| 7 | Chuẩn hoá **mã tự sinh** (TS/BC/TL/DC/PT/PC…), trạng thái vòng đời, tính lãi/lỗ thanh lý |
| 8 | **Việt hoá toàn bộ giao diện có dấu**, gom cấu hình rải rác về một trang duy nhất |

---

## 4. Chức năng chính mới thêm

### 4.1. Module Tài chính (hoàn toàn mới)
Phiếu thu/chi có luồng duyệt · ngân sách theo tháng + cảnh báo vượt · ngân sách mua sắm · khấu hao hàng tháng + **cron ngày 1** · sinh **bút toán kế toán** (`account.move`) · báo cáo tài sản.

### 4.2. Tự động hoá liên module
- Bảo trì hoàn thành → **tự tạo Phiếu chi**
- Thanh lý được duyệt → **tự tạo Phiếu thu**

### 4.3. Thông báo real-time
**Telegram Bot** + **Email (SMTP)** gửi khi tạo/duyệt phiếu, bảo trì, thanh lý; bật/tắt từng kênh.

### 4.4. Dashboard KPI trực quan
Thẻ KPI có màu + icon: tài sản theo trạng thái, bảo trì, thu/chi tháng, khấu hao — tính real-time khi mở.

### 4.5. AI Agent (Gemini) — điểm nhấn
- **Chat widget nổi** góc màn hình, hỏi đáp tiếng Việt.
- **AI Agent tự thao tác** qua *function calling*: tra cứu số liệu thật, **tạo / sửa / xoá bản ghi, duyệt phiếu** trên mọi model bằng ngôn ngữ tự nhiên.
- **Phân tích AI** trên báo cáo tài sản (nhận xét & khuyến nghị).
- Gọi AI qua endpoint OpenAI-compatible (**9Router**), cấu hình base URL / key / model.

### 4.6. Tiện ích khác
Kanban, chatter (mail.thread), quét barcode, xuất đơn mượn `.docx`, dữ liệu mẫu ngành linh kiện điện tử, trang Cấu hình tập trung.

---

## 5. Cấu hình nhanh

Vào **Quản lý Tài chính → Cấu hình → Cài đặt**:

| Mục | Giá trị |
|-----|---------|
| Telegram Bot Token / Chat ID | Lấy từ @BotFather |
| Email nhận thông báo | Cần Outgoing Mail Server (Settings → Technical) |
| AI Base URL | `http://localhost:20128/v1` (9Router) hoặc URL tunnel |
| AI API Key / Model | `sk-...` / `gemini-2.5-flash` |

---

## Thông tin nhóm

| | |
|-|-|
| **Nhóm** | CNTT-17-03-N11 |
| **Trường** | Đại học Đại Nam — Khoa Công nghệ Thông tin |
| **Repository** | https://github.com/huzgnm/CNTT-17-03-N11 |
| **Dựa trên** | https://github.com/thang0305/TTDN-15-02-N3 |
