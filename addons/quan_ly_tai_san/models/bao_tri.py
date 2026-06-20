# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class BaoTri(models.Model):
    _name = "bao_tri"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Bảng chứa thông tin bảo trì, bảo dưỡng tài sản"
    _rec_name = "ma_bao_tri"

    ma_bao_tri = fields.Char(
        "Mã bảo trì", required=True, copy=False, readonly=True, default="New"
    )
    tai_san_id = fields.Many2one("tai_san", string="Tài sản", required=True)
    ten_tai_san = fields.Char(related="tai_san_id.ten_tai_san", string="Tên tài sản", readonly=True)
    ngay_bao_tri = fields.Date("Ngày bảo trì", default=fields.Date.today)
    noi_dung_bao_tri = fields.Text("Nội dung bảo trì")
    chi_phi_bao_tri = fields.Float("Chi phí bảo trì (VND)")
    nha_cung_cap_id = fields.Many2one("nha_cung_cap", string="Đơn vị thực hiện", required=True)
    ghi_chu = fields.Text("Ghi chú")
    thong_ke_id = fields.Many2one("thong_ke", string="Thống kê liên quan")

    tinh_trang = fields.Selection([
        ("dang_cho_duyet", "Chờ duyệt"),
        ("dang_bao_tri", "Đang bảo trì"),
        ("da_xong", "Đã xong"),
        ("huy", "Đã hủy"),
    ], string="Tình trạng", default="dang_cho_duyet", tracking=True)

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
        return super(BaoTri, self).create(vals)

    def action_bat_dau_bao_tri(self):
        for rec in self:
            if rec.tinh_trang != "dang_cho_duyet":
                raise UserError("Chỉ có thể bắt đầu từ trạng thái Chờ duyệt.")
            rec.tai_san_id.write({"trang_thai": "bao_tri"})
            rec.tinh_trang = "dang_bao_tri"
            rec.message_post(body="Bắt đầu bảo trì tài sản.")

    def action_hoan_thanh(self):
        for rec in self:
            if rec.tinh_trang != "dang_bao_tri":
                raise UserError("Phải ở trạng thái Đang bảo trì mới có thể hoàn thành.")
            rec.tai_san_id.write({"trang_thai": "dang_su_dung"})
            rec.tinh_trang = "da_xong"
            rec.message_post(body="Hoàn thành bảo trì. Tài sản đã trở về trạng thái sử dụng.")

            # TRIGGER Muc 2: tu dong tao phieu chi tai chinh
            if rec.chi_phi_bao_tri > 0:
                nguoi_lap = self.env["nhan_vien"].search([], limit=1)
                self.env["tai_chinh.phieu_thu_chi"].create({
                    "loai_phieu": "chi",
                    "nguon_goc": "bao_tri",
                    "ten_noi_dung": "Chi phi bao tri tai san: %s (%s)" % (
                        rec.tai_san_id.ten_tai_san, rec.ma_bao_tri),
                    "so_tien": rec.chi_phi_bao_tri,
                    "tai_san_id": rec.tai_san_id.id,
                    "bao_tri_id": rec.id,
                    "nguoi_lap_id": nguoi_lap.id if nguoi_lap else False,
                    "trang_thai": "cho_duyet",
                })
                rec.message_post(body="Tu dong tao phieu chi tai chinh: %s VND" % rec.chi_phi_bao_tri)

    def action_huy(self):
        for rec in self:
            if rec.tinh_trang in ("da_xong",):
                raise UserError("Không thể hủy phiếu bảo trì đã hoàn thành.")
            rec.tinh_trang = "huy"
            if rec.tai_san_id.trang_thai == "bao_tri":
                rec.tai_san_id.write({"trang_thai": "dang_su_dung"})
            rec.message_post(body="Phieu bao tri da bi huy.")
