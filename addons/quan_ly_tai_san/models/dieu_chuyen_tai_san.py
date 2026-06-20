# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class DieuChuyenTaiSan(models.Model):
    _name = 'dieu_chuyen_tai_san'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Quản lý điều chuyển tài sản'
    _rec_name = "ma_dieu_chuyen"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    ma_dieu_chuyen = fields.Char(
        "Mã điều chuyển", required=True, copy=False, readonly=True, default="New"
    )
    tai_san_id = fields.Many2one('tai_san', string="Mã tài sản", required=True)
    ten_tai_san = fields.Char(related='tai_san_id.ten_tai_san', string="Tên tài sản", readonly=True)
    tu_dia_diem = fields.Many2one('phong_ban', string="Địa điểm hiện tại", required=True)
    den_dia_diem = fields.Many2one('phong_ban', string="Địa điểm chuyển đi", required=True)
    ngay_dieu_chuyen = fields.Date("Thời gian điều chuyển", required=True, default=fields.Date.today)
    nhan_vien_id = fields.Many2one('nhan_vien', string="Mã phê duyệt", required=True)
    nguoi_phe_duyet = fields.Char(related='nhan_vien_id.ho_va_ten', string="Người phê duyệt", readonly=True)
    thong_ke_id = fields.Many2one('thong_ke', string="Thống kê liên quan")

    trang_thai = fields.Selection([
        ('cho_duyet', 'Chờ duyệt'),
        ('da_duyet', 'Đã duyệt'),
        ('hoan_thanh', 'Hoàn thành'),
    ], string="Trạng thái", default='cho_duyet')

    ghi_chu = fields.Text("Ghi chú")

    @api.constrains('tu_dia_diem', 'den_dia_diem')
    def _check_dia_diem(self):
        for record in self:
            if (record.tu_dia_diem and record.den_dia_diem
                    and record.tu_dia_diem == record.den_dia_diem):
                raise ValidationError(
                    "Địa điểm hiện tại và địa điểm chuyển đi không được trùng nhau!"
                )

    @api.model
    def create(self, vals):
        if vals.get('ma_dieu_chuyen', 'New') == 'New':
            last = self.search([], order="id desc", limit=1)
            last_num = 0
            if last and last.ma_dieu_chuyen and last.ma_dieu_chuyen.startswith("DC"):
                try:
                    last_num = int(last.ma_dieu_chuyen[2:])
                except ValueError:
                    last_num = 0
            vals['ma_dieu_chuyen'] = f"DC{last_num + 1:05d}"

        new_record = super().create(vals)

        # Ghi lịch sử điều chuyển
        self.env['lich_su_dieu_chuyen_tai_san'].create({
            'tai_san_id': new_record.tai_san_id.id,
            'tu_dia_diem': new_record.tu_dia_diem.id,
            'den_dia_diem': new_record.den_dia_diem.id,
            'ngay_dieu_chuyen': new_record.ngay_dieu_chuyen,
            'nhan_vien_id': new_record.nhan_vien_id.id,
            'trang_thai': new_record.trang_thai,
            'ghi_chu': new_record.ghi_chu,
        })
        return new_record
