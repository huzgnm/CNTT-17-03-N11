# -*- coding: utf-8 -*-
from odoo import api, fields, models
from ..utils.telegram_helper import send_telegram_message


class PhieuThuChi(models.Model):
    _name = "tai_chinh.phieu_thu_chi"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Phiếu thu/chi tài chính"
    _rec_name = "ma_phieu"
    _order = "ngay_lap desc, id desc"

    ma_phieu = fields.Char("Mã phiếu", required=True, copy=False, readonly=True, default="New")
    loai_phieu = fields.Selection([
        ("thu", "Phiếu thu"),
        ("chi", "Phiếu chi"),
    ], string="Loại phiếu", required=True, default="chi", tracking=True)
    nguon_goc = fields.Selection([
        ("bao_tri", "Chi phí bảo trì tài sản"),
        ("mua_sam", "Mua sắm tài sản"),
        ("thanh_ly", "Thu thanh lý tài sản"),
        ("luong", "Chi lương nhân viên"),
        ("khac", "Khác"),
    ], string="Nguồn gốc", required=True, default="khac")
    ten_noi_dung = fields.Char("Nội dung", required=True)
    so_tien = fields.Float("Số tiền (VND)", required=True)
    ngay_lap = fields.Date("Ngày lập", required=True, default=fields.Date.today)
    ngay_duyet = fields.Date("Ngày duyệt", readonly=True)

    nguoi_lap_id = fields.Many2one("nhan_vien", string="Người lập", required=True)
    nguoi_duyet_id = fields.Many2one("nhan_vien", string="Người duyệt")
    phong_ban_id = fields.Many2one(related="nguoi_lap_id.phong_ban_id", string="Phòng ban", readonly=True)

    tai_san_id = fields.Many2one("tai_san", string="Tài sản liên quan")
    bao_tri_id = fields.Many2one("bao_tri", string="Phiếu bảo trì")
    thanh_ly_id = fields.Many2one("thanh_ly", string="Phiếu thanh lý")
    ngan_sach_id = fields.Many2one("tai_chinh.ngan_sach", string="Ngân sách")

    ghi_chu = fields.Text("Ghi chú")
    trang_thai = fields.Selection([
        ("nhap", "Nháp"),
        ("cho_duyet", "Chờ duyệt"),
        ("da_duyet", "Đã duyệt"),
        ("huy", "Đã hủy"),
    ], string="Trạng thái", default="nhap", tracking=True)

    @api.model
    def create(self, vals):
        if vals.get("ma_phieu", "New") == "New":
            prefix = "PT" if vals.get("loai_phieu") == "thu" else "PC"
            last = self.search([("loai_phieu", "=", vals.get("loai_phieu"))], order="id desc", limit=1)
            num = int(last.ma_phieu[2:]) if last and len(last.ma_phieu) > 2 else 0
            vals["ma_phieu"] = "%s%05d" % (prefix, num + 1)
        record = super(PhieuThuChi, self).create(vals)
        # Neu phieu duoc tao tu trigger tu dong (nguon_goc != khac), gui thong bao Telegram
        if record.nguon_goc in ("bao_tri", "thanh_ly"):
            loai_text = "THU" if record.loai_phieu == "thu" else "CHI"
            msg = (
                u"\U0001F4CB <b>PHIEU {loai} TU DONG</b>\n"
                u"Ma phieu: <code>{ma}</code>\n