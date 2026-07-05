# -*- coding: utf-8 -*-
import logging
import requests

_logger = logging.getLogger(__name__)
TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/sendMessage"


def send_telegram_message(env, message: str) -> bool:
    """
    Gui tin nhan Telegram.
    Cau hinh trong Settings > Technical > System Parameters:
      - quan_ly_tai_chinh.telegram_bot_token
      - quan_ly_tai_chinh.telegram_chat_id
    """
    try:
        ICP = env["ir.config_parameter"].sudo()
        token = ICP.get_param("quan_ly_tai_chinh.telegram_bot_token", "")
        chat_id = ICP.get_param("quan_ly_tai_chinh.telegram_chat_id", "")
        if not token or not chat_id:
            _logger.warning("Telegram chua duoc cau hinh (thieu token hoac chat_id).")
            return False
        url = TELEGRAM_API_URL.format(token=token)
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        _logger.info("Telegram: gui tin nhan thanh cong den chat_id=%s", chat_id)
        return True
    except Exception as e:
        _logger.error("Telegram: gui tin nhan that bai: %s", str(e))
        return False
