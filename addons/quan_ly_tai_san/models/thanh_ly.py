# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError


class ThanhLy(models.Model):
    _name = "thanh_ly"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Phieu thanh ly tai san"
    _rec_name = "ma_thanh_ly"

    ma_thanh_ly = fields.Char(
        "Ma thanh ly", required=True, copy=False, readonly=True, default="New"
    )
    tai_san_id = fields.Many2one("tai_san", string="Tai san", required=True)
    nguoi_lap_id = fields.Many2one("nhan_vien", string="Nguoi lap bien ban", required=True)
    ngay_thanh_ly = fields.Date("Ngay thanh ly", required=True, default=fields.Date.today)
    ly_do = fields.Text("Ly do thanh ly", required=True)
    gia_tri_con_lai = fields.Float(
        "Gia tri con lai (VND)", related="tai_san_id.gia_tri_con_lai", readonly=True
    )
    gia_tri_thanh_ly = fields.Float("Gia tri thu hoi (VND)")
    lai_lo_thanh_ly = fields.Float(
        "Lai/(Lo) thanh ly (VND)", compute="_compute_lai_lo", store=True
    )

    trang_thai = fields.Selection(
        [
            ("cho_duyet", "Cho duyet"),
            ("da_duyet", "Da duyet"),
            ("huy", "Da huy"),
        ],
        string="Trang thai",
        default="cho_duyet",
        tracking=True,
    )
    ghi_chu = fields.Text("Ghi chu")

    @api.depends("gia_tri_thanh_ly", "gia_tri_con_lai")
    def _compute_lai_lo(self):
        for rec in self:
            rec.lai_lo_thanh_ly = rec.gia_tri_thanh_ly - rec.gia_tri_con_lai

    @api.model
    def create(self, vals):
        if vals.get("ma_thanh_ly", "New") == "New":
            last = self.search([], order="id desc", limit=1)
            num = (
                int(last.ma_thanh_ly[2:])
                if last and last.ma_thanh_ly.startswith("TL")
                else 0
            )
            vals["ma_thanh_ly"] = "TL%05d" % (num + 1)
        return super(ThanhLy, self).create(vals)

    def action_duyet(self):
        for rec in self:
            if rec.trang_thai != "cho_duyet":
                raise UserError("Chi co the duyet tu trang thai Cho duyet.")
            rec.trang_thai = "da_duyet"
            rec.tai_san_id.write({"trang_thai": "da_thanh_ly"})
            rec.message_post(body="Phieu thanh ly da duoc duyet. Tai san chuyen sang Da thanh ly.")
            if rec.gia_tri_thanh_ly > 0:
                phieu = self.env["tai_chinh.phieu_thu_chi"].create({
                    "loai_phieu": "thu",
                    "nguon_goc": "thanh_ly",
                    "ten_noi_dung": "Thu tu thanh ly tai san: %s (%s)" % (
                        rec.tai_san_id.ten_tai_san, rec.ma_thanh_ly
                    ),
                    "so_tien": rec.gia_tri_thanh_ly,
                    "tai_san_id": rec.tai_san_id.id,
                    "thanh_ly_id": rec.id,
                    "nguoi_lap_id": rec.nguoi_lap_id.id,
                    "trang_thai": "cho_duyet",
                })
                rec.message_post(
                    body="Tu dong tao phieu thu tai chinh %s: %s VND" % (
                        phieu.ma_phieu, rec.gia_tri_thanh_ly
                    )
                )

    def action_huy(self):
        for rec in self:
            if rec.trang_thai == "da_duyet":
                raise UserError("Khong the huy phieu da duyet.")
            rec.trang_thai = "huy"
            rec.message_post(body="Phieu thanh ly da bi huy.")
