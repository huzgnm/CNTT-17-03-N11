from odoo import models, fields, api
from datetime import date

class NhanVien(models.Model):
    _name = 'nhan_vien'
    _description = 'Bảng chứa thông tin nhân viên'
    _rec_name = "ma_dinh_danh"

    ma_dinh_danh = fields.Char("Mã định danh", required=True)
    ho_ten_dem = fields.Char("Họ tên đệm", required=True)
    ten = fields.Char("Tên", required=True)
    ho_va_ten = fields.Char("Họ và tên", compute="_compute_ho_va_ten", store=True)
    ngay_sinh = fields.Date("Ngày sinh")
    tuoi = fields.Integer("Tuổi", compute="_compute_tuoi", store=True) 
    que_quan = fields.Char("Quê quán")
    email = fields.Char("Email")
    so_dien_thoai = fields.Char("Số điện thoại")
    lich_su_lam_viec_ids = fields.One2many(
        comodel_name="lich_su_lam_viec",
        inverse_name="nhan_vien_id",
        string="Danh sách lịch sử làm việc"
    )
    phong_ban_id = fields.Many2one('phong_ban', string="Phòng ban", required=True)
    chuc_vu_id = fields.Many2one('chuc_vu', string="Chức vụ", required=True)

    @api.depends("ho_ten_dem", "ten")
    def _compute_ho_va_ten(self):
        for record in self:
            record.ho_va_ten = f"{record.ho_ten_dem} {record.ten}" if record.ho_ten_dem and record.ten else ""

    @api.depends("ngay_sinh")
    def _compute_tuoi(self):
        for record in self:
            if record.ngay_sinh:
                today = date.today()
                record.tuoi = today.year - record.ngay_sinh.year - (
                    (today.month, today.day) < (record.ngay_sinh.month, record.ngay_sinh.day)
                )
            else:
                record.tuoi = 0  
