# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ThongKe(models.Model):
    _name = 'thong_ke'
    _description = "Bảng thống kê tài sản"
    _rec_name = "ma_thong_ke"

    ma_thong_ke = fields.Char("Mã thống kê", required=True, copy=False, readonly=True, default="New")
    tai_san_ids = fields.One2many('tai_san', 'thong_ke_id', string="Danh sách tài sản")

    tong_tai_san = fields.Integer("Tổng tài sản", compute="_compute_thong_ke", store=True)
    tong_so_luong_tai_san = fields.Integer("Tổng số lượng tài sản", compute="_compute_thong_ke", store=True)

    trang_thai = fields.Selection([
        ('dang_su_dung', 'Đang sử dụng'),
        ('hong', 'Hỏng'),
        ('mat', 'Mất'),
        ('bao_tri', 'Bảo trì'),
        ('sua_chua', 'Sửa chữa'),
        ('cho_cap_phat', 'Chờ cấp phát'),
    ], string="Trạng thái")

    so_luong_trang_thai = fields.Integer(
        "Số lượng theo trạng thái", compute="_compute_so_luong_trang_thai", store=True
    )

    @api.depends('tai_san_ids', 'tai_san_ids.so_luong')
    def _compute_thong_ke(self):
        for record in self:
            record.tong_tai_san = len(record.tai_san_ids)
            record.tong_so_luong_tai_san = sum(record.tai_san_ids.mapped('so_luong'))

    @api.depends('trang_thai', 'tai_san_ids', 'tai_san_ids.trang_thai')
    def _compute_so_luong_trang_thai(self):
        for record in self:
            if record.trang_thai:
                record.so_luong_trang_thai = len(record.tai_san_ids.filtered(
                    lambda ts: ts.trang_thai == record.trang_thai
                ))
            else:
                record.so_luong_trang_thai = 0

    @api.model
    def create(self, vals):
        if vals.get('ma_thong_ke', 'New') == 'New':
            last = self.search([], order="id desc", limit=1)
            last_num = int(last.ma_thong_ke[3:]) if last and last.ma_thong_ke.startswith("MTK") else 0
            vals['ma_thong_ke'] = f"MTK{last_num + 1:03d}"
        return super().create(vals)
