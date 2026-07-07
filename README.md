![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)
![Odoo](https://img.shields.io/badge/Odoo%2015-714B67?style=for-the-badge&logo=odoo&logoColor=white)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Python](https://img.shields.io/badge/python-v3.10+-blue.svg)

# Hệ thống Quản lý Tài sản & Tài chính — CNTT-17-03-N11

> **Nhóm:** CNTT-17-03-N11 &nbsp;|&nbsp; **Nền tảng:** Odoo 15 Community &nbsp;|&nbsp; **Dựa trên bản gốc (K15):** [thang0305/TTDN-15-02-N3](https://github.com/thang0305/TTDN-15-02-N3)

Phát triển từ một module quản lý tài sản CRUD cơ bản của khoá 15, nhóm mở rộng thành **hệ thống 3 module liên thông** quản lý toàn bộ vòng đời *tài sản → chi phí → dòng tiền → kế toán*, có **tự động hoá**, **thông báo real-time (Telegram + Email)** và **AI Agent (Gemini)** biết tự thao tác dữ liệu.

---

## 1. Cài đặt & chạy

```bash
git clone https://github.com/huzgnm/CNTT-17-03-N11.git
cd CNTT-17-03-N11
python3.10 -m venv ./venv && source venv/bin/activate
pip3 install -r requirements.txt
pip install python-docx requests

# odoo.conf: addons_path = addons
python3 odoo-bin -c odoo.conf
```

Truy cập http://localhost:8069 → **Settings → Apps → Update Apps List**, cài theo thứ tự (Odoo tự lo phụ thuộc):

1. `nhan_su` — Quản lý Nhân sự
2. `quan_ly_tai_san` — Quản lý Tài sản
3. `quan_ly_tai_chinh` — Quản lý Tài chính

---

## 2. Ba module

| Thư mục | Tên | Vai trò |
|---------|-----|---------|
| `nhan_su` | Quản lý Nhân sự | Nhân viên, phòng ban, chức vụ, lịch sử làm việc |
| `quan_ly_tai_san` | Quản lý Tài sản | Vòng đời tài sản: mua → dùng → bảo trì → thanh lý |
| `quan_ly_tai_chinh` | Quản lý Tài chính | Thu/chi, ngân sách, khấu hao, báo cáo, kế toán, AI |

---

## 3. Chức năng chính (nâng cấp so với bản gốc K15)

> Bản gốc K15 chỉ là **1 module quản lý tài sản CRUD**. Dưới đây là những gì nhóm K17-N11 phát triển thêm.

### 3.1. Kiến trúc & nghiệp vụ tài sản
- **1 module → 3 module liên thông** qua `depends`, dữ liệu chảy giữa các module.
- Vòng đời tài sản đầy đủ: trạng thái `Đang dùng → Bảo trì → Hỏng → Thanh lý`, **mã tự sinh** (TS/BC/TL/DC…).
- **Khấu hao đường thẳng** tự tính (năm/tháng/giá trị còn lại); **cảnh báo** quá hạn bảo trì (>180 ngày) & hết bảo hành.
- Bảo trì, thanh lý (tính lãi/lỗ), mượn/trả (xuất **đơn mượn `.docx`**), điều chuyển; lịch sử đầy đủ; barcode; Kanban.

### 3.2. Module Tài chính (hoàn toàn mới)
- Phiếu thu/chi có luồng duyệt; ngân sách theo tháng + cảnh báo vượt; ngân sách mua sắm.
- Khấu hao hàng tháng + **cron tự chạy ngày 1**; sinh **bút toán kế toán** (`account.move`).
- Báo cáo tài sản tổng hợp.

### 3.3. Tự động hoá (trigger liên module)
- Bảo trì hoàn thành → **tự tạo Phiếu chi**.
- Thanh lý được duyệt → **tự tạo Phiếu thu**.
- Cron khấu hao ngày 1 hàng tháng.

### 3.4. Thông báo real-time
- **Telegram Bot** + **Email (SMTP)** gửi khi tạo/duyệt phiếu, bảo trì, thanh lý.
- Bật/tắt từng kênh trong trang Cấu hình.

### 3.5. Dashboard KPI
- Thẻ KPI trực quan (màu + icon): tài sản theo trạng thái, bảo trì, thu/chi tháng, khấu hao.
- Số liệu tính real-time khi mở, hiển thị tiền tệ VND.

### 3.6. AI Agent (Gemini) — điểm nhấn
- **Chat widget nổi** góc màn hình + trợ lý hỏi đáp bằng tiếng Việt.
- **AI Agent tự thao tác** qua *function calling*: tra cứu số liệu thật, **tạo / sửa / xoá bản ghi, duyệt phiếu…** trên mọi model bằng ngôn ngữ tự nhiên.
- **Phân tích AI** trên báo cáo tài sản (nhận xét & khuyến nghị).
- Gọi AI qua endpoint OpenAI-compatible (**9Router**), cấu hình base URL / key / model linh hoạt.

### 3.7. Trang Cấu hình tập trung
- Gom **Telegram + Email + AI** vào một chỗ: **Quản lý Tài chính → Cấu hình → Cài đặt** (thay cho việc chỉnh System Parameters thủ công).

---

## 4. Cấu hình nhanh

Vào **Quản lý Tài chính → Cấu hình → Cài đặt**:

| Mục | Giá trị |
|-----|---------|
| Telegram Bot Token / Chat ID | Lấy từ @BotFather |
| Email nhận thông báo | Cần cấu hình Outgoing Mail Server (Settings → Technical) |
| AI Base URL | `http://localhost:20128/v1` (9Router local) hoặc URL tunnel |
| AI API Key | Token dạng `sk-...` |
| AI Model | `gemini-2.5-flash`… |

---

## Thông tin nhóm

| | |
|-|-|
| **Nhóm** | CNTT-17-03-N11 |
| **Trường** | Đại học Đại Nam — Khoa Công nghệ Thông tin |
| **Repository** | https://github.com/huzgnm/CNTT-17-03-N11 |
| **Dựa trên** | https://github.com/thang0305/TTDN-15-02-N3 |
