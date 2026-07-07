# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class AiChatController(http.Controller):

    @http.route("/quan_ly_tai_chinh/ai_ask", type="json", auth="user")
    def ai_ask(self, question=None, **kw):
        from ..utils.gemini_agent import chat_agent
        if not question:
            return {"answer": "Vui long nhap cau hoi."}
        try:
            return {"answer": chat_agent(request.env, question)}
        except Exception as e:
            return {"answer": "Loi: %s" % str(e)}
