# -*- coding: utf-8 -*-
import logging
from .telegram_helper import send_telegram_message

_logger = logging.getLogger(__name__)


def gui_thong_bao(env, message, tieu_de="Thong bao Quan ly Tai chinh"):
    """Gui thong bao realtime qua Telegram va Email (theo cau hinh bat/tat)."""
    ICP = env["ir.config_parameter"].sudo()

    if ICP.get_param("quan_ly_tai_chinh.bat_telegram", "True") == "True":
        try:
            send_telegram_message(env, message)
        except Exception as e:
            _logger.error("Notify Telegram loi: %s", e)

    if ICP.get_param("quan_ly_tai_chinh.bat_email", "True") == "True":
        email_to = ICP.get_param("quan_ly_tai_chinh.email_nhan_thong_bao", "")
        if email_to:
            try:
                body = "<div style=\"font-family:Arial,sans-serif\">%s</div>" % message.replace("\n", "<br/>")
                env["mail.mail"].sudo().create({
                    "subject": tieu_de,
                    "body_html": body,
                    "email_to": email_to,
                }).send()
                _logger.info("Notify Email: da gui den %s", email_to)
            except Exception as e:
                _logger.error("Notify Email loi: %s", e)
