# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError


class KhauHaoHangThang(models.Model):
    _name = 'khau_hao_hang_thang'
    _description = 'Khấu hao tài sản hàng tháng'
    _rec_name = 'ma_khau_hao'
    _order = 'ky_nam desc, ky_thang desc'

    ma_khau_hao = fields.Char(
        "Mã khấu hao", required=True, copy=False, readonly=True, default="New"
    )
    tai_san_id = fields.Many2one(
        'tai_san', string="Tài sản", required=True, ondelete='cascade'
    )
    ten_tai_san = fields.Char(
        related='tai_san_id.ten_tai_san', string="Tên tài sản", readonly=True, store=True
    )
    ky_thang = fields.Integer("Tháng", required=True)
    ky_nam = fields.Integer("Năm", required=True)
    ky_khau_hao = fields.Char(
        "Kỳ khấu hao", compute="_compute_ky_khau_hao", store=True
    )

    so_tien_khau_hao = fields.Float("Số tiền khấu hao (VNĐ)", required=True)
    gia_tri_truoc_kh = fields.Float("Giá trị trước khấu hao (VNĐ)")
    gia_tri_sau_kh = fields.Float(
        "Giá trị còn lại sau khấu hao (VNĐ)",
        compute="_compute_gia_tri_sau_kh", store=True
    )
    luy_ke_khau_hao = fields.Float(
        "Khấu hao lũy kế (VNĐ)", compute="_compute_luy_ke", store=True
    )

    ngay_ghi_nhan = fields.Date("Ngày ghi nhận", default=fields.Date.today)
    account_move_id = fields.Many2one(
        'account.move', string="Bút toán kế toán", readonly=True, copy=False
    )
    trang_thai = fields.Selection([
        ('nhap', 'Nháp'),
        ('da_ghi_so', 'Đã ghi sổ'),
        ('huy', 'Đã hủy'),
    ], string="Trạng thái", default='nhap', readonly=True)

    ghi_chu = fields.Text("Ghi chú")

    # -------------------------------------------------------------------------
    # Compute
    # -------------------------------------------------------------------------
    @api.depends('ky_thang', 'ky_nam')
    def _compute_ky_khau_hao(self):
        for rec in self:
            if rec.ky_thang and rec.ky_nam:
                rec.ky_khau_hao = f"T{rec.ky_thang:02d}/{rec.ky_nam}"
            else:
                rec.ky_khau_hao = ""

    @api.depends('gia_tri_truoc_kh', 'so_tien_khau_hao')
    def _compute_gia_tri_sau_kh(self):
        for rec in self:
            rec.gia_tri_sau_kh = max(rec.gia_tri_truoc_kh - rec.so_tien_khau_hao, 0)

    @api.depends('tai_san_id', 'ky_thang', 'ky_nam', 'trang_thai')
    def _compute_luy_ke(self):
        for rec in self:
            domain = [
                ('tai_san_id', '=', rec.tai_san_id.id),
                ('trang_thai', '=', 'da_ghi_so'),
                '|',
                ('ky_nam', '<', rec.ky_nam),
                '&',
                ('ky_nam', '=', rec.ky_nam),
                ('ky_thang', '<=', rec.ky_thang),
            ]
            tat_ca = self.search(domain)
            rec.luy_ke_khau_hao = sum(tat_ca.mapped('so_tien_khau_hao'))

    # -------------------------------------------------------------------------
    # CRUD
    # -------------------------------------------------------------------------
    @api.model
    def create(self, vals):
        if vals.get('ma_khau_hao', 'New') == 'New':
            last = self.search([], order="id desc", limit=1)
            if last and last.ma_khau_hao and last.ma_khau_hao.startswith("KH"):
                try:
                    last_num = int(last.ma_khau_hao[2:])
                except ValueError:
                    last_num = 0
            else:
                last_num = 0
            vals['ma_khau_hao'] = f"KH{last_num + 1:06d}"
        return super().create(vals)

    # -------------------------------------------------------------------------
    # Actions
    # -------------------------------------------------------------------------
    def action_ghi_so(self):
        """Tạo bút toán kế toán và ghi sổ khấu hao"""
        for rec in self:
            if rec.trang_thai != 'nhap':
                raise UserError(f"Bản ghi {rec.ma_khau_hao} không ở trạng thái Nháp.")

            tai_san = rec.tai_san_id
            if not tai_san.journal_id:
                raise UserError(
                    f"Tài sản '{tai_san.ten_tai_san}' chưa thiết lập Sổ nhật ký kế toán."
                )
            if not tai_san.tai_khoan_khau_hao_id:
                raise UserError(
                    f"Tài sản '{tai_san.ten_tai_san}' chưa thiết lập Tài khoản chi phí khấu hao."
                )
            if not tai_san.tai_khoan_luy_ke_id:
                raise UserError(
                    f"Tài sản '{tai_san.ten_tai_san}' chưa thiết lập Tài khoản khấu hao lũy kế."
                )

            move_vals = {
                'journal_id': tai_san.journal_id.id,
                'date': rec.ngay_ghi_nhan,
                'ref': f"Khấu hao tài sản {tai_san.ma_tai_san} - {rec.ky_khau_hao}",
                'line_ids': [
                    # Debit: Chi phí khấu hao
                    (0, 0, {
                        'account_id': tai_san.tai_khoan_khau_hao_id.id,
                        'name': f"Chi phí khấu hao {tai_san.ten_tai_san} {rec.ky_khau_hao}",
                        'debit': rec.so_tien_khau_hao,
                        'credit': 0.0,
                    }),
                    # Credit: Khấu hao lũy kế
                    (0, 0, {
                        'account_id': tai_san.tai_khoan_luy_ke_id.id,
                        'name': f"Khấu hao lũy kế {tai_san.ten_tai_san} {rec.ky_khau_hao}",
                        'debit': 0.0,
                        'credit': rec.so_tien_khau_hao,
                    }),
                ],
            }
            move = self.env['account.move'].create(move_vals)
            move.action_post()

            rec.write({
                'account_move_id': move.id,
                'trang_thai': 'da_ghi_so',
            })

    def action_huy(self):
        """Hủy bút toán và đặt lại trạng thái nháp"""
        for rec in self:
            if rec.trang_thai == 'huy':
                raise UserError(f"Bản ghi {rec.ma_khau_hao} đã bị hủy rồi.")
            if rec.account_move_id and rec.account_move_id.state == 'posted':
                rec.account_move_id.button_cancel()
                rec.account_move_id.button_draft()
                rec.account_move_id.unlink()
            rec.write({'trang_thai': 'huy', 'account_move_id': False})

    def action_xem_but_toan(self):
        """Mở bút toán kế toán liên quan"""
        self.ensure_one()
        if not self.account_move_id:
            raise UserError("Chưa có bút toán cho bản ghi này.")
        return {
            'type': 'ir.actions.act_window',
            'name': 'Bút toán kế toán',
            'res_model': 'account.move',
            'res_id': self.account_move_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
