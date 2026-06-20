# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class NganSach(models.Model):
    _name = 'tai_chinh.ngan_sach'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Ngân sách tài chính'
    _rec_name = 'ten_ngan_sach'
    _order = 'nam desc, id desc'

    ma_ngan_sach = fields.Char(
        "Mã ngân sách", required=True, copy=False, readonly=True, default="New"
    )
    ten_ngan_sach = fields.Char("Tên ngân sách", required=True)
    nam = fields.Integer("Năm", required=True, default=lambda self: fields.Date.today().year)
    loai_ngan_sach = fields.Selection([
        ('mua_sam', 'Mua sắm tài sản'),
        ('bao_tri', 'Bảo trì tài sản'),
        ('van_hanh', 'Vận hành'),
        ('khac', 'Khác'),
    ], string="Loại ngân sách", required=True, default='bao_tri')

    tong_ngan_sach = fields.Float("Tổng ngân sách (VNĐ)", required=True)
    da_su_dung = fields.Float(
        "Đã sử dụng (VNĐ)", compute="_compute_da_su_dung", store=True
    )
    con_lai = fields.Float(
        "Còn lại (VNĐ)", compute="_compute_da_su_dung", store=True
    )
    phan_tram_su_dung = fields.Float(
        "% Sử dụng", compute="_compute_da_su_dung", store=True
    )
    canh_bao_vuot = fields.Boolean(
        "Vượt ngân sách", compute="_compute_da_su_dung", store=True
    )

    nguoi_lap_id = fields.Many2one('nhan_vien', string="Người lập", required=True)
    nguoi_duyet_id = fields.Many2one('nhan_vien', string="Người duyệt")
    ngay_lap = fields.Date("Ngày lập", default=fields.Date.today)
    ghi_chu = fields.Text("Ghi chú")

    trang_thai = fields.Selection([
        ('nhap', 'Nháp'),
        ('cho_duyet', 'Chờ duyệt'),
        ('da_duyet', 'Đã duyệt'),
        ('huy', 'Đã hủy'),
    ], string="Trạng thái", default='nhap', tracking=True)

    phieu_chi_ids = fields.One2many(
        'tai_chinh.phieu_thu_chi', 'ngan_sach_id', string="Phiếu chi liên quan"
    )

    @api.depends('phieu_chi_ids.so_tien', 'phieu_chi_ids.loai_phieu', 'phieu_chi_ids.trang_thai', 'tong_ngan_sach')
    def _compute_da_su_dung(self):
        for rec in self:
            chi = sum(
                p.so_tien for p in rec.phieu_chi_ids
                if p.loai_phieu == 'chi' and p.trang_thai == 'da_duyet'
            )
            rec.da_su_dung = chi
            rec.con_lai = rec.tong_ngan_sach - chi
            rec.phan_tram_su_dung = (chi / rec.tong_ngan_sach * 100) if rec.tong_ngan_sach else 0
            rec.canh_bao_vuot = chi > rec.tong_ngan_sach

    @api.model
    def create(self, vals):
        if vals.get('ma_ngan_sach', 'New') == 'New':
            last = self.search([], order='id desc', limit=1)
            num = int(last.ma_ngan_sach[2:]) if last and last.ma_ngan_sach.startswith('NS') else 0
            vals['ma_ngan_sach'] = f'NS{num + 1:05d}'
        return super().create(vals)

    def action_gui_duyet(self):
        self.write({'trang_thai': 'cho_duyet'})

    def action_duyet(self):
        self.write({'trang_thai': 'da_duyet'})

    def action_huy(self):
        self.write({'trang_thai': 'huy'})
