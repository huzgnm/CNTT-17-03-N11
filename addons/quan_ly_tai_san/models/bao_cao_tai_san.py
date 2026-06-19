# -*- coding: utf-8 -*-
from odoo import models, fields, api


class BaoCaoTaiSan(models.Model):
    """
    Báo cáo tài chính tổng hợp tài sản theo năm.
    Mỗi record = 1 bản báo cáo cho 1 năm, tổng hợp số liệu từ toàn bộ module.
    """
    _name = 'bao_cao_tai_san'
    _description = 'Báo cáo tài chính tổng hợp tài sản'
    _rec_name = 'ten_bao_cao'
    _order = 'nam_bao_cao desc'

    # -------------------------------------------------------------------------
    # Thông tin chung
    # -------------------------------------------------------------------------
    ten_bao_cao = fields.Char("Tên báo cáo", required=True)
    nam_bao_cao = fields.Integer(
        "Năm báo cáo", required=True,
        default=lambda self: fields.Date.today().year
    )
    ngay_tao = fields.Date("Ngày tạo báo cáo", default=fields.Date.today, readonly=True)
    nguoi_tao_id = fields.Many2one('nhan_vien', string="Người lập báo cáo")
    ghi_chu = fields.Text("Ghi chú")

    # -------------------------------------------------------------------------
    # Tổng quan tài sản
    # -------------------------------------------------------------------------
    tong_so_tai_san = fields.Integer(
        "Tổng số tài sản", compute="_compute_tong_quan", store=True
    )
    tong_nguyen_gia = fields.Float(
        "Tổng nguyên giá (VNĐ)", compute="_compute_tong_quan", store=True
    )
    tong_da_khau_hao = fields.Float(
        "Tổng đã khấu hao (VNĐ)", compute="_compute_tong_quan", store=True
    )
    tong_gia_tri_con_lai = fields.Float(
        "Tổng giá trị còn lại (VNĐ)", compute="_compute_tong_quan", store=True
    )

    # Tài sản theo trạng thái
    so_dang_su_dung = fields.Integer(
        "Đang sử dụng", compute="_compute_tong_quan", store=True
    )
    so_bao_tri = fields.Integer(
        "Đang bảo trì", compute="_compute_tong_quan", store=True
    )
    so_hong = fields.Integer(
        "Hỏng/Mất", compute="_compute_tong_quan", store=True
    )

    # -------------------------------------------------------------------------
    # Hoạt động trong năm
    # -------------------------------------------------------------------------
    # Mua mới
    so_mua_trong_nam = fields.Integer(
        "Số tài sản mua mới", compute="_compute_hoat_dong_nam", store=True
    )
    tong_gia_tri_mua = fields.Float(
        "Tổng giá trị mua mới (VNĐ)", compute="_compute_hoat_dong_nam", store=True
    )

    # Khấu hao trong năm
    khau_hao_trong_nam = fields.Float(
        "Khấu hao trong năm (VNĐ)", compute="_compute_hoat_dong_nam", store=True
    )
    so_ky_khau_hao = fields.Integer(
        "Số kỳ khấu hao đã ghi sổ", compute="_compute_hoat_dong_nam", store=True
    )

    # Bảo trì trong năm
    so_lan_bao_tri = fields.Integer(
        "Số lần bảo trì", compute="_compute_hoat_dong_nam", store=True
    )
    tong_chi_phi_bao_tri = fields.Float(
        "Tổng chi phí bảo trì (VNĐ)", compute="_compute_hoat_dong_nam", store=True
    )

    # Thanh lý trong năm
    so_lan_thanh_ly = fields.Integer(
        "Số lần thanh lý", compute="_compute_hoat_dong_nam", store=True
    )
    tong_thu_hoi_thanh_ly = fields.Float(
        "Tổng thu hồi thanh lý (VNĐ)", compute="_compute_hoat_dong_nam", store=True
    )
    lai_lo_thanh_ly = fields.Float(
        "Lãi/(Lỗ) thanh lý (VNĐ)", compute="_compute_hoat_dong_nam", store=True
    )

    # Mượn trả
    so_lan_muon = fields.Integer(
        "Số lần mượn tài sản", compute="_compute_hoat_dong_nam", store=True
    )

    # -------------------------------------------------------------------------
    # Chi tiết theo loại tài sản
    # -------------------------------------------------------------------------
    chi_tiet_ids = fields.One2many(
        'bao_cao_tai_san.chi_tiet', 'bao_cao_id', string="Chi tiết theo loại tài sản"
    )

    # =========================================================================
    # COMPUTE
    # =========================================================================
    @api.depends('nam_bao_cao')
    def _compute_tong_quan(self):
        for rec in self:
            all_ts = self.env['tai_san'].search([])
            rec.tong_so_tai_san = len(all_ts)
            rec.tong_nguyen_gia = sum(all_ts.mapped('gia_tri_tai_san'))
            rec.tong_da_khau_hao = sum(all_ts.mapped('tong_da_khau_hao'))
            rec.tong_gia_tri_con_lai = sum(all_ts.mapped('gia_tri_con_lai'))
            rec.so_dang_su_dung = len(all_ts.filtered(lambda t: t.trang_thai == 'dang_su_dung'))
            rec.so_bao_tri = len(all_ts.filtered(lambda t: t.trang_thai == 'bao_tri'))
            rec.so_hong = len(all_ts.filtered(lambda t: t.trang_thai in ('hong', 'mat')))

    @api.depends('nam_bao_cao')
    def _compute_hoat_dong_nam(self):
        for rec in self:
            nam = rec.nam_bao_cao
            tu_ngay = f'{nam}-01-01'
            den_ngay = f'{nam}-12-31'

            # Mua mới
            ts_mua = self.env['tai_san'].search([
                ('ngay_mua', '>=', tu_ngay),
                ('ngay_mua', '<=', den_ngay),
            ])
            rec.so_mua_trong_nam = len(ts_mua)
            rec.tong_gia_tri_mua = sum(ts_mua.mapped('tong_gia_tri'))

            # Khấu hao
            kh = self.env['khau_hao_hang_thang'].search([
                ('ky_nam', '=', nam),
                ('trang_thai', '=', 'da_ghi_so'),
            ])
            rec.so_ky_khau_hao = len(kh)
            rec.khau_hao_trong_nam = sum(kh.mapped('so_tien_khau_hao'))

            # Bảo trì
            bt = self.env['bao_tri'].search([
                ('ngay_bao_tri', '>=', tu_ngay),
                ('ngay_bao_tri', '<=', den_ngay),
                ('tinh_trang', 'not in', ['huy']),
            ])
            rec.so_lan_bao_tri = len(bt)
            rec.tong_chi_phi_bao_tri = sum(bt.mapped('chi_phi_bao_tri'))

            # Thanh lý
            tl = self.env['thanh_ly'].search([
                ('ngay_thanh_ly', '>=', tu_ngay),
                ('ngay_thanh_ly', '<=', den_ngay),
                ('trang_thai', '=', 'da_ghi_so'),
            ])
            rec.so_lan_thanh_ly = len(tl)
            rec.tong_thu_hoi_thanh_ly = sum(tl.mapped('gia_tri_thanh_ly'))
            rec.lai_lo_thanh_ly = sum(tl.mapped('lai_lo_thanh_ly'))

            # Mượn trả
            mt = self.env['muon_tra'].search([
                ('thoi_gian_muon', '>=', tu_ngay),
                ('thoi_gian_muon', '<=', den_ngay),
            ])
            rec.so_lan_muon = len(mt)

    # =========================================================================
    # ACTIONS
    # =========================================================================
    def action_lam_moi(self):
        """Tính lại toàn bộ số liệu báo cáo"""
        for rec in self:
            rec._compute_tong_quan()
            rec._compute_hoat_dong_nam()
            rec._tao_chi_tiet()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Cập nhật báo cáo',
                'message': 'Đã làm mới số liệu báo cáo thành công.',
                'type': 'success',
                'sticky': False,
            },
        }

    def _tao_chi_tiet(self):
        """Tạo/cập nhật chi tiết theo từng loại tài sản"""
        self.ensure_one()
        self.chi_tiet_ids.unlink()

        all_loai = self.env['danh_muc_loai_tai_san'].search([])
        for loai in all_loai:
            tai_san = self.env['tai_san'].search([
                ('danh_muc_loai_tai_san_id', '=', loai.id)
            ])
            if not tai_san:
                continue

            nam = self.nam_bao_cao
            kh = self.env['khau_hao_hang_thang'].search([
                ('tai_san_id', 'in', tai_san.ids),
                ('ky_nam', '=', nam),
                ('trang_thai', '=', 'da_ghi_so'),
            ])
            bt = self.env['bao_tri'].search([
                ('tai_san_id', 'in', tai_san.ids),
                ('ngay_bao_tri', '>=', f'{nam}-01-01'),
                ('ngay_bao_tri', '<=', f'{nam}-12-31'),
            ])

            self.env['bao_cao_tai_san.chi_tiet'].create({
                'bao_cao_id': self.id,
                'danh_muc_loai_tai_san_id': loai.id,
                'so_tai_san': len(tai_san),
                'tong_nguyen_gia': sum(tai_san.mapped('gia_tri_tai_san')),
                'tong_da_khau_hao': sum(tai_san.mapped('tong_da_khau_hao')),
                'tong_gia_tri_con_lai': sum(tai_san.mapped('gia_tri_con_lai')),
                'khau_hao_trong_nam': sum(kh.mapped('so_tien_khau_hao')),
                'chi_phi_bao_tri': sum(bt.mapped('chi_phi_bao_tri')),
            })

    def action_tao_bao_cao_day_du(self):
        """Tạo chi tiết theo loại tài sản và làm mới số liệu"""
        self.action_lam_moi()
        for rec in self:
            rec._tao_chi_tiet()


class BaoCaoTaiSanChiTiet(models.Model):
    _name = 'bao_cao_tai_san.chi_tiet'
    _description = 'Chi tiết báo cáo theo loại tài sản'
    _order = 'tong_nguyen_gia desc'

    bao_cao_id = fields.Many2one(
        'bao_cao_tai_san', string="Báo cáo", required=True, ondelete='cascade'
    )
    danh_muc_loai_tai_san_id = fields.Many2one(
        'danh_muc_loai_tai_san', string="Loại tài sản", required=True
    )
    so_tai_san = fields.Integer("Số tài sản")
    tong_nguyen_gia = fields.Float("Tổng nguyên giá (VNĐ)")
    tong_da_khau_hao = fields.Float("Đã khấu hao (VNĐ)")
    tong_gia_tri_con_lai = fields.Float("Giá trị còn lại (VNĐ)")
    khau_hao_trong_nam = fields.Float("KH trong năm (VNĐ)")
    chi_phi_bao_tri = fields.Float("Chi phí bảo trì (VNĐ)")
    ty_le_khau_hao = fields.Float(
        "Tỷ lệ đã KH (%)", compute="_compute_ty_le", store=True
    )

    @api.depends('tong_nguyen_gia', 'tong_da_khau_hao')
    def _compute_ty_le(self):
        for rec in self:
            if rec.tong_nguyen_gia > 0:
                rec.ty_le_khau_hao = (rec.tong_da_khau_hao / rec.tong_nguyen_gia) * 100
            else:
                rec.ty_le_khau_hao = 0.0
