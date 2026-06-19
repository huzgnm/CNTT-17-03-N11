from odoo import models, fields, api

class SoLuongHon18(models.Model):
    _name = 'so_luong_hon_18'
    _description = 'Bảng chứa thông tin số lượng nhân viên trên 18 tuổi'

    so_luong_nhan_vien_tren_18 = fields.Integer(
        string="Số lượng nhân viên trên 18 tuổi", 
        compute="_compute_so_luong", 
        store=False  # Không lưu vào database, chỉ tính toán khi cần
    )

    so_luong_nhan_vien_duoi_18 = fields.Integer(
        string="Số lượng nhân viên dưới 18 tuổi", 
        compute="_compute_so_luong", 
        store=False  # Không lưu vào database, chỉ tính toán khi cần
    )

    @api.depends()
    def _compute_so_luong(self):
        for record in self:
            record.so_luong_nhan_vien_tren_18 = self.env["nhan_vien"].search_count([("tuoi", ">", 18)])
            record.so_luong_nhan_vien_duoi_18 = self.env["nhan_vien"].search_count([("tuoi", "<", 18)])
