# -*- coding: utf-8 -*-
from odoo import api, fields, models


class TaiChinhCauHinh(models.TransientModel):
    _name = "tai_chinh.cau_hinh"
    _description = "Cau hinh Quan ly Tai chinh"

    bat_telegram = fields.Boolean("Bat thong bao Telegram", default=True)
    telegram_bot_token = fields.Char("Telegram Bot Token")
    telegram_chat_id = fields.Char("Telegram Chat ID")
    bat_email = fields.Boolean("Bat thong bao Email", default=True)
    email_nhan_thong_bao = fields.Char("Email nhan thong bao")
    ai_base_url = fields.Char("AI Base URL", default="https://9rt.nhuuduc.com/v1")
    ai_api_key = fields.Char("AI API Key")
    ai_model = fields.Char("AI Model", default="gemini-2.5-flash")

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        P = self.env["ir.config_parameter"].sudo()
        res.update({
            "bat_telegram": P.get_param("quan_ly_tai_chinh.bat_telegram", "True") == "True",
            "telegram_bot_token": P.get_param("quan_ly_tai_chinh.telegram_bot_token", ""),
            "telegram_chat_id": P.get_param("quan_ly_tai_chinh.telegram_chat_id", ""),
            "bat_email": P.get_param("quan_ly_tai_chinh.bat_email", "True") == "True",
            "email_nhan_thong_bao": P.get_param("quan_ly_tai_chinh.email_nhan_thong_bao", ""),
            "ai_base_url": P.get_param("quan_ly_tai_chinh.ai_base_url", "https://9rt.nhuuduc.com/v1"),
            "ai_api_key": P.get_param("quan_ly_tai_chinh.ai_api_key", ""),
            "ai_model": P.get_param("quan_ly_tai_chinh.ai_model", "gemini-2.5-flash"),
        })
        return res

    def action_luu(self):
        self.ensure_one()
        P = self.env["ir.config_parameter"].sudo()
        P.set_param("quan_ly_tai_chinh.bat_telegram", "True" if self.bat_telegram else "False")
        P.set_param("quan_ly_tai_chinh.telegram_bot_token", self.telegram_bot_token or "")
        P.set_param("quan_ly_tai_chinh.telegram_chat_id", self.telegram_chat_id or "")
        P.set_param("quan_ly_tai_chinh.bat_email", "True" if self.bat_email else "False")
        P.set_param("quan_ly_tai_chinh.email_nhan_thong_bao", self.email_nhan_thong_bao or "")
        P.set_param("quan_ly_tai_chinh.ai_base_url", self.ai_base_url or "")
        P.set_param("quan_ly_tai_chinh.ai_api_key", self.ai_api_key or "")
        P.set_param("quan_ly_tai_chinh.ai_model", self.ai_model or "")
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {"title": "Da luu", "message": "Da luu cau hinh thanh cong.",
                       "type": "success", "sticky": False,
                       "next": {"type": "ir.actions.act_window_close"}},
        }
