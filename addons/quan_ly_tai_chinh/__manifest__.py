# -*- coding: utf-8 -*-
{
    "name": "Quan ly Tai Chinh",
    "summary": "Quan ly tai chinh doanh nghiep: ngan sach, thu chi, lien ket tai san va nhan su",
    "description": "Module quan ly tai chinh: lap ngan sach, ghi nhan phieu thu/chi, tu dong tao phieu chi khi bao tri hoan thanh hoac thanh ly tai san duoc duyet.",
    "author": "Nhom CNTT-17-03-N11",
    "website": "https://github.com/huzgnm",
    "category": "Finance",
    "version": "0.1",
    "depends": ["base", "mail", "nhan_su", "quan_ly_tai_san"],
    "data": [
        "security/ir.model.access.csv",
        "views/ngan_sach.xml",
        "views/phieu_thu_chi.xml",
        "views/bao_cao_tai_chinh.xml",
        "views/menu.xml",
    ],
    "license": "LGPL-3",
}
