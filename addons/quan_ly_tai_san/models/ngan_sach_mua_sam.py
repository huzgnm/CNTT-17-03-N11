# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class NganSachMuaSam(models.Model):
    _name = 'ngan_sach_mua_sam'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Ngân sách mua sắm tài sản'
    _rec_name = 'ten_ngan_sach'
    _order = 'nam desc, id desc'

    # -------------------------------------------------------------------------
    # Thông tin cơ bản
    # -------------------------------------------------------------------------
    ma_ngan_sach = fields.Char(
        "Mã ngân sách", required=True, copy=False, readonly=True, default="New"
    )
    ten_ngan_sach = fields.Char("Tên ngân sách", required=True)
    nam = fields.Integer("Năm ngân sách", required=True, default=lambda self: fields.Date.today().year)
    danh_muc_loai_tai_san_id = fields.Many2one(
        'danh_muc_loai_tai_san', string="Loại tài sản",
        help="Để trống nếu ngân sách áp dụng cho tất cả loại tài sản"
    )
    mo_ta = fields.Text("Mô tả")
    nguoi_lap_id = fields.Many2one('nhan_vien', string="Người lập")
    nguoi_duyet_id = fields.Many2one('nhan_vien', string="Người duyệt")
    ngay_duyet = fields.Date("Ngày duyệt")

    # -------------------------------------------------------------------------
    # Tài chính
    # -------------------------------------------------------------------------
    so_tien_ke_hoach = fields.Float("Ngân sách kế hoạch (VNĐ)", required=True)
    so_tien_thuc_te = fields.Float(
        "Đã chi thực tế (VNĐ)", compute="_compute_thuc_te", store=True
    )
    chenh_lech = fields.Float(
        "Còn lại (VNĐ)", compute="_compute_chenh_lech", store=True
    )
    ty_le_thuc_hien = fields.Float(
        "Tỷ lệ thực hiện (%)", compute="_compute_chenh_lech", store=True
    )

    # -------------------------------------------------------------------------
    # Trạng thái
    # -------------------------------------------------------------------------
    trang_thai = fields.Selection([
        ('lap_ke_hoach', 'Lập kế hoạch'),
        ('cho_duyet', 'Chờ duyệt'),
        ('da_duyet', 'Đã duyệt'),
        ('dang_thuc_hien', 'Đang thực hiện'),
        ('hoan_thanh', 'Hoàn thành'),
        ('vuot_ngan_sach', 'Vượt ngân sách'),
        ('huy', 'Đã hủy'),
    ], string="Trạng thái", default='lap_ke_hoach', readonly=True)

    canh_bao_vuot = fields.Boolean(
        "Cảnh báo vượt ngân sách", compute="_compute_canh_bao", store=True
    )

    # Chi tiết theo tháng
    chi_tiet_ids = fields.One2many(
        'ngan_sach_mua_sam.chi_tiet', 'ngan_sach_id', string="Chi tiết theo tháng"
    )

    # Danh sách tài sản đã mua trong năm (liên kết)
    tai_san_ids = fields.One2many(
        'tai_san', string="Tài sản đã mua",
        compute="_compute_tai_san_ids"
    )
    so_tai_san_da_mua = fields.Integer(
        "Số tài sản đã mua", compute="_compute_thuc_te", store=True
    )

    # =========================================================================
    # COMPUTE
    # =========================================================================
    @api.depends('nam', 'danh_muc_loai_tai_san_id')
    def _compute_tai_san_ids(self):
        for rec in self:
            domain = [('ngay_mua', '>=', f'{rec.nam}-01-01'),
                      ('ngay_mua', '<=', f'{rec.nam}-12-31')]
            if rec.danh_muc_loai_tai_san_id:
                domain.append(('danh_muc_loai_tai_san_id', '=', rec.danh_muc_loai_tai_san_id.id))
            rec.tai_san_ids = self.env['tai_san'].search(domain)

    @api.depends('nam', 'danh_muc_loai_tai_san_id')
    def _compute_thuc_te(self):
        for rec in self:
            domain = [('ngay_mua', '>=', f'{rec.nam}-01-01'),
                      ('ngay_mua', '<=', f'{rec.nam}-12-31')]
            if rec.danh_muc_loai_tai_san_id:
                domain.append(('danh_muc_loai_tai_san_id', '=', rec.danh_muc_loai_tai_san_id.id))
            tai_san = self.env['tai_san'].search(domain)
            rec.so_tien_thuc_te = sum(tai_san.mapped('tong_gia_tri'))
            rec.so_tai_san_da_mua = len(tai_san)

    @api.depends('so_tien_ke_hoach', 'so_tien_thuc_te')
    def _compute_chenh_lech(self):
        for rec in self:
            rec.chenh_lech = rec.so_tien_ke_hoach - rec.so_tien_thuc_te
            if rec.so_tien_ke_hoach > 0:
                rec.ty_le_thuc_hien = (rec.so_tien_thuc_te / rec.so_tien_ke_hoach) * 100
            else:
                rec.ty_le_thuc_hien = 0.0

    @api.depends('chenh_lech')
    def _compute_canh_bao(self):
        for rec in self:
            rec.canh_bao_vuot = rec.chenh_lech < 0

    # =========================================================================
    # CONSTRAINS
    # =========================================================================
    @api.constrains('so_tien_ke_hoach')
    def _check_ngan_sach(self):
        for rec in self:
            if rec.so_tien_ke_hoach <= 0:
                raise ValidationError("Ngân sách kế hoạch phải lớn hơn 0!")

    @api.constrains('nam')
    def _check_nam(self):
        for rec in self:
            if rec.nam < 2000 or rec.nam > 2100:
                raise ValidationError("Năm ngân sách không hợp lệ!")

    # =========================================================================
    # CRUD
    # =========================================================================
    @api.model
    def create(self, vals):
        if vals.get('ma_ngan_sach', 'New') == 'New':
            last = self.search([], order="id desc", limit=1)
            if last and last.ma_ngan_sach and last.ma_ngan_sach.startswith("NS"):
                try:
                    last_num = int(last.ma_ngan_sach[2:])
                except ValueError:
                    last_num = 0
            else:
                last_num = 0
            vals['ma_ngan_sach'] = f"NS{last_num + 1:05d}"
        return super().create(vals)

    # =========================================================================
    # ACTIONS
    # =========================================================================
    def action_gui_duyet(self):
        for rec in self:
            if rec.trang_thai != 'lap_ke_hoach':
                raise ValidationError("Chỉ có thể gửi duyệt từ trạng thái Lập kế hoạch.")
            rec.trang_thai = 'cho_duyet'

    def action_duyet(self):
        for rec in self:
            if rec.trang_thai != 'cho_duyet':
                raise ValidationError("Chỉ có thể duyệt từ trạng thái Chờ duyệt.")
            rec.write({
                'trang_thai': 'da_duyet',
                'ngay_duyet': fields.Date.today(),
                'nguoi_duyet_id': rec.nguoi_duyet_id.id,
            })

    def action_bat_dau_thuc_hien(self):
        for rec in self:
            if rec.trang_thai != 'da_duyet':
                raise ValidationError("Ngân sách phải được duyệt trước.")
            rec.trang_thai = 'dang_thuc_hien'

    def action_hoan_thanh(self):
        for rec in self:
            rec.trang_thai = 'hoan_thanh'

    def action_huy(self):
        for rec in self:
            rec.trang_thai = 'huy'

    def action_cap_nhat_trang_thai(self):
        """Cập nhật trạng thái dựa trên chi tiêu thực tế"""
        for rec in self:
            if rec.trang_thai == 'dang_thuc_hien':
                if rec.ty_le_thuc_hien >= 100:
                    rec.trang_thai = 'vuot_ngan_sach' if rec.chenh_lech < 0 else 'hoan_thanh'

    def action_xem_tai_san(self):
        """Xem danh sách tài sản đã mua trong phạm vi ngân sách"""
        self.ensure_one()
        domain = [('ngay_mua', '>=', f'{self.nam}-01-01'),
                  ('ngay_mua', '<=', f'{self.nam}-12-31')]
        if self.danh_muc_loai_tai_san_id:
            domain.append(('danh_muc_loai_tai_san_id', '=', self.danh_muc_loai_tai_san_id.id))
        return {
            'type': 'ir.actions.act_window',
            'name': f'Tài sản mua năm {self.nam}',
            'res_model': 'tai_san',
            'view_mode': 'tree,form',
            'domain': domain,
        }


class NganSachMuaSamChiTiet(models.Model):
    _name = 'ngan_sach_mua_sam.chi_tiet'
    _description = 'Chi tiết ngân sách theo tháng'
    _order = 'thang'

    ngan_sach_id = fields.Many2one(
        'ngan_sach_mua_sam', string="Ngân sách", required=True, ondelete='cascade'
    )
    thang = fields.Integer("Tháng", required=True)
    ten_thang = fields.Char("Tên tháng", compute="_compute_ten_thang", store=True)
    so_tien_ke_hoach = fields.Float("Kế hoạch (VNĐ)")
    so_tien_thuc_te = fields.Float(
        "Thực tế (VNĐ)", compute="_compute_thuc_te_thang", store=True
    )
    chenh_lech = fields.Float("Chênh lệch (VNĐ)", compute="_compute_chenh_lech_thang", store=True)
    ghi_chu = fields.Char("Ghi chú")

    @api.depends('thang')
    def _compute_ten_thang(self):
        thang_map = {
            1: "Tháng 1", 2: "Tháng 2", 3: "Tháng 3", 4: "Tháng 4",
            5: "Tháng 5", 6: "Tháng 6", 7: "Tháng 7", 8: "Tháng 8",
            9: "Tháng 9", 10: "Tháng 10", 11: "Tháng 11", 12: "Tháng 12",
        }
        for rec in self:
            rec.ten_thang = thang_map.get(rec.thang, f"Tháng {rec.thang}")

    @api.depends('thang', 'ngan_sach_id.nam', 'ngan_sach_id.danh_muc_loai_tai_san_id')
    def _compute_thuc_te_thang(self):
        for rec in self:
            if not rec.ngan_sach_id or not rec.thang:
                rec.so_tien_thuc_te = 0.0
                continue
            nam = rec.ngan_sach_id.nam
            thang_str = f"{rec.thang:02d}"
            domain = [
                ('ngay_mua', '>=', f'{nam}-{thang_str}-01'),
                ('ngay_mua', '<=', f'{nam}-{thang_str}-31'),
            ]
            if rec.ngan_sach_id.danh_muc_loai_tai_san_id:
                domain.append((
                    'danh_muc_loai_tai_san_id', '=',
                    rec.ngan_sach_id.danh_muc_loai_tai_san_id.id
                ))
            tai_san = self.env['tai_san'].search(domain)
            rec.so_tien_thuc_te = sum(tai_san.mapped('tong_gia_tri'))

    @api.depends('so_tien_ke_hoach', 'so_tien_thuc_te')
    def _compute_chenh_lech_thang(self):
        for rec in self:
            rec.chenh_lech = rec.so_tien_ke_hoach - rec.so_tien_thuc_te

    @api.constrains('thang')
    def _check_thang(self):
        for rec in self:
            if not (1 <= rec.thang <= 12):
                raise ValidationError("Tháng phải từ 1 đến 12!")
