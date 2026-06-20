# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError


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

    # Thiết lập kế toán
    journal_id = fields.Many2one(
        "account.journal", string="Sổ nhật ký",
        domain=[("type", "in", ["general", "purchase"])]
    )
    tai_khoan_chi_phi_id = fields.Many2one(
        "account.account", string="TK Chi phí bảo trì",
        help="Tài khoản ghi Nợ chi phí (vd: 6274, 6414, 6424)"
    )
    tai_khoan_phai_tra_id = fields.Many2one(
        "account.account", string="TK Phải trả nhà cung cấp",
        help="Tài khoản ghi Có (vd: 331 - Phải trả người bán)"
    )
    account_move_id = fields.Many2one(
        "account.move", string="Bút toán kế toán", readonly=True, copy=False
    )
    da_ghi_so = fields.Boolean("Đã ghi sổ", compute="_compute_da_ghi_so", store=True)

    @api.depends("account_move_id", "account_move_id.state")
    def _compute_da_ghi_so(self):
        for rec in self:
            rec.da_ghi_so = bool(rec.account_move_id and rec.account_move_id.state == "posted")

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

    def action_ghi_so_chi_phi(self):
        for rec in self:
            if rec.da_ghi_so:
                raise UserError(f"Bản ghi {rec.ma_bao_tri} đã ghi sổ rồi.")
            if rec.tinh_trang not in ("dang_bao_tri", "da_xong"):
                raise UserError("Chỉ ghi sổ khi đang bảo trì hoặc đã xong.")
            if not rec.chi_phi_bao_tri or rec.chi_phi_bao_tri <= 0:
                raise UserError("Chi phí bảo trì phải lớn hơn 0.")
            missing = []
            if not rec.journal_id:
                missing.append("Sổ nhật ký")
            if not rec.tai_khoan_chi_phi_id:
                missing.append("TK Chi phí bảo trì")
            if not rec.tai_khoan_phai_tra_id:
                missing.append("TK Phải trả nhà cung cấp")
            if missing:
                raise UserError(f"Chưa thiết lập: {', '.join(missing)}")

            move = self.env["account.move"].create({
                "journal_id": rec.journal_id.id,
                "date": rec.ngay_bao_tri or fields.Date.today(),
                "ref": f"Chi phí bảo trì {rec.tai_san_id.ma_tai_san} - {rec.ma_bao_tri}",
                "line_ids": [
                    (0, 0, {
                        "account_id": rec.tai_khoan_chi_phi_id.id,
                        "name": f"Chi phí bảo trì: {rec.ten_tai_san} - {rec.noi_dung_bao_tri or ''}",
                        "debit": rec.chi_phi_bao_tri,
                        "credit": 0.0,
                    }),
                    (0, 0, {
                        "account_id": rec.tai_khoan_phai_tra_id.id,
                        "name": f"Phải trả {rec.nha_cung_cap_id.name if rec.nha_cung_cap_id else ''} - {rec.ma_bao_tri}",
                        "debit": 0.0,
                        "credit": rec.chi_phi_bao_tri,
                    }),
                ],
            })
            move.action_post()
            rec.account_move_id = move.id

    def action_huy(self):
        for rec in self:
            if rec.account_move_id and rec.account_move_id.state == "posted":
                rec.account_move_id.button_cancel()
                rec.account_move_id.button_draft()
                rec.account_move_id.unlink()
            rec.write({"tinh_trang": "huy", "account_move_id": False})

    def action_xem_but_toan(self):
        self.ensure_one()
        if not self.account_move_id:
            raise UserError("Chưa có bút toán.")
        return {
            "type": "ir.actions.act_window",
            "name": "Bút toán chi phí bảo trì",
            "res_model": "account.move",
            "res_id": self.account_move_id.id,
            "view_mode": "form",
            "target": "current",
        }
