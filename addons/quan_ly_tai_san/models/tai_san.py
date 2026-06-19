# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import date
from dateutil.relativedelta import relativedelta


class TaiSan(models.Model):
    _name = "tai_san"
    _description = "Bảng quản lý tài sản"
    _rec_name = "ma_tai_san"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # ── Thông tin cơ bản ─────────────────────────────────────────────────────
    ma_tai_san = fields.Char(
        "Mã tài sản", required=True, copy=False, readonly=True, default="New"
    )
    ten_tai_san = fields.Char("Tên tài sản", required=True)
    danh_muc_loai_tai_san_id = fields.Many2one(
        "danh_muc_loai_tai_san", string="Loại tài sản", required=True
    )

    # ── Tài chính ────────────────────────────────────────────────────────────
    so_luong = fields.Integer("Số lượng", default=1)
    gia_tri_tai_san = fields.Float("Nguyên giá tài sản (VNĐ)", required=True)
    tong_gia_tri = fields.Float(
        "Tổng giá trị (VNĐ)", compute="_compute_tong_gia_tri", store=True
    )
    het_han_bao_hanh = fields.Date("Hết hạn bảo hành")
    hinh_anh = fields.Binary("Hình ảnh tài sản", attachment=True)
    hinh_anh_ten = fields.Char("Tên file ảnh")
    mo_ta = fields.Text("Mô tả / Ghi chú")
    vi_tri = fields.Char("Vị trí / Phòng ban sử dụng")

    # ── Cảnh báo bảo hành / bảo trì ─────────────────────────────────────────
    tinh_trang_bao_hanh = fields.Selection([
        ("con_han", "Còn bảo hành"),
        ("sap_het", "Sắp hết bảo hành (< 30 ngày)"),
        ("het_han", "Hết bảo hành"),
        ("khong_co", "Không có bảo hành"),
    ], string="Tình trạng bảo hành", compute="_compute_tinh_trang_bao_hanh", store=True)
    ngay_bao_tri_gan_nhat = fields.Date(
        "Ngày bảo trì gần nhất", compute="_compute_ngay_bao_tri_gan_nhat", store=True
    )
    so_ngay_chua_bao_tri = fields.Integer(
        "Số ngày chưa bảo trì", compute="_compute_ngay_bao_tri_gan_nhat", store=True
    )
    canh_bao_bao_tri = fields.Boolean(
        "Cảnh báo bảo trì", compute="_compute_ngay_bao_tri_gan_nhat", store=True,
        help="True nếu tài sản chưa được bảo trì > 180 ngày"
    )
    phan_tram_khau_hao = fields.Float(
        "% Đã khấu hao", compute="_compute_phan_tram_khau_hao", store=True
    )
    ngay_mua = fields.Date("Ngày mua")
    thoi_gian_su_dung = fields.Integer("Thời gian sử dụng (năm)", default=5)

    # ── Khấu hao ─────────────────────────────────────────────────────────────
    ty_le_khau_hao = fields.Float(
        related="danh_muc_loai_tai_san_id.ty_le_khau_hao",
        string="Tỷ lệ khấu hao hàng năm (%)", store=True
    )
    khau_hao_moi_nam = fields.Float(
        "Khấu hao mỗi năm (VNĐ)", compute="_compute_khau_hao", store=True
    )
    khau_hao_moi_thang = fields.Float(
        "Khấu hao mỗi tháng (VNĐ)", compute="_compute_khau_hao", store=True
    )
    tong_da_khau_hao = fields.Float(
        "Đã khấu hao lũy kế (VNĐ)", compute="_compute_tong_da_khau_hao", store=True
    )
    gia_tri_con_lai = fields.Float(
        "Giá trị còn lại (VNĐ)", compute="_compute_gia_tri_con_lai", store=True
    )

    # ── Kế toán - Khấu hao ───────────────────────────────────────────────────
    journal_id = fields.Many2one(
        "account.journal", string="Sổ nhật ký khấu hao",
        domain=[("type", "in", ["general", "purchase"])]
    )
    tai_khoan_khau_hao_id = fields.Many2one(
        "account.account", string="TK Chi phí khấu hao",
        help="Tài khoản ghi Nợ khi tính khấu hao (vd: 6274)"
    )
    tai_khoan_luy_ke_id = fields.Many2one(
        "account.account", string="TK Khấu hao lũy kế",
        help="Tài khoản ghi Có khi tính khấu hao (vd: 2141)"
    )

    # ── Kế toán - Mua tài sản ────────────────────────────────────────────────
    journal_mua_id = fields.Many2one(
        "account.journal", string="Sổ nhật ký mua",
        domain=[("type", "in", ["general", "purchase"])]
    )
    tai_khoan_tai_san_id = fields.Many2one(
        "account.account", string="TK Nguyên giá tài sản",
        help="Tài khoản ghi Nợ khi mua (vd: 211)"
    )
    tai_khoan_thanh_toan_id = fields.Many2one(
        "account.account", string="TK Thanh toán / Phải trả",
        help="Tài khoản ghi Có khi mua (vd: 331, 111, 112)"
    )
    account_move_mua_id = fields.Many2one(
        "account.move", string="Bút toán mua tài sản", readonly=True, copy=False
    )
    da_ghi_so_mua = fields.Boolean(
        "Đã ghi sổ mua", compute="_compute_da_ghi_so_mua", store=True
    )

    # ── Trạng thái ───────────────────────────────────────────────────────────
    hien_trang_su_dung = fields.Selection([
        ("dang_su_dung", "Đang sử dụng"),
        ("khong_su_dung", "Không sử dụng"),
    ], string="Hiện trạng sử dụng", default="dang_su_dung")

    trang_thai = fields.Selection([
        ("dang_su_dung", "Đang sử dụng"),
        ("hong", "Hỏng"),
        ("mat", "Mất"),
        ("bao_tri", "Bảo trì"),
        ("sua_chua", "Sửa chữa"),
        ("cho_cap_phat", "Đang chờ cấp phát"),
        ("da_thanh_ly", "Đã thanh lý"),
    ], string="Trạng thái", default="dang_su_dung")

    thong_ke_id = fields.Many2one("thong_ke", string="Thống kê liên quan")

    # ── Thống kê ─────────────────────────────────────────────────────────────
    so_lan_muon = fields.Integer("Số lần mượn", compute="_compute_so_lan_muon", store=True)
    so_lan_su_dung = fields.Integer("Số lần sử dụng", compute="_compute_so_lan_su_dung", store=True)
    so_lan_bao_tri = fields.Integer("Số lần bảo trì", compute="_compute_so_lan_bao_tri", store=True)
    so_lan_thanh_ly = fields.Integer("Số lần thanh lý", compute="_compute_so_lan_thanh_ly", store=True)
    so_lan_dieu_chuyen = fields.Integer(
        "Số lần điều chuyển", compute="_compute_so_lan_dieu_chuyen", store=True
    )

    # ── One2many ─────────────────────────────────────────────────────────────
    muon_tra_ids = fields.One2many("muon_tra", "tai_san_id", string="Lịch sử mượn trả")
    lich_su_su_dung_tai_san_ids = fields.One2many(
        "lich_su_su_dung_tai_san", "tai_san_id", string="Lịch sử sử dụng"
    )
    lich_su_quan_ly_tai_san_ids = fields.One2many(
        "lich_su_quan_ly_tai_san", "tai_san_id", string="Lịch sử quản lý"
    )
    lich_su_bao_tri_tai_san_ids = fields.One2many(
        "bao_tri", "tai_san_id", string="Lịch sử bảo trì"
    )
    lich_su_thanh_ly_tai_san_ids = fields.One2many(
        "thanh_ly", "tai_san_id", string="Lịch sử thanh lý"
    )
    lich_su_dieu_chuyen_tai_san_ids = fields.One2many(
        "dieu_chuyen_tai_san", "tai_san_id", string="Lịch sử điều chuyển"
    )
    khau_hao_hang_thang_ids = fields.One2many(
        "khau_hao_hang_thang", "tai_san_id", string="Lịch sử khấu hao"
    )

    # =========================================================================
    # COMPUTE
    # =========================================================================
    @api.depends("so_luong", "gia_tri_tai_san")
    def _compute_tong_gia_tri(self):
        for rec in self:
            rec.tong_gia_tri = rec.so_luong * rec.gia_tri_tai_san

    @api.depends("gia_tri_tai_san", "thoi_gian_su_dung", "danh_muc_loai_tai_san_id.ty_le_khau_hao")
    def _compute_khau_hao(self):
        for rec in self:
            if rec.thoi_gian_su_dung and rec.thoi_gian_su_dung > 0:
                rec.khau_hao_moi_nam = rec.gia_tri_tai_san / rec.thoi_gian_su_dung
            else:
                rec.khau_hao_moi_nam = 0.0
            rec.khau_hao_moi_thang = rec.khau_hao_moi_nam / 12

    @api.depends("khau_hao_hang_thang_ids.so_tien_khau_hao", "khau_hao_hang_thang_ids.trang_thai")
    def _compute_tong_da_khau_hao(self):
        for rec in self:
            da_ghi = rec.khau_hao_hang_thang_ids.filtered(lambda k: k.trang_thai == "da_ghi_so")
            rec.tong_da_khau_hao = sum(da_ghi.mapped("so_tien_khau_hao"))

    @api.depends("gia_tri_tai_san", "tong_da_khau_hao")
    def _compute_gia_tri_con_lai(self):
        for rec in self:
            rec.gia_tri_con_lai = max(0.0, rec.gia_tri_tai_san - rec.tong_da_khau_hao)

    @api.depends("account_move_mua_id", "account_move_mua_id.state")
    def _compute_da_ghi_so_mua(self):
        for rec in self:
            rec.da_ghi_so_mua = bool(
                rec.account_move_mua_id and rec.account_move_mua_id.state == "posted"
            )

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

    # =========================================================================
    # COMPUTE - Tính năng bổ sung
    # =========================================================================
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

    @api.depends("lich_su_bao_tri_tai_san_ids", "lich_su_bao_tri_tai_san_ids.tinh_trang",
                 "lich_su_bao_tri_tai_san_ids.ngay_bao_tri")
    def _compute_ngay_bao_tri_gan_nhat(self):
        today = date.today()
        for rec in self:
            done = rec.lich_su_bao_tri_tai_san_ids.filtered(
                lambda b: b.tinh_trang == "da_xong"
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

    @api.depends("tong_da_khau_hao", "gia_tri_tai_san")
    def _compute_phan_tram_khau_hao(self):
        for rec in self:
            if rec.gia_tri_tai_san:
                rec.phan_tram_khau_hao = min(100.0, rec.tong_da_khau_hao / rec.gia_tri_tai_san * 100)
            else:
                rec.phan_tram_khau_hao = 0.0

    # =========================================================================
    # CRUD
    # =========================================================================
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
            vals["ma_tai_san"] = f"TS{last_num + 1:05d}"
        return super().create(vals)

    # =========================================================================
    # ACTIONS - Kế toán mua tài sản
    # =========================================================================
    def action_ghi_so_mua_tai_san(self):
        for rec in self:
            if rec.da_ghi_so_mua:
                raise UserError(f"Tài sản {rec.ma_tai_san} đã ghi sổ mua rồi.")
            missing = []
            if not rec.journal_mua_id:
                missing.append("Sổ nhật ký mua")
            if not rec.tai_khoan_tai_san_id:
                missing.append("TK Nguyên giá tài sản")
            if not rec.tai_khoan_thanh_toan_id:
                missing.append("TK Thanh toán / Phải trả")
            if missing:
                raise UserError(f"Chưa thiết lập: {', '.join(missing)}")

            move = self.env["account.move"].create({
                "journal_id": rec.journal_mua_id.id,
                "date": rec.ngay_mua or fields.Date.today(),
                "ref": f"Mua tài sản {rec.ma_tai_san} - {rec.ten_tai_san}",
                "line_ids": [
                    (0, 0, {
                        "account_id": rec.tai_khoan_tai_san_id.id,
                        "name": f"Nguyên giá TSCĐ: {rec.ten_tai_san}",
                        "debit": rec.tong_gia_tri,
                        "credit": 0.0,
                    }),
                    (0, 0, {
                        "account_id": rec.tai_khoan_thanh_toan_id.id,
                        "name": f"Phải trả / Thanh toán mua {rec.ten_tai_san}",
                        "debit": 0.0,
                        "credit": rec.tong_gia_tri,
                    }),
                ],
            })
            move.action_post()
            rec.account_move_mua_id = move.id

    def action_xem_but_toan_mua(self):
        self.ensure_one()
        if not self.account_move_mua_id:
            raise UserError("Chưa có bút toán mua tài sản.")
        return {
            "type": "ir.actions.act_window",
            "name": "Bút toán mua tài sản",
            "res_model": "account.move",
            "res_id": self.account_move_mua_id.id,
            "view_mode": "form",
            "target": "current",
        }

    # =========================================================================
    # ACTIONS - Khấu hao
    # =========================================================================
    def _kiem_tra_da_khau_hao(self, thang, nam):
        self.ensure_one()
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
            if rec.trang_thai != "dang_su_dung":
                continue
            if not rec.journal_id or not rec.tai_khoan_khau_hao_id or not rec.tai_khoan_luy_ke_id:
                raise UserError(
                    f"Tài sản {rec.ma_tai_san} chưa thiết lập đầy đủ thông tin kế toán khấu hao."
                )
            kh = rec._tao_khau_hao_thang(today.month, today.year)
            if kh:
                kh.action_ghi_so()
                count += 1
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Khấu hao",
                "message": f"Đã tạo và ghi sổ {count} kỳ khấu hao.",
                "type": "success",
                "sticky": False,
            },
        }

    def action_tao_lich_khau_hao(self):
        for rec in self:
            if not rec.ngay_mua:
                raise UserError(f"Tài sản {rec.ma_tai_san} chưa có ngày mua.")
            today = date.today()
            start = rec.ngay_mua
            current = date(start.year, start.month, 1)
            end = date(today.year, today.month, 1)
            created = 0
            while current <= end:
                kh = rec._tao_khau_hao_thang(current.month, current.year)
                if kh:
                    created += 1
                if current.month == 12:
                    current = date(current.year + 1, 1, 1)
                else:
                    current = date(current.year, current.month + 1, 1)
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Tạo lịch khấu hao",
                "message": f"Đã tạo {created} kỳ khấu hao mới.",
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
        """Tạo activity cảnh báo cho tài sản chưa bảo trì > 180 ngày"""
        tai_san_canh_bao = self.search([
            ("trang_thai", "=", "dang_su_dung"),
            ("canh_bao_bao_tri", "=", True),
        ])
        activity_type = self.env.ref("mail.mail_activity_data_warning", raise_if_not_found=False)
        for ts in tai_san_canh_bao:
            # Kiểm tra chưa có activity cảnh báo bảo trì
            existing = self.env["mail.activity"].search([
                ("res_model", "=", "tai_san"),
                ("res_id", "=", ts.id),
                ("summary", "ilike", "Cảnh báo bảo trì"),
            ], limit=1)
            if not existing and activity_type:
                ts.activity_schedule(
                    activity_type_id=activity_type.id,
                    summary=f"Cảnh báo bảo trì: {ts.so_ngay_chua_bao_tri} ngày chưa bảo trì",
                    note=f"Tài sản {ts.ten_tai_san} ({ts.ma_tai_san}) chưa được bảo trì "
                         f"trong {ts.so_ngay_chua_bao_tri} ngày. Vui lòng lên kế hoạch bảo trì.",
                )

    @api.model
    def cron_canh_bao_bao_hanh(self):
        """Tạo activity cảnh báo cho tài sản sắp hết bảo hành (< 30 ngày)"""
        tai_san_sap_het = self.search([
            ("tinh_trang_bao_hanh", "=", "sap_het"),
        ])
        activity_type = self.env.ref("mail.mail_activity_data_warning", raise_if_not_found=False)
        for ts in tai_san_sap_het:
            existing = self.env["mail.activity"].search([
                ("res_model", "=", "tai_san"),
                ("res_id", "=", ts.id),
                ("summary", "ilike", "Sắp hết bảo hành"),
            ], limit=1)
            if not existing and activity_type:
                ts.activity_schedule(
                    activity_type_id=activity_type.id,
                    summary=f"Sắp hết bảo hành: {ts.het_han_bao_hanh}",
                    note=f"Tài sản {ts.ten_tai_san} ({ts.ma_tai_san}) sắp hết hạn bảo hành "
                         f"vào ngày {ts.het_han_bao_hanh}.",
                )

    def action_view_muon_tra(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Mượn trả',
            'res_model': 'muon_tra',
            'view_mode': 'tree,form',
            'domain': [('tai_san_id', '=', self.id)],
            'context': {'default_tai_san_id': self.id},
        }

    def action_view_bao_tri(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Bảo trì',
            'res_model': 'bao_tri',
            'view_mode': 'tree,form',
            'domain': [('tai_san_id', '=', self.id)],
            'context': {'default_tai_san_id': self.id},
        }

    def action_view_thanh_ly(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Thanh lý',
            'res_model': 'thanh_ly',
            'view_mode': 'tree,form',
            'domain': [('tai_san_id', '=', self.id)],
            'context': {'default_tai_san_id': self.id},
        }

    def action_view_dieu_chuyen(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Điều chuyển',
            'res_model': 'dieu_chuyen_tai_san',
            'view_mode': 'tree,form',
            'domain': [('tai_san_id', '=', self.id)],
            'context': {'default_tai_san_id': self.id},
        }
