# -*- coding: utf-8 -*-
"""
Helper gui thong bao Telegram cho module Quan ly Tai Chinh.

Cau hinh:
  - quan_ly_tai_chinh.telegram_bot_token : token cua bot Telegram
  - quan_ly_tai_chinh.telegram_chat_id   : ID cua group/user nhan thong bao

Huong dan lay config:
  1. Tao bot qua @BotFather, lay token.
  2. Them bot vao group, gui 1 tin nhan bat ky.
  3. Goi https://api.telegram.org/bot<TOKEN>/getUpdates de lay chat_id.
  4. Vao Settings > Technical > Parameters > System Parameters trong Odoo
     va them 2 khoa tren.
"""

import requests
import logging

_logger = logging.getLogger(__name__)

TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/sendMessage"


def send_telegram_message(env, message: str) -> bool:
    """
    Gui tin nhan den Telegram.
    Tra ve True neu thanh cong, False neu that bai (khong raise exception).
    """
    ICP = env["ir.config_parameter"].sudo()
    token = ICP.get_param("quan_ly_tai_chinh.telegram_bot_token", "")
    chat_id = ICP.get_param("quan_ly_tai_chinh.telegram_chat_id", "")

    if not token or not chat_id:
        _logger.warning(
            "Telegram chua duoc cau hinh. "
            "Vui long them quan_ly_tai_chinh.telegram_bot_token "
            "va quan_ly_tai_chinh.telegram_chat_id vao System Parameters."
        )
        return False

    url = TELEGRAM_API_URL.format(token=token)
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
    }

    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        _logger.info("Telegram: gui tin nhan thanh cong den chat_id=%s", chat_id)
        return True
    except Exception as e:
        _logger.error("Telegram: gui tin nhan that bai: %s", str(e))
        return False
