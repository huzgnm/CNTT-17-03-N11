# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    qltc_telegram_bot_token = fields.Char(
        "Telegram Bot Token",
        config_parameter="quan_ly_tai_chinh.telegram_bot_token")
    qltc_telegram_chat_id = fields.Char(
        "Telegram Chat ID",
        config_parameter="quan_ly_tai_chinh.telegram_chat_id")
    qltc_gemini_api_key = fields.Char(
        "Gemini API Key",
        config_parameter="quan_ly_tai_chinh.gemini_api_key")
    qltc_email_nhan_thong_bao = fields.Char(
        "Email nhan thong bao",
        config_parameter="quan_ly_tai_chinh.email_nhan_thong_bao")
    qltc_bat_telegram = fields.Boolean(
        "Bat thong bao Telegram",
        config_parameter="quan_ly_tai_chinh.bat_telegram")
    qltc_bat_email = fields.Boolean(
        "Bat thong bao Email",
        config_parameter="quan_ly_tai_chinh.bat_email")
