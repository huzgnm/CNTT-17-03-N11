# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import date
from dateutil.relativedelta import relativedelta


class TaiSan(models.Model):
    _name = "tai_san"
    _description = "Ban quan ly tai san"
    _rec_name = "ma_tai_san"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # -- Thong tin co ban --
    ma_tai_san = fields.Char(
        "Ma tai san", required=True, copy=False, readonly=True, default="New"
    )
    ten_tai_san = fields.Char("Ten tai san", required=True)
    ma_vach = fields.Char("Ma vach / Barcode", copy=False, index=True)
    danh_muc_loai_tai_san_id = fields.Many2one(
        "danh_muc_loai_tai_san", string="Loai tai san", required=True
    )

    # -- Thoi gian --
    so_luong = fields.Integer("So luong", default=1)
    gia_tri_tai_san = fields.Float(
        "Tong gia tri (VND)", compute="_compute_tong_gia_tri", store=True
    )
    het_han_bao_hanh = fields.Date("Het han bao hanh")
    hinh_anh = fields.Binary("Hinh anh", attachment=True)
    hinh_anh_ten_file = fields.Char("Ten file hinh anh")
    vi_tri = fields.Char("Vi tri / Phong ban su dung")
    mo_ta = fields.Text("Mo ta / Ghi chu")

    # -- Ngay --
    ngay_mua = fields.Date("Ngay mua")
    ngay_su_dung = fields.Date("Ngay su dung")
    thoi_gian_su_dung = fields.Integer("Thoi gian su dung (nam)", default=5)

    # -- Tinh trang bao hanh --
    tinh_trang_bao_hanh = fields.Selection([
        ("con_han", "Con han"),
        ("sap_het", "Sap het han bao hanh (< 30 ngay)"),
        ("het_han", "Het han"),
        ("khong_co", "Khong co bao hanh"),
    ], string="Tinh trang bao hanh", compute="_compute_tinh_trang_bao_hanh", store=True)
    ngay_bao_tri_gan_nhat = fields.Date(
        "Ngay bao tri gan nhat", compute="_compute_ngay_bao_tri_gan_nhat", store=True
    )
    so_ngay_chua_bao_tri = fields.Integer(
        "So ngay chua bao tri", compute="_compute_ngay_bao_tri_gan_nhat", store=True
    )
    canh_bao_bao_tri = fields.Boolean(
        "Canh bao bao tri", compute="_compute_ngay_bao_tri_gan_nhat", store=True,
        help="True neu tai san chua duoc bao tri > 180 ngay"
    )
    phan_tram_khau_hao = fields.Float(
        "% Khau hao", related="danh_muc_loai_tai_san_id.ty_le_khau_hao",
        store=True
    )
    khau_hao_moi_nam = fields.Float(
        "Khau hao moi nam (VND)", compute="_compute_khau_hao", store=True
    )
    khau_hao_moi_thang = fields.Float(
        "Khau hao moi thang (VND)", compute="_compute_khau_hao", store=True
    )
    tong_da_khau_hao = fields.Float(
        "Da khau hao luy ke (VND)", compute="_compute_tong_da_khau_hao", store=True
    )
    gia_tri_con_lai = fields.Float(
        "Gia tri con lai (VND)", compute="_compute_gia_tri_con_lai", store=True
    )

    # -- Lien ket --
    nha_cung_cap_id = fields.Many2one("nha_cung_cap", string="Nha cung cap")
    nhac_cung_cap_id = fields.Many2one("nha_cung_cap", string="Nha cung cap mua")
    thong_ke_id = fields.Many2one("thong_ke", string="Thong ke lien quan")

    # -- Trang thai --
    hien_trang_su_dung = fields.Selection([
        ("dang_su_dung", "Dang su dung"),
        ("khong_su_dung", "Khong su dung"),
    ], string="Hien trang su dung", default="dang_su_dung")

    trang_thai = fields.Selection([
        ("dang_su_dung", "Dang su dung"),
        ("hong", "Hong"),
        ("mat", "Mat"),
        ("bao_tri", "Bao tri"),
        ("sua_chua", "Sua chua"),
        ("cho_cap_phat", "Dang cho cap phat"),
        ("da_thanh_ly", "Da thanh ly"),
    ], string="Trang thai", default="dang_su_dung")

    # -- Thong ke --
    so_lan_muon = fields.Integer("So lan muon", compute="_compute_so_lan_muon", store=True)
    so_lan_su_dung = fields.Integer("So lan su dung", compute="_compute_so_lan_su_dung", store=True)
    so_lan_bao_tri = fields.Integer("So lan bao tri", compute="_compute_so_lan_bao_tri", store=True)
    so_lan_thanh_ly = fields.Integer("So lan thanh ly", compute="_compute_so_lan_thanh_ly", store=True)
    so_lan_dieu_chuyen = fields.Integer(
        "So lan dieu chuyen", compute="_compute_so_lan_dieu_chuyen", store=True
    )

    # -- One2many --
    muon_tra_ids = fields.One2many("muon_tra", "tai_san_id", string="Lich su muon tra")
    lich_su_su_dung_tai_san_ids = fields.One2many(
        "lich_su_su_dung_tai_san", "tai_san_id", string="Lich su su dung"
    )
    lich_su_quan_ly_tai_san_ids = fields.One2many(
        "lich_su_quan_ly_tai_san", "tai_san_id", string="Lich su quan ly"
    )
    lich_su_bao_tri_tai_san_ids = fields.One2many(
        "bao_tri", "tai_san_id", string="Lich su bao tri"
    )
    lich_su_thanh_ly_tai_san_ids = fields.One2many(
        "thanh_ly", "tai_san_id", string="Lich su thanh ly"
    )
    lich_su_dieu_chuyen_tai_san_ids = fields.One2many(
        "dieu_chuyen_tai_san", "tai_san_id", string="Lich su dieu chuyen"
    )
    khau_hao_hang_thang_ids = fields.One2many(
        "khau_hao_hang_thang", "tai_san_id", string="Lich su khau hao"
    )

    # ===================================
    # COMPUTE
    # ===================================
    @api.depends("so_luong", "gia_tri_tai_san")
    def _compute_tong_gia_tri(self):
        for rec in self:
            rec.tong_gia_tri = rec.so_luong * rec.gia_tri_tai_san

    @api.depends("gia_tri_tai_san", "thoi_gian_su_dung", "danh_muc_loai_tai_san_id.ty_le_khau_hao")
    def _compute_khau_hao(self):
        for rec in self:
            if rec.thoi_gian_su_dung and rec.thoi_gian_su_dung > 0:
                rec.khau_hao_moi_nam = rec.gia_tri_tai_san / rec.thoi_gian_su_dung
                rec.khau_hao_moi_thang = rec.khau_hao_moi_nam / 12
            else:
                rec.khau_hao_moi_nam = 0.0
                rec.khau_hao_moi_thang = 0.0

    @api.depends("khau_hao_hang_thang_ids.so_tien_khau_hao", "khau_hao_hang_thang_ids.trang_thai")
    def _compute_tong_da_khau_hao(self):
        for rec in self:
            da_ghi = rec.khau_hao_hang_thang_ids.filtered(lambda k: k.trang_thai == "da_ghi_so")
            rec.tong_da_khau_hao = sum(da_ghi.mapped("so_tien_khau_hao"))

    @api.depends("tong_da_khau_hao", "gia_tri_tai_san")
    def _compute_gia_tri_con_lai(self):
        for rec in self:
            rec.gia_tri_con_lai = max(0.0, rec.gia_tri_tai_san - rec.tong_da_khau_hao)

    @api.depends("het_han_bao_hanh")
    def _compute_tinh_trang_bao_hanh(self):
        today = date.today()
        for rec in self:
            if not rec.het_han_bao_hanh:
                rec.tinh_trang_bao_hanh = "khong_co"
            elif rec.het_han_bao_hanh < today:
                rec.tinh_trang_bao_hanh = "het_han"
            elif (rec.het_han_bao_hanh - today).days <= 30:
                rec.tinh_trang_bao_hanh = "sap_het"
            else:
                rec.tinh_trang_bao_hanh = "con_han"

    @api.depends("lich_su_bao_tri_tai_san_ids", "lich_su_bao_tri_tai_san_ids.trang_thai",
                 "lich_su_bao_tri_tai_san_ids.ngay_bao_tri")
    def _compute_ngay_bao_tri_gan_nhat(self):
        today = date.today()
        for rec in self:
            done = rec.lich_su_bao_tri_tai_san_ids.filtered(
                lambda b: b.trang_thai == "da_xong"
            ).sorted("ngay_bao_tri", reverse=True)
            if done:
                rec.ngay_bao_tri_gan_nhat = done[0].ngay_bao_tri
                delta = (today - done[0].ngay_bao_tri).days
                rec.so_ngay_chua_bao_tri = delta
                rec.canh_bao_bao_tri = delta > 180
            else:
                rec.ngay_bao_tri_gan_nhat = False
                rec.so_ngay_chua_bao_tri = 0
                rec.canh_bao_bao_tri = False

    @api.depends("gia_tri_tai_san", "tong_da_khau_hao")
    def _compute_phan_tram_khau_hao_da_trich(self):
        for rec in self:
            if rec.gia_tri_tai_san:
                rec.phan_tram_khau_hao = min(100.0, rec.tong_da_khau_hao / rec.gia_tri_tai_san * 100)
            else:
                rec.phan_tram_khau_hao = 0.0

    # ===================================
    # COMPUTE - Thong ke su dung
    # ===================================
    @api.depends("muon_tra_ids")
    def _compute_so_lan_muon(self):
        for rec in self:
            rec.so_lan_muon = len(rec.muon_tra_ids)

    @api.depends("lich_su_su_dung_tai_san_ids")
    def _compute_so_lan_su_dung(self):
        for rec in self:
            rec.so_lan_su_dung = len(rec.lich_su_su_dung_tai_san_ids)

    @api.depends("lich_su_bao_tri_tai_san_ids")
    def _compute_so_lan_bao_tri(self):
        for rec in self:
            rec.so_lan_bao_tri = len(rec.lich_su_bao_tri_tai_san_ids)

    @api.depends("lich_su_thanh_ly_tai_san_ids")
    def _compute_so_lan_thanh_ly(self):
        for rec in self:
            rec.so_lan_thanh_ly = len(rec.lich_su_thanh_ly_tai_san_ids)

    @api.depends("lich_su_dieu_chuyen_tai_san_ids")
    def _compute_so_lan_dieu_chuyen(self):
        for rec in self:
            rec.so_lan_dieu_chuyen = len(rec.lich_su_dieu_chuyen_tai_san_ids)

    # ===================================
    # CRUD
    # ===================================
    @api.model
    def create(self, vals):
        if vals.get("ma_tai_san", "New") == "New":
            last = self.search([], order="id desc", limit=1)
            last_num = 0
            if last and last.ma_tai_san and last.ma_tai_san.startswith("TS"):
                try:
                    last_num = int(last.ma_tai_san[2:])
                except ValueError:
                    last_num = 0
            vals["ma_tai_san"] = "TS%05d" % (last_num + 1)
        return super(TaiSan, self).create(vals)

    # ===================================
    # ACTIONS - ao toan mua tai san
    # ===================================
    def _kiem_tra_da_khau_hao(self, thang, nam):
        return self.env["khau_hao_hang_thang"].search_count([
            ("tai_san_id", "=", self.id),
            ("ky_thang", "=", thang),
            ("ky_nam", "=", nam),
            ("trang_thai", "!=", "huy"),
        ]) > 0

    def _tao_khau_hao_thang(self, thang, nam):
        self.ensure_one()
        if self._kiem_tra_da_khau_hao(thang, nam):
            return None
        if self.khau_hao_moi_thang <= 0:
            return None
        return self.env["khau_hao_hang_thang"].create({
            "tai_san_id": self.id,
            "ky_thang": thang,
            "ky_nam": nam,
            "so_tien_khau_hao": self.khau_hao_moi_thang,
            "ngay_ghi_nhan": date(nam, thang, 1),
        })

    def action_tinh_khau_hao_thang_nay(self):
        today = date.today()
        count = 0
        for rec in self:
            if rec.trang_thai not in ("dang_su_dung",):
                continue
            if not rec.journal_id or not rec.tai_khoan_khau_hao_id or not rec.tai_khoan_luy_ke_id:
                raise UserError(
                    f"Tai san {rec.ma_tai_san} chua thiet lap du thong tin ke toan khau hao."
                )
            kh = rec._tao_khau_hao_thang(today.month, today.year)
            if kh:
                kh.action_ghi_so()
                count += 1
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Khau hao",
                "message": f"Da ghi {count} khau hao thang nay.",
                "type": "success",
                "sticky": False,
            },
        }

    def action_tao_lich_su_khau_hao(self):
        for rec in self:
            if not rec.ngay_mua:
                raise UserError(f"Tai san {rec.ma_tai_san} chua co ngay mua.")
            today = date.today()
            start = rec.ngay_mua
            current = date(start.year, start.month, 1)
            end = date(today.year, today.month, 1)
            created = 0
            while current <= end:
                kh = rec._tao_khau_hao_thang(current.month, current.year)
                if kh:
                    try:
                        kh.action_ghi_so()
                    except Exception:
                        pass
                    created += 1
                if current.month == 12:
                    current = date(current.year + 1, 1, 1)
                else:
                    current = date(current.year, current.month + 1, 1)
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Tao lich su khau hao",
                "message": f"Da tao {created} ky khau hao.",
                "type": "success",
                "sticky": False,
            },
        }

    @api.model
    def cron_tinh_khau_hao_hang_thang(self):
        today = date.today()
        tai_san_list = self.search([("trang_thai", "=", "dang_su_dung")])
        for rec in tai_san_list:
            if not rec.journal_id or not rec.tai_khoan_khau_hao_id or not rec.tai_khoan_luy_ke_id:
                continue
            kh = rec._tao_khau_hao_thang(today.month, today.year)
            if kh:
                try:
                    kh.action_ghi_so()
                except Exception:
                    pass

    @api.model
    def cron_canh_bao_bao_tri(self):
        "Tao activity canh bao cho tai san chua bao tri > 180 ngay"
        tai_san_canh_bao = self.search([
            ("trang_thai", "=", "dang_su_dung"),
            ("canh_bao_bao_tri", "=", True),
        ])
        activity_type = self.env.ref("mail.mail_activity_data_warning", raise_if_not_found=False)
        for ts in tai_san_canh_bao:
            # Kiem tra trang cho activity canh bao bao tri
            existing = self.env["mail.activity"].search([
                ("res_model", "=", "tai_san"),
                ("res_id", "=", ts.id),
                ("summary", "ilike", "canh bao bao tri"),
            ], limit=1)
            if not existing and activity_type:
                try:
                    ts.activity_schedule(
                        "mail.mail_activity_data_warning",
                        summary="canh bao bao tri",
                        note=f"trong{ts.so_ngay_chua_bao_tri} ngay chua bao tri {ts.ma_tai_san} can kiem tra bao tri.",
                    )
                except Exception:
                    pass

    # ===================================
    # ACTIONS - Stat buttons
    # ===================================
    def action_view_muon_tra(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Muon tra",
            "res_model": "muon_tra",
            "view_mode": "tree,form",
            "domain": [("tai_san_id", "=", self.id)],
            "context": {"default_tai_san_id": self.id},
        }

    def action_view_bao_tri(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Bao tri",
            "res_model": "bao_tri",
            "view_mode": "tree,form",
            "domain": [("tai_san_id", "=", self.id)],
            "context": {"default_tai_san_id": self.id},
        }

    def action_view_thanh_ly(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Thanh ly",
            "res_model": "thanh_ly",
            "view_mode": "tree,form",
            "domain": [("tai_san_id", "=", self.id)],
            "context": {"default_tai_san_id": self.id},
        }

    def action_view_dieu_chuyen(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Dieu chuyen",
            "res_model": "dieu_chuyen_tai_san",
            "view_mode": "tree,form",
            "domain": [("tai_san_id", "=", self.id)],
            "context": {"default_tai_san_id": self.id},
        }
