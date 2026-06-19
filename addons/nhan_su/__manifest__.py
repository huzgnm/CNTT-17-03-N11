# -*- coding: utf-8 -*-
{
    'name': "Quản lý Nhân sự",

    'summary': "Quản lý nhân viên, chức vụ, phòng ban và lịch sử làm việc",

    'description': "Module quản lý nhân sự: thông tin nhân viên, chức vụ, phòng ban, lịch sử công tác.",

    'author': "Nhóm CNTT-17-03-N11",
    'website': "https://github.com/huzgnm",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/nhan_vien.xml',
        'views/chuc_vu.xml',
        'views/phong_ban.xml',
        'views/lich_su_lam_viec.xml',
        'views/so_luong_hon_18.xml',
        'views/menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
