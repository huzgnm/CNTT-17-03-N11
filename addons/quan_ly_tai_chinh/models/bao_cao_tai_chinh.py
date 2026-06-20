# -*- coding: utf-8 -*-
from odoo import api, fields, models


class BaoCaoTaiChinh(models.Model):
    _name = 'tai_chinh.bao_cao'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Báo cáo tài chính tổng hợp'
    _rec_name = 'ten_bao_cao'
    _order = 'nam desc, id desc'

    ma_bao_cao = fields.Char(
        "Mã báo cáo", required=True, copy=False, readonly=True, default="New"
    )
    ten_bao_cao = fields.Char("Tên báo cáo", required=True)
    ky_bao_cao = fields.Selection([
        ('thang', 'Theo tháng'),
        ('quy', 'Theo quý'),
        ('nam', 'Theo năm'),
    ], string="Kỳ báo cáo", required=True, default='thang')
    thang = fields.Selection(
        [(str(i), f'Tháng {i}') for i in range(1, 13)],
        string="Tháng"
    )
    quy = fields.Selection([
        ('1', 'Quý 1 (T1-T3)'),
        ('2', 'Quý 2 (T4-T6)'),
        ('3', 'Quý 3 (T7-T9)'),
        ('4', 'Quý 4 (T10-T12)'),
    ], string="Quý")
    nam = fields.Integer("Năm", required=True, default=lambda self: fields.Date.today().year)

    nguoi_lap_id = fields.Many2one('nhan_vien', string="Người lập", required=True)
    nguoi_duyet_id = fields.Many2one('nhan_vien', string="Người duyệt", readonly=True)
    ngay_lap = fields.Date("Ngày lập", default=fields.Date.today)

    tong_thu = fields.Float("Tổng thu (VNĐ)", compute="_compute_tong", store=True)
    tong_chi = fields.Float("Tổng chi (VNĐ)", compute="_compute_tong", store=True)
    can_doi = fields.Float("Cân đối (VNĐ)", compute="_compute_tong", store=True)
    chi_bao_tri = fields.Float("Chi bảo trì (VNĐ)", compute="_compute_tong", store=True)
    chi_mua_sam = fields.Float("Chi mua sắm (VNĐ)", compute="_compute_tong", store=True)
    thu_thanh_ly = fields.Float("Thu thanh lý (VNĐ)", compute="_compute_tong", store=True)

    ghi_chu = fields.Text("Nhận xét / Ghi chú")
    trang_thai = fields.Selection([
        ('nhap', 'Nháp'),
        ('da_duyet', 'Đã duyệt'),
    ], string="Trạng thái", default='nhap', tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('ma_bao_cao', 'New') == 'New':
            last = self.search([], order='id desc', limit=1)
            num = int(last.ma_bao_cao[2:]) if last and last.ma_bao_cao.startswith('BC') else 0
            vals['ma_bao_cao'] = f'BC{num + 1:05d}'
        return super().create(vals)

    @api.depends('nam', 'thang', 'quy', 'ky_bao_cao')
    def _compute_tong(self):
        for rec in self:
            domain = [('trang_thai', '=', 'da_duyet'), ('ngay_duyet', '!=', False)]
            if rec.ky_bao_cao == 'thang' and rec.thang:
                m = int(rec.thang)
                domain += [
                    ('ngay_duyet', '>=', f'{rec.nam}-{m:02d}-01'),
                    ('ngay_duyet', '<=', f'{rec.nam}-{m:02d}-31'),
                ]
            elif rec.ky_bao_cao == 'quy' and rec.quy:
                q = int(rec.quy)
                start_m = (q - 1) * 3 + 1
                end_m = start_m + 2
                domain += [
                    ('ngay_duyet', '>=', f'{rec.nam}-{start_m:02d}-01'),
                    ('ngay_duyet', '<=', f'{rec.nam}-{end_m:02d}-31'),
                ]
            else:
                domain += [
                    ('ngay_duyet', '>=', f'{rec.nam}-01-01'),
                    ('ngay_duyet', '<=', f'{rec.nam}-12-31'),
                ]
            phieu = self.env['tai_chinh.phieu_thu_chi'].search(domain)
            thu = sum(p.so_tien for p in phieu if p.loai_phieu == 'thu')
            chi = sum(p.so_tien for p in phieu if p.loai_phieu == 'chi')
            rec.tong_thu = thu
            rec.tong_chi = chi
            rec.can_doi = thu - chi
            rec.chi_bao_tri = sum(p.so_tien for p in phieu if p.loai_phieu == 'chi' and p.nguon_goc == 'bao_tri')
            rec.chi_mua_sam = sum(p.so_tien for p in phieu if p.loai_phieu == 'chi' and p.nguon_goc == 'mua_sam')
            rec.thu_thanh_ly = sum(p.so_tien for p in phieu if p.loai_phieu == 'thu' and p.nguon_goc == 'thanh_ly')

    def action_tinh_toan(self):
        self._compute_tong()
        self.message_post(body="Đã tính toán lại số liệu báo cáo.")

    def action_duyet(self):
        self.write({'trang_thai': 'da_duyet', 'nguoi_duyet_id': False})
        self.message_post(body="Báo cáo đã được duyệt.")
