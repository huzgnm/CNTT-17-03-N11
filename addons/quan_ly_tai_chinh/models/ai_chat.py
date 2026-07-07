# -*- coding: utf-8 -*-
from odoo import models, fields
from odoo.exceptions import UserError


class TaiChinhAiChat(models.TransientModel):
    _name = "tai_chinh.ai_chat"
    _description = "Tro ly AI Gemini - Hoi dap"

    cau_hoi = fields.Text("Cau hoi", required=True)
    cau_tra_loi = fields.Text("Cau tra loi cua AI", readonly=True)

    def _lay_boi_canh(self):
        TaiSan = self.env["tai_san"]
        tong = TaiSan.search_count([])
        dang_dung = TaiSan.search_count([("trang_thai", "=", "dang_su_dung")])
        bao_tri = TaiSan.search_count([("trang_thai", "=", "bao_tri")])
        hong = TaiSan.search_count([("trang_thai", "=", "hong")])
        return ("Boi canh he thong hien tai: co %d tai san (%d dang su dung, "
                "%d dang bao tri, %d bi hong)." % (tong, dang_dung, bao_tri, hong))

    def action_hoi(self):
        from ..utils.ai_client import hoi_text
        self.ensure_one()
        prompt = (
            "Ban la tro ly AI cho phan mem Quan ly Tai san va Tai chinh cua mot cong ty "
            "kinh doanh linh kien dien tu may tinh tai Viet Nam. "
            "Tra loi ngan gon, ro rang, thuc te bang tieng Viet co dau.\n\n"
            + self._lay_boi_canh() + "\n\n"
            "Cau hoi cua nguoi dung: " + (self.cau_hoi or ""))
        try:
            self.cau_tra_loi = hoi_text(self.env, prompt)
        except Exception as e:
            self.cau_tra_loi = "Loi khi goi AI: %s" % str(e)
        return {
            "type": "ir.actions.act_window",
            "res_model": "tai_chinh.ai_chat",
            "res_id": self.id,
            "view_mode": "form",
            "target": "current",
            "name": "Tro ly AI Gemini",
        }
