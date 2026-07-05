# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError


class BaoTri(models.Model):
    _name = "bao_tri"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Bao tri tai san"
    _rec_name = "ma_bao_tri"

    ma_bao_tri = fields.Char(
        "Ma bao tri", required=True, copy=False, readonly=True, default="New"
    )
    tai_san_id = fields.Many2one("tai_san", string="Tai san", required=True)
    ten_tai_san = fields.Char(
        related="tai_san_id.ten_tai_san", string="Ten tai san", readonly=True
    )
    ngay_bao_tri = fields.Date("Ngay bao tri", default=fields.Date.today)
    noi_dung_bao_tri = fields.Text("Noi dung bao tri")
    chi_phi_bao_tri = fields.Float("Chi phi bao tri (VND)")
    nha_cung_cap_id = fields.Many2one("nha_cung_cap", string="Don vi thuc hien")
    ghi_chu = fields.Text("Ghi chu")
    thong_ke_id = fields.Many2one("thong_ke", string="Thong ke lien quan")

    tinh_trang = fields.Selection(
        [
            ("dang_cho_duyet", "Cho duyet"),
            ("dang_bao_tri", "Dang bao tri"),
            ("da_xong", "Da xong"),
            ("huy", "Da huy"),
        ],
        string="Tinh trang",
        default="dang_cho_duyet",
        tracking=True,
    )

    @api.model
    def create(self, vals):
        if vals.get("ma_bao_tri", "New") == "New":
            last = self.search([], order="id desc", limit=1)
            last_num = 0
            if last and last.ma_bao_tri and last.ma_bao_tri.startswith("BC"):
                try:
                    last_num = int(last.ma_bao_tri[2:])
                except ValueError:
                    last_num = 0
            vals["ma_bao_tri"] = "BC%05d" % (last_num + 1)
        return super().create(vals)

    def action_bat_dau_bao_tri(self):
        for rec in self:
            if rec.tinh_trang != "dang_cho_duyet":
                raise UserError("Chi co the bat dau tu trang thai Cho duyet.")
            rec.tai_san_id.write({"trang_thai": "bao_tri"})
            rec.tinh_trang = "dang_bao_tri"
            rec.message_post(body="Da bat dau bao tri.")

    def action_hoan_thanh(self):
        for rec in self:
            if rec.tinh_trang != "dang_bao_tri":
                raise UserError("Phai o trang thai Dang bao tri moi co the hoan thanh.")
            rec.tai_san_id.write({"trang_thai": "dang_su_dung"})
            rec.tinh_trang = "da_xong"
            rec.message_post(body="Bao tri hoan thanh.")

            # TRIGGER Muc 2: tu dong tao phieu chi
            if rec.chi_phi_bao_tri > 0:
                nguoi_lap = self.env["nhan_vien"].search([], limit=1)
                phieu = self.env["tai_chinh.phieu_thu_chi"].create({
                    "loai_phieu": "chi",
                    "nguon_goc": "bao_tri",
                    "ten_noi_dung": "Chi phi bao tri tai san: %s (%s)" % (
                        rec.tai_san_id.ten_tai_san, rec.ma_bao_tri
                    ),
                    "so_tien": rec.chi_phi_bao_tri,
                    "tai_san_id": rec.tai_san_id.id,
                    "bao_tri_id": rec.id,
                    "nguoi_lap_id": nguoi_lap.id if nguoi_lap else False,
                    "trang_thai": "cho_duyet",
                })
                rec.message_post(
                    body="Tu dong tao phieu chi tai chinh %s: %s VND" % (
                        phieu.ma_phieu, rec.chi_phi_bao_tri
                    )
                )

    def action_huy(self):
        for rec in self:
            if rec.tinh_trang in ("da_xong",):
                raise UserError("Khong the huy bao tri da hoan thanh.")
            rec.tinh_trang = "huy"
            rec.message_post(body="Bao tri da bi huy.")
