# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError


class BaoCaoTaiSan(models.Model):
    _name = "tai_chinh.bao_cao_tai_san"
    _description = "Báo cáo tài sản tổng hợp"
    _rec_name = "ma_bao_cao"
    _order = "nam_bao_cao desc, id desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    ma_bao_cao = fields.Char(
        "Mã báo cáo", required=True, copy=False, readonly=True, default="New"
    )
    nam_bao_cao = fields.Integer(
        "Năm báo cáo", required=True,
        default=lambda self: __import__("datetime").date.today().year
    )
    ngay_lap = fields.Date("Ngày lập", default=fields.Date.today, required=True)
    nguoi_lap_id = fields.Many2one("nhan_vien", string="Người lập")
    nguoi_duyet_id = fields.Many2one("nhan_vien", string="Người duyệt")
    ngay_duyet = fields.Date("Ngày duyệt", readonly=True)

    tong_tai_san = fields.Integer("Tong so tai san", readonly=True)
    tong_nguyen_gia = fields.Float("Tổng nguyên giá (VND)", readonly=True)
    tong_da_khau_hao = fields.Float("Tổng đã khấu hao (VND)", readonly=True)
    tong_gia_tri_con_lai = fields.Float("Tổng giá trị còn lại (VND)", readonly=True)
    tong_chi_phi_bao_tri = fields.Float("Tong chi phi bao tri nam (VND)", readonly=True)
    tong_thu_thanh_ly = fields.Float("Tong thu tu thanh ly (VND)", readonly=True)

    trang_thai = fields.Selection([
        ("nhap", "Nháp"),
        ("cho_duyet", "Chờ duyệt"),
        ("da_duyet", "Đã duyệt"),
    ], string="Trạng thái", default="nhap", tracking=True)

    ghi_chu = fields.Text("Ghi chú")
    chi_tiet_ids = fields.One2many(
        "tai_chinh.bao_cao_tai_san.chi_tiet", "bao_cao_id", string="Chi tiết theo loại"
    )

    @api.model
    def create(self, vals):
        if vals.get("ma_bao_cao", "New") == "New":
            last = self.search([], order="id desc", limit=1)
            num = 0
            if last and last.ma_bao_cao and last.ma_bao_cao.startswith("BC"):
                try:
                    num = int(last.ma_bao_cao[2:])
                except ValueError:
                    pass
            vals["ma_bao_cao"] = "BCTS%05d" % (num + 1)
        return super(BaoCaoTaiSan, self).create(vals)

    def action_tinh_toan(self):
        for rec in self:
            # Xoa chi tiet cu
            rec.chi_tiet_ids.unlink()

            tai_san_all = self.env["tai_san"].search([])
            rec.tong_tai_san = len(tai_san_all)
            rec.tong_nguyen_gia = sum(tai_san_all.mapped("gia_tri_tai_san"))
            rec.tong_da_khau_hao = sum(tai_san_all.mapped("tong_da_khau_hao"))
            rec.tong_gia_tri_con_lai = sum(tai_san_all.mapped("gia_tri_con_lai"))

            # Bao tri trong nam
            bao_tri_nam = self.env["bao_tri"].search([
                ("tinh_trang", "=", "da_xong"),
                ("ngay_bao_tri", ">=", "%s-01-01" % rec.nam_bao_cao),
                ("ngay_bao_tri", "<=", "%s-12-31" % rec.nam_bao_cao),
            ])
            rec.tong_chi_phi_bao_tri = sum(bao_tri_nam.mapped("chi_phi_bao_tri"))

            # Thanh ly trong nam
            thanh_ly_nam = self.env["thanh_ly"].search([
                ("trang_thai", "=", "da_duyet"),
                ("ngay_thanh_ly", ">=", "%s-01-01" % rec.nam_bao_cao),
                ("ngay_thanh_ly", "<=", "%s-12-31" % rec.nam_bao_cao),
            ])
            rec.tong_thu_thanh_ly = sum(thanh_ly_nam.mapped("gia_tri_thanh_ly"))

            # Chi tiet theo loai tai san
            loai_ts = self.env["danh_muc_loai_tai_san"].search([])
            for loai in loai_ts:
                ts_loai = tai_san_all.filtered(lambda t: t.danh_muc_loai_tai_san_id.id == loai.id)
                if not ts_loai:
                    continue
                self.env["tai_chinh.bao_cao_tai_san.chi_tiet"].create({
                    "bao_cao_id": rec.id,
                    "danh_muc_loai_tai_san_id": loai.id,
                    "so_tai_san": len(ts_loai),
                    "tong_nguyen_gia": sum(ts_loai.mapped("gia_tri_tai_san")),
                    "tong_da_khau_hao": sum(ts_loai.mapped("tong_da_khau_hao")),
                    "tong_gia_tri_con_lai": sum(ts_loai.mapped("gia_tri_con_lai")),
                })

            rec.trang_thai = "cho_duyet"
            rec.message_post(body="Da tinh toan bao cao.")

    def action_duyet(self):
        for rec in self:
            if rec.trang_thai != "cho_duyet":
                raise UserError("Chi co the duyet tu trang thai Cho duyet.")
            rec.trang_thai = "da_duyet"
            rec.ngay_duyet = fields.Date.today()
            rec.message_post(body="Bao cao da duoc duyet.")


class BaoCaoTaiSanChiTiet(models.Model):
    _name = "tai_chinh.bao_cao_tai_san.chi_tiet"
    _description = "Chi tiet bao cao tai san theo loai"
    _order = "danh_muc_loai_tai_san_id"

    bao_cao_id = fields.Many2one(
        "tai_chinh.bao_cao_tai_san", string="Báo cáo", required=True, ondelete="cascade"
    )
    danh_muc_loai_tai_san_id = fields.Many2one("danh_muc_loai_tai_san", string="Loại tài sản")
    so_tai_san = fields.Integer("So tai san")
    tong_nguyen_gia = fields.Float("Tổng nguyên giá (VND)", widget="monetary")
    tong_da_khau_hao = fields.Float("Tổng đã khấu hao (VND)")
    tong_gia_tri_con_lai = fields.Float("Tổng giá trị còn lại (VND)")
    ty_le_con_lai = fields.Float(
        "% Con lai", compute="_compute_ty_le", store=True
    )

    @api.depends("tong_nguyen_gia", "tong_gia_tri_con_lai")
    def _compute_ty_le(self):
        for rec in self:
            rec.ty_le_con_lai = (
                rec.tong_gia_tri_con_lai / rec.tong_nguyen_gia * 100
                if rec.tong_nguyen_gia else 0.0
            )
