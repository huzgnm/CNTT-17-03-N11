# -*- coding: utf-8 -*-
{
    'name': "Quản lý Tài Chính",
    'summary': "Quản lý tài chính doanh nghiệp: ngân sách, thu chi, liên kết tài sản và nhân sự",
    'description': "Module quản lý tài chính: lập ngân sách, ghi nhận phiếu thu/chi, tự động tạo phiếu chi khi bảo trì hoàn thành hoặc thanh lý tài sản được duyệt.",
    'author': "Nhóm CNTT-17-03-N11",
    'website': "https://github.com/huzgnm",
    'category': 'Finance',
    'version': '0.1',
    'depends': ['base', 'mail', 'nhan_su', 'quan_ly_tai_san'],
    'data': [
        'security/ir.model.access.csv',
        'views/ngan_sach.xml',
        'views/phieu_thu_chi.xml',
        'views/bao_cao_tai_chinh.xml',
        'views/menu.xml',
    ],
    'license': 'LGPL-3',
}
