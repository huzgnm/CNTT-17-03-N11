# -*- coding: utf-8 -*-
{
    'name': "Quản lý Văn bản",

    'summary': "Quản lý văn bản đi trong tổ chức",

    'description': "Module quản lý văn bản đi: theo dõi, lưu trữ và tra cứu văn bản.",

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
        'views/van_ban_di.xml',
        'views/menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
