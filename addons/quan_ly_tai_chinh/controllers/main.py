# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class AiChatController(http.Controller):

    @http.route("/quan_ly_tai_chinh/ai_ask", type="json", auth="user")
    def ai_ask(self, question=None, **kw):
        from ..utils.gemini_helper import ask_gemini
        api_key = request.env["ir.config_parameter"].sudo().get_param(
            "quan_ly_tai_chinh.gemini_api_key", "")
        if not api_key:
            return {"answer": "Chua cau hinh Gemini API key. Vao Settings > Technical > "
                    "System Parameters, them khoa 'quan_ly_tai_chinh.gemini_api_key'."}
        if not question:
            return {"answer": "Vui long nhap cau hoi."}
        TaiSan = request.env["tai_san"]
        boi_canh = ("Boi canh he thong: co %d tai san (%d dang su dung, %d dang bao tri)." % (
            TaiSan.search_count([]),
            TaiSan.search_count([("trang_thai", "=", "dang_su_dung")]),
            TaiSan.search_count([("trang_thai", "=", "bao_tri")]),
        ))
        prompt = ("Ban la tro ly AI cho phan mem Quan ly Tai san va Tai chinh cua cong ty "
                  "kinh doanh linh kien dien tu may tinh tai Viet Nam. Tra loi ngan gon, "
                  "ro rang bang tieng Viet co dau.\n\n" + boi_canh + "\n\nCau hoi: " + question)
        try:
            return {"answer": ask_gemini(api_key, prompt)}
        except Exception as e:
            return {"answer": "Loi khi goi Gemini API: %s" % str(e)}
