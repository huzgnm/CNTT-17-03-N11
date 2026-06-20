---
![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)
![GitLab](https://img.shields.io/badge/gitlab-%23181717.svg?style=for-the-badge&logo=gitlab&logoColor=white)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)

> **Nhom:** CNTT-17-03-N11 &nbsp;|&nbsp; **GitHub:** [huzgnm](https://github.com/huzgnm) &nbsp;|&nbsp; **Nen tang:** Odoo 15 Community

---

# Muc luc

1. [Cai dat moi truong](#1-cai-dat-cong-cu-moi-truong-va-cac-thu-vien-can-thiet)
2. [Setup database](#2-setup-database)
3. [Setup tham so chay](#3-setup-tham-so-chay-cho-he-thong)
4. [Chay he thong](#4-chay-he-thong-va-cai-dat-cac-ung-dung-can-thiet)
5. [Module Quan ly Tai san](#5-module-quan-ly-tai-san-quan_ly_tai_san)
6. [Module Quan ly Nhan su](#6-module-quan-ly-nhan-su-nhan_su)
7. [Module Quan ly Tai chinh](#7-module-quan-ly-tai-chinh-quan_ly_tai_chinh)
8. [Tinh nang nang cap so voi ban goc](#8-tinh-nang-nang-cap-so-voi-ban-goc)

---

# 1. Cai dat cong cu, moi truong va cac thu vien can thiet

## 1.1. Clone project

```bash
git clone https://github.com/huzgnm/CNTT-17-03-N11.git
cd CNTT-17-03-N11
```

## 1.2. Cai dat cac thu vien can thiet

```bash
sudo apt-get install libxml2-dev libxslt-dev libldap2-dev libsasl2-dev \
  libssl-dev python3.10-distutils python3.10-dev build-essential \
  libssl-dev libffi-dev zlib1g-dev python3.10-venv libpq-dev
```

## 1.3. Khoi tao moi truong ao

```bash
python3.10 -m venv ./venv
source venv/bin/activate
pip3 install -r requirements.txt
```

## 1.4. Cai dat thu vien bo sung cho module tuy chinh

```bash
pip install python-docx
```

> **Luu y:** `python-docx` can thiet cho tinh nang xuat don muon tai san ra file `.docx`.

---

# 2. Setup database

Khoi tao database tren Docker:

```bash
sudo apt install docker-compose
sudo docker-compose up -d
```

---

# 3. Setup tham so chay cho he thong

## 3.1. Khoi tao odoo.conf

Tao tep **odoo.conf** voi noi dung:

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

# 4. Chay he thong va cai dat cac ung dung can thiet

```bash
python3 odoo-bin.py -c odoo.conf -u all
```

Truy cap: **http://localhost:8069/**

Sau khi dang nhap, vao **Settings -> Apps -> Update Apps List** va cai theo thu tu:

1. `Quan ly Nhan su` (`nhan_su`)
2. `Quan ly Tai san` (`quan_ly_tai_san`)
3. `Quan ly Tai chinh` (`quan_ly_tai_chinh`)

---

# 5. Module Quan ly Tai san (`quan_ly_tai_san`)

> **Phien ban:** 0.2 &nbsp;|&nbsp; **Phu thuoc:** `base`, `mail`, `nhan_su`

Module quan ly toan bo vong doi tai san co dinh cua doanh nghiep.

## 5.1. Cau truc thu muc

```
addons/quan_ly_tai_san/
├── models/
│   ├── tai_san.py                    # Tai san co dinh (model trung tam)
│   ├── bao_tri.py                    # Bao tri tai san
│   ├── thanh_ly.py                   # Thanh ly tai san
│   ├── muon_tra.py                   # Muon / tra tai san
│   ├── dieu_chuyen_tai_san.py        # Dieu chuyen tai san
│   ├── don_muon.py                   # Xuat don muon DOCX
│   ├── thong_ke.py                   # Thong ke tai san
│   ├── danh_muc_loai_tai_san.py      # Danh muc loai tai san
│   ├── nha_cung_cap.py               # Nha cung cap
│   ├── lich_su_su_dung_tai_san.py    # Lich su su dung
│   ├── lich_su_quan_ly_tai_san.py    # Lich su quan ly
│   └── lich_su_dieu_chuyen_tai_san.py
├── views/                            # 13 file XML views
├── security/ir.model.access.csv
└── __manifest__.py
```

## 5.2. Tinh nang chinh

### Quan ly tai san co ban
- Tao tai san voi ma tu sinh (`TS00001`, `TS00002`, ...)
- Trang thai vong doi: `Dang su dung -> Bao tri -> Hong -> Da thanh ly`
- Canh bao bao tri tu dong khi tai san chua bao tri > 180 ngay
- Luu lich su day du: su dung, quan ly, dieu chuyen
- Scan ma vach / barcode

### Khau hao tai san
- Phuong phap duong thang: `Gia tri / Thoi gian su dung / 12`
- Tinh toan tu dong: khau hao moi nam, moi thang, gia tri con lai
- Ty le khau hao lay tu danh muc loai tai san

### Bao tri tai san
Luong: **Cho duyet -> Dang bao tri -> Da xong**

- Ghi nhan chi phi bao tri, don vi thuc hien
- **Trigger Muc 2:** Hoan thanh bao tri -> tu dong tao Phieu chi trong module Tai chinh
- Canh bao lich su bao tri tren form tai san

### Thanh ly tai san
Luong: **Cho duyet -> Da duyet**

- Tinh toan lai/lo thanh ly tu dong
- **Trigger Muc 2:** Duyet thanh ly -> tu dong tao Phieu thu trong module Tai chinh
- Cap nhat trang thai tai san -> "Da thanh ly"

### Muon / Tra tai san
- Theo doi nguoi muon, ngay muon, ngay tra du kien / thuc te
- Xuat **don muon dinh dang `.docx`** (dung `python-docx`)
- Kanban view theo trang thai

### Dieu chuyen tai san
- Ghi nhan dia diem cu -> moi, nguoi phe duyet
- Ma tu sinh `DC00001`

### Thong ke & Lich su
- Thong ke so luong tai san theo trang thai
- 3 loai lich su: su dung, quan ly, dieu chuyen

---

# 6. Module Quan ly Nhan su (`nhan_su`)

> **Phien ban:** 0.1 &nbsp;|&nbsp; **Phu thuoc:** `base`, `mail`

## 6.1. Cau truc

```
addons/nhan_su/
├── models/
│   ├── nhan_vien.py       # Nhan vien
│   ├── phong_ban.py       # Phong ban
│   └── chuc_vu.py         # Chuc vu
└── views/
```

## 6.2. Tinh nang chinh

- Quan ly nhan vien: ho ten, ma dinh danh, phong ban, chuc vu, email
- Lich su lam viec: chuyen phong ban, thay doi chuc vu
- Phan loai theo phong ban va chuc vu
- Thong ke nhan vien theo do tuoi

---

# 7. Module Quan ly Tai chinh (`quan_ly_tai_chinh`)

> **Phien ban:** 0.1 &nbsp;|&nbsp; **Phu thuoc:** `base`, `mail`, `nhan_su`, `quan_ly_tai_san`

Module quan ly thu chi, ngan sach va bao cao tai chinh. Nhan du lieu tu dong tu cac su kien tai san.

## 7.1. Cau truc thu muc

```
addons/quan_ly_tai_chinh/
├── models/
│   ├── phieu_thu_chi.py      # Phieu thu / chi
│   ├── ngan_sach.py          # Ngan sach tai chinh
│   └── bao_cao_tai_chinh.py  # Bao cao tai chinh tong hop
├── views/
│   ├── phieu_thu_chi.xml
│   ├── ngan_sach.xml
│   ├── bao_cao_tai_chinh.xml
│   └── menu.xml
└── security/ir.model.access.csv
```

## 7.2. Tinh nang chinh

### Phieu Thu / Chi
- Luong: **Nhap -> Cho duyet -> Da duyet** (co the Huy)
- Phan loai nguon goc: Bao tri / Mua sam / Thanh ly / Luong / Khac
- Lien ket truc tiep voi tai san, phieu bao tri, phieu thanh ly
- Ma tu sinh: `PT00001` (thu), `PC00001` (chi)
- Tich hop chatter de theo doi lich su duyet

### Ngan sach
- Dat ngan sach thu / chi theo thang
- Theo doi % su dung ngan sach (progressbar)
- Canh bao khi vuot ngan sach

### Bao cao Tai chinh
- Tong hop thu / chi theo ky (thang / quy / nam)
- Tinh toan can doi: Tong thu - Tong chi
- Duyet bao cao boi quan ly

### Triggers tu dong (Muc 2)
| Su kien | Ket qua tu dong |
|---------|----------------|
| Bao tri hoan thanh | Tao Phieu chi (chi phi bao tri) |
| Thanh ly duoc duyet | Tao Phieu thu (thu hoi tai san) |

---

# 8. Tinh nang nang cap so voi ban goc

| # | Tinh nang | Module |
|---|-----------|--------|
| 1 | Ma tu sinh cho tat ca model (TS, BC, TL, DC, PT, PC...) | Tat ca |
| 2 | Chatter / mail.thread tren tat ca form chinh | Tat ca |
| 3 | Kanban view cho Tai san, Muon tra, Bao tri, Phieu thu chi | QLTS / QLTC |
| 4 | Canh bao bao tri tu dong (> 180 ngay) | QLTS |
| 5 | Tinh toan khau hao tu dong (nam / thang / gia tri con lai) | QLTS |
| 6 | Ket noi Nha cung cap vao Bao tri | QLTS |
| 7 | Scan ma vach / barcode | QLTS |
| 8 | Xuat don muon DOCX | QLTS |
| 9 | Module Tai chinh doc lap (Phieu thu/chi, Ngan sach, Bao cao) | QLTC |
| 10 | Trigger Muc 2: Bao tri xong -> tu dong tao Phieu chi | QLTS -> QLTC |
| 11 | Trigger Muc 2: Thanh ly duyet -> tu dong tao Phieu thu | QLTS -> QLTC |
| 12 | Lich su su dung / quan ly / dieu chuyen tai san | QLTS |
| 13 | Thong ke tai san theo trang thai | QLTS |
| 14 | Tinh toan lai/lo thanh ly tu dong | QLTS |
| 15 | Canh bao het han bao hanh tai san | QLTS |
