# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError


class ThanhLy(models.Model):
    _name = "thanh_ly"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Bảng chứa thông tin thanh lý tài sản"
    _rec_name = "ma_thanh_ly"

    ma_thanh_ly = fields.Char(
        "Mã thanh lý", required=True, copy=False, readonly=True, default="New"
    )
    tai_san_id = fields.Many2one("tai_san", string="Tài sản", required=True)
    ten_tai_san = fields.Char(
        related="tai_san_id.ten_tai_san", string="Tên tài sản", readonly=True, store=True
    )
    ngay_thanh_ly = fields.Date("Ngày thanh lý", default=fields.Date.today)
    gia_tri_thanh_ly = fields.Float("Giá trị thu hồi (VNĐ)")
    nha_cung_cap_id = fields.Many2one("nha_cung_cap", string="Đơn vị thanh lý", required=True)
    nhan_vien_id = fields.Many2one("nhan_vien", string="Người phê duyệt", required=True)
    nguoi_phe_duyet = fields.Char(
        related="nhan_vien_id.ho_va_ten", string="Họ tên người duyệt", readonly=True
    )
    chuc_vu_id = fields.Many2one(
        related="nhan_vien_id.chuc_vu_id", string="Chức vụ", readonly=True
    )
    ghi_chu = fields.Text("Ghi chú")
    thong_ke_id = fields.Many2one("thong_ke", string="Thống kê liên quan")

    # Thông tin tài chính tham chiếu từ tài sản
    nguyen_gia = fields.Float(
        "Nguyên giá (VNĐ)", related="tai_san_id.gia_tri_tai_san", readonly=True, store=True
    )
    da_khau_hao = fields.Float(
        "Đã khấu hao (VNĐ)", related="tai_san_id.tong_da_khau_hao", readonly=True, store=True
    )
    gia_tri_con_lai = fields.Float(
        "Giá trị còn lại (VNĐ)", related="tai_san_id.gia_tri_con_lai", readonly=True, store=True
    )
    lai_lo_thanh_ly = fields.Float(
        "Lãi/(Lỗ) thanh lý (VNĐ)", compute="_compute_lai_lo", store=True
    )

    # Thiết lập kế toán
    journal_id = fields.Many2one(
        "account.journal", string="Sổ nhật ký",
        domain=[("type", "in", ["general", "sale"])]
    )
    tai_khoan_nguyen_gia_id = fields.Many2one(
        "account.account", string="TK Nguyên giá tài sản",
        help="Ghi Có khi thanh lý (vd: 211)"
    )
    tai_khoan_luy_ke_id = fields.Many2one(
        "account.account", string="TK Khấu hao lũy kế",
        help="Ghi Nợ khi thanh lý (vd: 2141)"
    )
    tai_khoan_thu_hoi_id = fields.Many2one(
        "account.account", string="TK Thu hồi / Tiền mặt",
        help="Ghi Nợ cho phần tiền thu hồi (vd: 111, 131)"
    )
    tai_khoan_lai_id = fields.Many2one(
        "account.account", string="TK Lãi thanh lý",
        help="Ghi Có khi thu hồi > giá trị còn lại (vd: 711)"
    )
    tai_khoan_lo_id = fields.Many2one(
        "account.account", string="TK Lỗ thanh lý",
        help="Ghi Nợ khi thu hồi < giá trị còn lại (vd: 811)"
    )
    account_move_id = fields.Many2one(
        "account.move", string="Bút toán kế toán", readonly=True, copy=False
    )

    trang_thai = fields.Selection([
        ("nhap", "Nháp"),
        ("cho_duyet", "Chờ duyệt"),
        ("da_duyet", "Đã duyệt"),
        ("da_ghi_so", "Đã ghi sổ"),
        ("huy", "Đã hủy"),
    ], string="Trạng thái", default="nhap", readonly=True)

    @api.depends("gia_tri_thanh_ly", "gia_tri_con_lai")
    def _compute_lai_lo(self):
        for rec in self:
            rec.lai_lo_thanh_ly = rec.gia_tri_thanh_ly - rec.gia_tri_con_lai

    @api.model
    def create(self, vals):
        if vals.get("ma_thanh_ly", "New") == "New":
            last = self.search([], order="id desc", limit=1)
            last_num = 0
            if last and last.ma_thanh_ly and last.ma_thanh_ly.startswith("TL"):
                try:
                    last_num = int(last.ma_thanh_ly[2:])
                except ValueError:
                    last_num = 0
            vals["ma_thanh_ly"] = f"TL{last_num + 1:05d}"
        return super().create(vals)

    def action_cho_duyet(self):
        for rec in self:
            if rec.trang_thai != "nhap":
                raise UserError("Chỉ có thể gửi duyệt từ trạng thái Nháp.")
            rec.trang_thai = "cho_duyet"

    def action_duyet(self):
        for rec in self:
            if rec.trang_thai != "cho_duyet":
                raise UserError("Chỉ có thể duyệt từ trạng thái Chờ duyệt.")
            rec.trang_thai = "da_duyet"

    def action_ghi_so_thanh_ly(self):
        for rec in self:
            if rec.trang_thai != "da_duyet":
                raise UserError("Phải duyệt trước khi ghi sổ.")
            self._kiem_tra_tai_khoan(rec)

            ts = rec.tai_san_id
            nguyen_gia = ts.gia_tri_tai_san
            luy_ke = ts.tong_da_khau_hao
            thu_hoi = rec.gia_tri_thanh_ly
            lai_lo = thu_hoi - ts.gia_tri_con_lai

            lines = []
            if luy_ke > 0:
                lines.append((0, 0, {
                    "account_id": rec.tai_khoan_luy_ke_id.id,
                    "name": f"Xóa khấu hao lũy kế - {ts.ten_tai_san}",
                    "debit": luy_ke, "credit": 0.0,
                }))
            if thu_hoi > 0:
                lines.append((0, 0, {
                    "account_id": rec.tai_khoan_thu_hoi_id.id,
                    "name": f"Thu hồi từ thanh lý - {ts.ten_tai_san}",
                    "debit": thu_hoi, "credit": 0.0,
                }))
            if lai_lo < 0 and rec.tai_khoan_lo_id:
                lines.append((0, 0, {
                    "account_id": rec.tai_khoan_lo_id.id,
                    "name": f"Lỗ thanh lý tài sản - {ts.ten_tai_san}",
                    "debit": abs(lai_lo), "credit": 0.0,
                }))
            lines.append((0, 0, {
                "account_id": rec.tai_khoan_nguyen_gia_id.id,
                "name": f"Xóa nguyên giá tài sản - {ts.ten_tai_san}",
                "debit": 0.0, "credit": nguyen_gia,
            }))
            if lai_lo > 0 and rec.tai_khoan_lai_id:
                lines.append((0, 0, {
                    "account_id": rec.tai_khoan_lai_id.id,
                    "name": f"Lãi thanh lý tài sản - {ts.ten_tai_san}",
                    "debit": 0.0, "credit": lai_lo,
                }))

            move = self.env["account.move"].create({
                "journal_id": rec.journal_id.id,
                "date": rec.ngay_thanh_ly or fields.Date.today(),
                "ref": f"Thanh lý tài sản {ts.ma_tai_san} - {rec.ma_thanh_ly}",
                "line_ids": lines,
            })
            move.action_post()
            ts.write({"trang_thai": "mat", "hien_trang_su_dung": "khong_su_dung"})
            rec.write({"account_move_id": move.id, "trang_thai": "da_ghi_so"})

    def action_huy(self):
        for rec in self:
            if rec.trang_thai == "huy":
                raise UserError("Bản ghi đã hủy rồi.")
            if rec.account_move_id and rec.account_move_id.state == "posted":
                rec.account_move_id.button_cancel()
                rec.account_move_id.button_draft()
                rec.account_move_id.unlink()
            rec.write({"trang_thai": "huy", "account_move_id": False})

    def action_xem_but_toan(self):
        self.ensure_one()
        if not self.account_move_id:
            raise UserError("Chưa có bút toán.")
        return {
            "type": "ir.actions.act_window",
            "name": "Bút toán thanh lý",
            "res_model": "account.move",
            "res_id": self.account_move_id.id,
            "view_mode": "form",
            "target": "current",
        }

    def _kiem_tra_tai_khoan(self, rec):
        missing = []
        if not rec.journal_id:
            missing.append("Sổ nhật ký")
        if not rec.tai_khoan_nguyen_gia_id:
            missing.append("TK Nguyên giá tài sản")
        if not rec.tai_khoan_luy_ke_id:
            missing.append("TK Khấu hao lũy kế")
        if not rec.tai_khoan_thu_hoi_id and rec.gia_tri_thanh_ly > 0:
            missing.append("TK Thu hồi / Tiền mặt")
        if rec.lai_lo_thanh_ly > 0 and not rec.tai_khoan_lai_id:
            missing.append("TK Lãi thanh lý (711)")
        if rec.lai_lo_thanh_ly < 0 and not rec.tai_khoan_lo_id:
            missing.append("TK Lỗ thanh lý (811)")
        if missing:
            raise UserError(f"Chưa thiết lập: {', '.join(missing)}")
