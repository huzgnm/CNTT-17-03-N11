# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError


class NganSachMuaSam(models.Model):
    _name = "tai_chinh.ngan_sach_mua_sam"
    _description = "Ngan sach mua sam tai san"
    _rec_name = "ma_ngan_sach"
    _order = "nam desc, id desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    ma_ngan_sach = fields.Char(
        "Ma ngan sach", required=True, copy=False, readonly=True, default="New"
    )
    nam = fields.Integer("Nam ke hoach", required=True, default=lambda self: __import__("datetime").date.today().year)
    danh_muc_loai_tai_san_id = fields.Many2one(
        "danh_muc_loai_tai_san", string="Loai tai san", required=True
    )
    so_tien_ke_hoach = fields.Float("So tien ke hoach (VND)", required=True)
    so_tien_thuc_te = fields.Float(
        "So tien thuc te (VND)", compute="_compute_thuc_te", store=True
    )
    chenh_lech = fields.Float(
        "Chenh lech (VND)", compute="_compute_thuc_te", store=True
    )
    phan_tram_su_dung = fields.Float(
        "% Su dung", compute="_compute_thuc_te", store=True
    )
    canh_bao_vuot = fields.Boolean(
        "Canh bao vuot ngan sach", compute="_compute_thuc_te", store=True
    )
    trang_thai = fields.Selection([
        ("nhap", "Nhap"),
        ("da_duyet", "Da duyet"),
        ("huy", "Da huy"),
    ], string="Trang thai", default="nhap", tracking=True)
    ghi_chu = fields.Text("Ghi chu")
    chi_tiet_ids = fields.One2many(
        "tai_chinh.ngan_sach_mua_sam.chi_tiet", "ngan_sach_id", string="Chi tiet theo thang"
    )

    @api.depends("so_tien_ke_hoach", "chi_tiet_ids.so_tien_thuc_te")
    def _compute_thuc_te(self):
        for rec in self:
            thuc_te = sum(rec.chi_tiet_ids.mapped("so_tien_thuc_te"))
            rec.so_tien_thuc_te = thuc_te
            rec.chenh_lech = rec.so_tien_ke_hoach - thuc_te
            rec.phan_tram_su_dung = (thuc_te / rec.so_tien_ke_hoach * 100) if rec.so_tien_ke_hoach else 0.0
            rec.canh_bao_vuot = thuc_te > rec.so_tien_ke_hoach

    @api.model
    def create(self, vals):
        if vals.get("ma_ngan_sach", "New") == "New":
            last = self.search([], order="id desc", limit=1)
            num = 0
            if last and last.ma_ngan_sach and last.ma_ngan_sach.startswith("NS"):
                try:
                    num = int(last.ma_ngan_sach[2:])
                except ValueError:
                    pass
            vals["ma_ngan_sach"] = "NS%05d" % (num + 1)
        return super(NganSachMuaSam, self).create(vals)

    def action_duyet(self):
        for rec in self:
            if rec.trang_thai != "nhap":
                raise UserError("Chi co the duyet tu trang thai Nhap.")
            rec.trang_thai = "da_duyet"
            rec.message_post(body="Ngan sach da duoc duyet.")

    def action_huy(self):
        for rec in self:
            rec.trang_thai = "huy"


class NganSachMuaSamChiTiet(models.Model):
    _name = "tai_chinh.ngan_sach_mua_sam.chi_tiet"
    _description = "Chi tiet ngan sach mua sam theo thang"
    _order = "ten_thang"

    ngan_sach_id = fields.Many2one(
        "tai_chinh.ngan_sach_mua_sam", string="Ngan sach", required=True, ondelete="cascade"
    )
    ten_thang = fields.Selection([
        ("1","Thang 1"), ("2","Thang 2"), ("3","Thang 3"), ("4","Thang 4"),
        ("5","Thang 5"), ("6","Thang 6"), ("7","Thang 7"), ("8","Thang 8"),
        ("9","Thang 9"), ("10","Thang 10"), ("11","Thang 11"), ("12","Thang 12"),
    ], string="Thang", required=True)
    so_tien_ke_hoach = fields.Float("Ke hoach (VND)")
    so_tien_thuc_te = fields.Float("Thuc te (VND)")
    chenh_lech = fields.Float("Chenh lech (VND)", compute="_compute_chenh_lech", store=True)
    ghi_chu = fields.Char("Ghi chu")

    @api.depends("so_tien_ke_hoach", "so_tien_thuc_te")
    def _compute_chenh_lech(self):
        for rec in self:
            rec.chenh_lech = rec.so_tien_ke_hoach - rec.so_tien_thuc_te
