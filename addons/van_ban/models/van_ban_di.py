from odoo import models, fields


class VanBanDi(models.Model):
    _name = 'van_ban_di'
    _description = 'Bảng chứa thông tin văn bản đi'

    ma_van_ban_di = fields.Char("Mã văn bản đi", required=True)
    ten_van_ban_di = fields.Char("Tên văn bản đi", required=True)
