from odoo import models, fields

class LichSuLamViec(models.Model):
    _name = 'lich_su_lam_viec'
    _description = 'Bảng chứa lịch sử làm việc'

    nhan_vien_id = fields.Many2one('nhan_vien', string="Mã nhân viên", required=True)
    ho_va_ten = fields.Char(related='nhan_vien_id.ho_va_ten', string="Tên nhân viên", readonly=True)
    phong_ban_id = fields.Many2one(related='nhan_vien_id.phong_ban_id', string="Phòng ban", readonly=True)
    chuc_vu_id = fields.Many2one(related='nhan_vien_id.chuc_vu_id', string="Chức vụ", readonly=True)

    loai_chuc_vu = fields.Selection(
        [
            ("Chính", "Chính"),
            ("Kiêm nhiệm", "Kiêm nhiệm"),
        ],
        string="Loại chức vụ",
        default="Chính"
    )
    ngay_bat_dau = fields.Date("Ngày bắt đầu", required=True, default=fields.Date.today)
    ngay_ket_thuc = fields.Date("Ngày kết thúc")
