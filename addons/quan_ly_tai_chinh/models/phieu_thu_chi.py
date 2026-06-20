# -*- coding: utf-8 -*-
from odoo import api, fields, models


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
    phong_ban_id = fields.Many2one(related="nguoi_lap_id.phong_ban_id", string="Phong ban", readonly=True)

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
            last = self.search([("loai_phieu", "=", vals.get("loai_phieu"))], order="id desc", limit=1)
            num = int(last.ma_phieu[2:]) if last and len(last.ma_phieu) > 2 else 0
            vals["ma_phieu"] = "%s%05d" % (prefix, num + 1)
        return super(PhieuThuChi, self).create(vals)

    def action_gui_duyet(self):
        self.write({"trang_thai": "cho_duyet"})
        self.message_post(body="Phieu da duoc gui duyet.")

    def action_duyet(self):
        for rec in self:
            rec.write({"trang_thai": "da_duyet", "ngay_duyet": fields.Date.today()})
            rec.message_post(body="Phieu da duoc duyet.")

    def action_huy(self):
        self.write({"trang_thai": "huy"})
