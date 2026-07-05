# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


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
    chi_phi_bao_tri = fields.Float("Chi phí bảo trì (VNĐ)")
    nha_cung_cap_id = fields.Many2one("nha_cung_cap", string="Đơn vị thực hiện", required=True)
    ghi_chu = fields.Text("Ghi chú")
    thong_ke_id = fields.Many2one("thong_ke", string="Thống kê liên quan")

    tinh_trang = fields.Selection([
        ("dang_cho_duyet", "Chờ duyệt"),
        ("dang_bao_tri", "Đang bảo trì"),
        ("da_xong", "Đã xong"),
        ("huy", "Đã hủy"),
    ], string="Tình trạng", default="dang_cho_duyet")


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
            vals["ma_bao_tri"] = f"BC{last_num + 1:05d}"
        return super().create(vals)

    def action_bat_dau_bao_tri(self):
        for rec in self:
            if rec.tinh_trang != "dang_cho_duyet":
                raise UserError("Chỉ có thể bắt đầu từ trạng thái Chờ duyệt.")
            rec.tai_san_id.write({"trang_thai": "bao_tri"})
            rec.tinh_trang = "dang_bao_tri"

    def action_hoan_thanh(self):
        for rec in self:
            if rec.tinh_trang != "dang_bao_tri":
                raise UserError("Phải ở trạng thái Đang bảo trì mới có thể hoàn thành.")
            rec.tai_san_id.write({"trang_thai": "dang_su_dung"})
            rec.tinh_trang = "da_xong"

            # ===== TRIGGER TỰ ĐỘNG (Mức 2) =====
            # Bảo trì hoàn thành → tự động tạo phiếu chi trong module Tài chính
            if rec.chi_phi_bao_tri > 0:
                nguoi_lap = rec.tai_san_id.nha_cung_cap_id and self.env['nhan_vien'].search([], limit=1)
                self.env['tai_chinh.phieu_thu_chi'].create({
                    'loai_phieu': 'chi',
                    'nguon_goc': 'bao_tri',
                    'ten_noi_dung': f'Chi phí bảo trì tài sản: {rec.tai_san_id.ten_tai_san} ({rec.ma_bao_tri})',
                    'so_tien': rec.chi_phi_bao_tri,
                    'tai_san_id': rec.tai_san_id.id,
                    'bao_tri_id': rec.id,
                    'nguoi_lap_id': self.env['nhan_vien'].search([], limit=1).id,
                    'trang_thai': 'cho_duyet',
                })
                rec.message_post(
                    body=f"✅ Tự động tạo phiếu chi tài chính: {rec.chi_phi_bao_tri:,.0f} VNĐ"
                )

    def action_huy(self):
        for rec in self:
            if rec.account_move_id and rec.account_move_id.state == "posted":
                rec.account_move_id.button_cancel()
                rec.account_move_id.button_draft()
                rec.account_mo