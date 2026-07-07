# -*- coding: utf-8 -*-
"""Client goi AI qua endpoint kieu OpenAI (9router / OpenAI-compatible)."""
import logging
import requests

_logger = logging.getLogger(__name__)

DEFAULT_BASE = "http://localhost:20128/v1"
DEFAULT_MODEL = "gemini-2.5-flash"


def _cfg(env):
    ICP = env["ir.config_parameter"].sudo()
    base = (ICP.get_param("quan_ly_tai_chinh.ai_base_url") or DEFAULT_BASE).rstrip("/")
    key = ICP.get_param("quan_ly_tai_chinh.ai_api_key", "")
    model = ICP.get_param("quan_ly_tai_chinh.ai_model") or DEFAULT_MODEL
    return base, key, model


def goi_ai(env, messages, tools=None, temperature=0.3):
    base, key, model = _cfg(env)
    if not key:
        raise Exception("Chua cau hinh AI API key. Vao Quan ly Tai chinh > "
                        "Cau hinh > Cai dat chung de nhap key.")
    payload = {"model": model, "messages": messages, "temperature": temperature}
    if tools:
        payload["tools"] = tools
    r = requests.post(
        base + "/chat/completions",
        json=payload,
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()


def hoi_text(env, prompt):
    data = goi_ai(env, [{"role": "user", "content": prompt}])
    return data["choices"][0]["message"].get("content") or "(khong co phan hoi)"
