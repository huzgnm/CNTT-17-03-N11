# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import date


class TaiChinhDashboard(models.TransientModel):
    _name = "tai_chinh.dashboard"
    _description = "Dashboard Quan ly Tai Chinh"

    tong_tai_san = fields.Integer("Tong tai san", readonly=True)
    tai_san_dang_su_dung = fields.Integer("Dang su dung", readonly=True)
    tai_san_bao_tri = fields.Integer("Tai san dang bao tri", readonly=True)
    tai_san_hong = fields.Integer("Bi hong", readonly=True)
    tai_san_da_thanh_ly = fields.Integer("Da thanh ly", readonly=True)

    bao_tri_cho_duyet = fields.Integer("Cho duyet", readonly=True)
    bao_tri_dang_thuc_hien = fields.Integer("Dang bao tri", readonly=True)
    bao_tri_hoan_thanh_thang = fields.Integer("Hoan thanh thang nay", readonly=True)

    phieu_thu_cho_duyet = fields.Integer("Phieu thu cho duyet", readonly=True)
    phieu_chi_cho_duyet = fields.Integer("Phieu chi cho duyet", readonly=True)
    tong_thu_thang = fields.Float("Tong thu thang nay (VND)", readonly=True)
    tong_chi_thang = fields.Float("Tong chi thang nay (VND)", readonly=True)

    khau_hao_thang = fields.Float("Khau hao thang nay (VND)", readonly=True)
    tai_san_het_khau_hao = fields.Integer("Tai san het khau hao", readonly=True)

    thanh_ly_cho_duyet = fields.Integer("Thanh ly cho duyet", readonly=True)

    currency_id = fields.Many2one("res.currency", string="Tien te", readonly=True)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        today = date.today()
        dau_thang = "%04d-%02d-01" % (today.year, today.month)
        if today.month == 12:
            cuoi_thang = "%04d-12-31" % today.year
        else:
            cuoi_thang = "%04d-%02d-01" % (today.year, today.month + 1)

        TaiSan = self.env["tai_san"]
        BaoTri = self.env["bao_tri"]
        Phieu = self.env["tai_chinh.phieu_thu_chi"]
        KhauHao = self.env["tai_chinh.khau_hao"]
        ThanhLy = self.env["thanh_ly"]

        thu_thang = Phieu.search([("loai_phieu", "=", "thu"), ("trang_thai", "=", "da_duyet"),
                                  ("ngay_duyet", ">=", dau_thang), ("ngay_duyet", "<", cuoi_thang)])
        chi_thang = Phieu.search([("loai_phieu", "=", "chi"), ("trang_thai", "=", "da_duyet"),
                                  ("ngay_duyet", ">=", dau_thang), ("ngay_duyet", "<", cuoi_thang)])
        kh_thang = KhauHao.search([("ky_khau_hao", ">=", dau_thang), ("ky_khau_hao", "<", cuoi_thang),
                                   ("trang_thai", "=", "da_ghi_so")])

        res.update({
            "currency_id": self.env.company.currency_id.id,
            "tong_tai_san": TaiSan.search_count([]),
            "tai_san_dang_su_dung": TaiSan.search_count([("trang_thai", "=", "dang_su_dung")]),
            "tai_san_bao_tri": TaiSan.search_count([("trang_thai", "=", "bao_tri")]),
            "tai_san_hong": TaiSan.search_count([("trang_thai", "=", "hong")]),
            "tai_san_da_thanh_ly": TaiSan.search_count([("trang_thai", "=", "da_thanh_ly")]),
            "bao_tri_cho_duyet": BaoTri.search_count([("tinh_trang", "=", "dang_cho_duyet")]),
            "bao_tri_dang_thuc_hien": BaoTri.search_count([("tinh_trang", "=", "dang_bao_tri")]),
            "bao_tri_hoan_thanh_thang": BaoTri.search_count([("tinh_trang", "=", "da_xong"),
                                                             ("ngay_bao_tri", ">=", dau_thang),
                                                             ("ngay_bao_tri", "<", cuoi_thang)]),
            "phieu_thu_cho_duyet": Phieu.search_count([("trang_thai", "=", "cho_duyet"), ("loai_phieu", "=", "thu")]),
            "phieu_chi_cho_duyet": Phieu.search_count([("trang_thai", "=", "cho_duyet"), ("loai_phieu", "=", "chi")]),
            "tong_thu_thang": sum(thu_thang.mapped("so_tien")),
            "tong_chi_thang": sum(chi_thang.mapped("so_tien")),
            "khau_hao_thang": sum(kh_thang.mapped("so_tien_khau_hao")),
            "tai_san_het_khau_hao": TaiSan.search_count([("gia_tri_con_lai", "<=", 0)]),
            "thanh_ly_cho_duyet": ThanhLy.search_count([("trang_thai", "=", "cho_duyet")]),
        })
        return res

    def action_refresh(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Dashboard",
            "res_model": "tai_chinh.dashboard",
            "view_mode": "form",
            "target": "main",
        }
