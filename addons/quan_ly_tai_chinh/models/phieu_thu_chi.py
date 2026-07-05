# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError
from ..utils.telegram_helper import send_telegram_message


class PhieuThuChi(models.Model):
    _name = "tai_chinh.phieu_thu_chi"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Phieu thu/chi tai chinh"
    _rec_name = "ma_phieu"
    _order = "ngay_lap desc, id desc"

    ma_phieu = fields.Char("Ma phieu", required=True, copy=False, readonly=True, default="New")
    loai_phieu = fields.Selection([
        ("thu", "Phieu thu"),
        ("chi", "Phieu chi"),
    ], string="Loai phieu", required=True, default="chi", tracking=True)
    nguon_goc = fields.Selection([
        ("bao_tri", "Chi phi bao tri tai san"),
        ("mua_sam", "Mua sam tai san"),
        ("thanh_ly", "Thu thanh ly tai san"),
        ("luong", "Chi luong nhan vien"),
        ("khac", "Khac"),
    ], string="Nguon goc", required=True, default="khac")
    ten_noi_dung = fields.Char("Noi dung", required=True)
    so_tien = fields.Float("So tien (VND)", required=True)
    ngay_lap = fields.Date("Ngay lap", required=True, default=fields.Date.today)
    ngay_duyet = fields.Date("Ngay duyet", readonly=True)

    nguoi_lap_id = fields.Many2one("nhan_vien", string="Nguoi lap", required=True)
    nguoi_duyet_id = fields.Many2one("nhan_vien", string="Nguoi duyet")
    phong_ban_id = fields.Many2one(
        related="nguoi_lap_id.phong_ban_id", string="Phong ban", readonly=True
    )

    tai_san_id = fields.Many2one("tai_san", string="Tai san lien quan")
    bao_tri_id = fields.Many2one("bao_tri", string="Phieu bao tri")
    thanh_ly_id = fields.Many2one("thanh_ly", string="Phieu thanh ly")
    ngan_sach_id = fields.Many2one("tai_chinh.ngan_sach", string="Ngan sach")

    ghi_chu = fields.Text("Ghi chu")
    trang_thai = fields.Selection([
        ("nhap", "Nhap"),
        ("cho_duyet", "Cho duyet"),
        ("da_duyet", "Da duyet"),
        ("huy", "Da huy"),
    ], string="Trang thai", default="nhap", tracking=True)

    @api.model
    def create(self, vals):
        if vals.get("ma_phieu", "New") == "New":
            prefix = "PT" if vals.get("loai_phieu") == "thu" else "PC"
            last = self.search(
                [("loai_phieu", "=", vals.get("loai_phieu"))], order="id desc", limit=1
            )
            num = int(last.ma_phieu[2:]) if last and len(last.ma_phieu) > 2 else 0
            vals["ma_phieu"] = "%s%05d" % (prefix, num + 1)
        record = super(PhieuThuChi, self).create(vals)
        if record.nguon_goc in ("bao_tri", "thanh_ly"):
            loai_text = "THU" if record.loai_phieu == "thu" else "CHI"
            msg = (
                "\U0001F4CB <b>PHIEU %s TU DONG</b>\n"
                "Ma phieu: <code>%s</code>\n"
                "Noi dung: %s\n"
                "So tien: <b>%s VND</b>\n"
                "Nguon goc: %s"
            ) % (
                loai_text,
                record.ma_phieu,
                record.ten_noi_dung,
                "{:,.0f}".format(record.so_tien),
                dict(self._fields["nguon_goc"].selection).get(record.nguon_goc, record.nguon_goc),
            )
            send_telegram_message(self.env, msg)
        return record

    def action_gui_duyet(self):
        for rec in self:
            if rec.trang_thai != "nhap":
                raise UserError("Chi co the gui duyet tu trang thai Nhap.")
            rec.trang_thai = "cho_duyet"
            rec.message_post(body="Phieu da duoc gui duyet.")

    def action_duyet(self):
        for rec in self:
            if rec.trang_thai != "cho_duyet":
                raise UserError("Chi co the duyet tu trang thai Cho duyet.")
            rec.trang_thai = "da_duyet"
            rec.ngay_duyet = fields.Date.today()
            rec.message_post(body="Phieu da duoc duyet.")
            msg = (
                "\U00002705 <b>PHIEU DA DUYET</b>\n"
                "Ma phieu: <code>%s</code>\n"
                "Noi dung: %s\n"
                "So tien: <b>%s VND</b>"
            ) % (
                rec.ma_phieu,
                rec.ten_noi_dung,
                "{:,.0f}".format(rec.so_tien),
            )
            send_telegram_message(self.env, msg)

    def action_huy(self):
        for rec in self:
            if rec.trang_thai == "da_duyet":
                raise UserError("Khong the huy phieu da duyet.")
            rec.trang_thai = "huy"
            rec.message_post(body="Phieu da bi huy.")
