# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import date


class TaiChinhDashboard(models.TransientModel):
    _name = "tai_chinh.dashboard"
    _description = "Dashboard Quan ly Tai Chinh"

    # === TAI SAN ===
    tong_tai_san = fields.Integer("Tong tai san", compute="_compute_all")
    tai_san_dang_su_dung = fields.Integer("Dang su dung", compute="_compute_all")
    tai_san_bao_tri = fields.Integer("Dang bao tri", compute="_compute_all")
    tai_san_hong = fields.Integer("Bi hong", compute="_compute_all")
    tai_san_da_thanh_ly = fields.Integer("Da thanh ly", compute="_compute_all")

    # === BAO TRI ===
    bao_tri_cho_duyet = fields.Integer("Cho duyet", compute="_compute_all")
    bao_tri_dang_thuc_hien = fields.Integer("Dang bao tri", compute="_compute_all")
    bao_tri_hoan_thanh_thang = fields.Integer("Hoan thanh thang nay", compute="_compute_all")

    # === PHIEU THU CHI ===
    phieu_thu_cho_duyet = fields.Integer("Phieu thu cho duyet", compute="_compute_all")
    phieu_chi_cho_duyet = fields.Integer("Phieu chi cho duyet", compute="_compute_all")
    tong_thu_thang = fields.Float("Tong thu thang nay (VND)", compute="_compute_all")
    tong_chi_thang = fields.Float("Tong chi thang nay (VND)", compute="_compute_all")

    # === KHAU HAO ===
    khau_hao_thang = fields.Float("Khau hao thang nay (VND)", compute="_compute_all")
    tai_san_het_khau_hao = fields.Integer("Tai san het khau hao", compute="_compute_all")

    # === THANH LY ===
    thanh_ly_cho_duyet = fields.Integer("Thanh ly cho duyet", compute="_compute_all")

    currency_id = fields.Many2one("res.currency", string="Tien te", compute="_compute_all")

    @api.depends()
    def _compute_all(self):
        today = date.today()
        thang = today.month
        nam = today.year
        dau_thang = "%04d-%02d-01" % (nam, thang)
        if thang == 12:
            cuoi_thang = "%04d-12-31" % nam
        else:
            cuoi_thang = "%04d-%02d-01" % (nam, thang + 1)

        for rec in self:
            rec.currency_id = self.env.company.currency_id
            TaiSan = self.env["tai_san"]
            rec.tong_tai_san = TaiSan.search_count([])
            rec.tai_san_dang_su_dung = TaiSan.search_count([("trang_thai", "=", "dang_su_dung")])
            rec.tai_san_bao_tri = TaiSan.search_count([("trang_thai", "=", "bao_tri")])
            rec.tai_san_hong = TaiSan.search_count([("trang_thai", "=", "hong")])
            rec.tai_san_da_thanh_ly = TaiSan.search_count([("trang_thai", "=", "da_thanh_ly")])

            BaoTri = self.env["bao_tri"]
            rec.bao_tri_cho_duyet = BaoTri.search_count([("tinh_trang", "=", "dang_cho_duyet")])
            rec.bao_tri_dang_thuc_hien = BaoTri.search_count([("tinh_trang", "=", "dang_bao_tri")])
            rec.bao_tri_hoan_thanh_thang = BaoTri.search_count([
                ("tinh_trang", "=", "da_xong"),
                ("ngay_bao_tri", ">=", dau_thang),
                ("ngay_bao_tri", "<", cuoi_thang),
            ])

            Phieu = self.env["tai_chinh.phieu_thu_chi"]
            rec.phieu_thu_cho_duyet = Phieu.search_count([
                ("trang_thai", "=", "cho_duyet"), ("loai_phieu", "=", "thu")
            ])
            rec.phieu_chi_cho_duyet = Phieu.search_count([
                ("trang_thai", "=", "cho_duyet"), ("loai_phieu", "=", "chi")
            ])

            thu_thang = Phieu.search([
                ("loai_phieu", "=", "thu"), ("trang_thai", "=", "da_duyet"),
                ("ngay_duyet", ">=", dau_thang), ("ngay_duyet", "<", cuoi_thang),
            ])
            rec.tong_thu_thang = sum(thu_thang.mapped("so_tien"))

            chi_thang = Phieu.search([
                ("loai_phieu", "=", "chi"), ("trang_thai", "=", "da_duyet"),
                ("ngay_duyet", ">=", dau_thang), ("ngay_duyet", "<", cuoi_thang),
            ])
            rec.tong_chi_thang = sum(chi_thang.mapped("so_tien"))

            KhauHao = self.env["tai_chinh.khau_hao"]
            kh_thang = KhauHao.search([
                ("ky_khau_hao", ">=", dau_thang),
                ("ky_khau_hao", "<", cuoi_thang),
                ("trang_thai", "=", "da_ghi_so"),
            ])
            rec.khau_hao_thang = sum(kh_thang.mapped("so_tien_khau_hao"))
            rec.tai_san_het_khau_hao = TaiSan.search_count([("gia_tri_con_lai", "<=", 0)])

            ThanhLy = self.env["thanh_ly"]
            rec.thanh_ly_cho_duyet = ThanhLy.search_count([("trang_thai", "=", "cho_duyet")])

    def action_refresh(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "tai_chinh.dashboard",
            "view_mode": "form",
            "target": "inline",
        }
