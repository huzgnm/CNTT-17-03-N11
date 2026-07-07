# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import date


class KhauHaoHangThang(models.Model):
    _name = "tai_chinh.khau_hao"
    _description = "Khau hao tai san hang thang"
    _rec_name = "ma_khau_hao"
    _order = "ky_khau_hao desc, id desc"

    ma_khau_hao = fields.Char(
        "Mã khấu hao", required=True, copy=False, readonly=True, default="New"
    )
    tai_san_id = fields.Many2one("tai_san", string="Tài sản", required=True, ondelete="cascade")
    ten_tai_san = fields.Char(related="tai_san_id.ten_tai_san", string="Tên tài sản", readonly=True)
    danh_muc_loai_tai_san_id = fields.Many2one(
        related="tai_san_id.danh_muc_loai_tai_san_id", string="Loại tài sản", readonly=True
    )

    ky_khau_hao = fields.Date("Ky khau hao (thang)", required=True)
    gia_tri_truoc_kh = fields.Float("Gia tri truoc KH (VND)", readonly=True)
    so_tien_khau_hao = fields.Float("Số tiền khấu hao (VND)", required=True)
    gia_tri_sau_kh = fields.Float("Gia tri sau KH (VND)", compute="_compute_gia_tri_sau", store=True)

    trang_thai = fields.Selection([
        ("nhap", "Nháp"),
        ("da_ghi_so", "Đã ghi sổ"),
    ], string="Trạng thái", default="nhap")

    ghi_chu = fields.Text("Ghi chú")

    @api.depends("gia_tri_truoc_kh", "so_tien_khau_hao")
    def _compute_gia_tri_sau(self):
        for rec in self:
            rec.gia_tri_sau_kh = max(0.0, rec.gia_tri_truoc_kh - rec.so_tien_khau_hao)

    @api.model
    def create(self, vals):
        if vals.get("ma_khau_hao", "New") == "New":
            last = self.search([], order="id desc", limit=1)
            num = 0
            if last and last.ma_khau_hao and last.ma_khau_hao.startswith("KH"):
                try:
                    num = int(last.ma_khau_hao[2:])
                except ValueError:
                    pass
            vals["ma_khau_hao"] = "KH%05d" % (num + 1)
        return super(KhauHaoHangThang, self).create(vals)

    def action_ghi_so(self):
        for rec in self:
            if rec.trang_thai != "nhap":
                raise UserError("Chi co the ghi so tu trang thai Nhap.")
            # Cap nhat tong_da_khau_hao tren tai san
            rec.tai_san_id.tong_da_khau_hao += rec.so_tien_khau_hao
            rec.trang_thai = "da_ghi_so"

    @api.model
    def cron_khau_hao_hang_thang(self):
        """Chay ngay 1 hang thang: tu dong tao ban ghi khau hao cho tat ca tai san dang su dung."""
        today = date.today()
        ky = today.replace(day=1)
        tai_san_list = self.env["tai_san"].search([
            ("trang_thai", "=", "dang_su_dung"),
            ("khau_hao_moi_thang", ">", 0),
        ])
        for ts in tai_san_list:
            # Kiem tra da co ban ghi chua
            existing = self.search([
                ("tai_san_id", "=", ts.id),
                ("ky_khau_hao", "=", ky),
            ], limit=1)
            if existing:
                continue
            if ts.gia_tri_con_lai <= 0:
                continue
            so_tien = min(ts.khau_hao_moi_thang, ts.gia_tri_con_lai)
            rec = self.create({
                "tai_san_id": ts.id,
                "ky_khau_hao": ky,
                "gia_tri_truoc_kh": ts.gia_tri_con_lai,
                "so_tien_khau_hao": so_tien,
            })
            rec.action_ghi_so()
