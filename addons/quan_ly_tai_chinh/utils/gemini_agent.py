# -*- coding: utf-8 -*-
"""AI Agent Gemini: function calling de tra cuu du lieu va tao phieu trong Odoo."""
import logging
import requests
from datetime import date

_logger = logging.getLogger(__name__)

GEMINI_URL = ("https://generativelanguage.googleapis.com/v1beta/models/"
              "gemini-flash-latest:generateContent")

TOOLS = [{
    "function_declarations": [
        {
            "name": "dem_tai_san",
            "description": ("Dem so luong tai san. Co the loc theo trang thai: "
                            "dang_su_dung, bao_tri, hong, da_thanh_ly. "
                            "Bo trong de dem tat ca."),
            "parameters": {
                "type": "object",
                "properties": {"trang_thai": {"type": "string"}},
            },
        },
        {
            "name": "thong_ke_tai_chinh",
            "description": ("Lay tong thu, tong chi da duyet trong thang hien tai "
                            "va so phieu dang cho duyet."),
            "parameters": {"type": "object", "properties": {}},
        },
        {
            "name": "danh_sach_tai_san",
            "description": ("Liet ke toi da 15 tai san (ten, trang thai, nguyen gia, "
                            "gia tri con lai). Co the loc theo trang thai."),
            "parameters": {
                "type": "object",
                "properties": {"trang_thai": {"type": "string"}},
            },
        },
        {
            "name": "tao_phieu",
            "description": ("Tao phieu thu hoac chi moi o trang thai Nhap. "
                            "loai la 'thu' hoac 'chi'."),
            "parameters": {
                "type": "object",
                "properties": {
                    "loai": {"type": "string"},
                    "noi_dung": {"type": "string"},
                    "so_tien": {"type": "number"},
                },
                "required": ["loai", "noi_dung", "so_tien"],
            },
        },
    ]
}]


def _thuc_thi(env, ten, args):
    args = args or {}
    if ten == "dem_tai_san":
        dom = [("trang_thai", "=", args["trang_thai"])] if args.get("trang_thai") else []
        return {"so_luong": env["tai_san"].search_count(dom)}
    if ten == "thong_ke_tai_chinh":
        t = date.today()
        dau = "%04d-%02d-01" % (t.year, t.month)
        Ph = env["tai_chinh.phieu_thu_chi"]
        thu = sum(Ph.search([("loai_phieu", "=", "thu"), ("trang_thai", "=", "da_duyet"),
                             ("ngay_duyet", ">=", dau)]).mapped("so_tien"))
        chi = sum(Ph.search([("loai_phieu", "=", "chi"), ("trang_thai", "=", "da_duyet"),
                             ("ngay_duyet", ">=", dau)]).mapped("so_tien"))
        cho = Ph.search_count([("trang_thai", "=", "cho_duyet")])
        return {"tong_thu_thang": thu, "tong_chi_thang": chi, "phieu_cho_duyet": cho}
    if ten == "danh_sach_tai_san":
        dom = [("trang_thai", "=", args["trang_thai"])] if args.get("trang_thai") else []
        recs = env["tai_san"].search(dom, limit=15)
        return {"danh_sach": [{
            "ten": r.ten_tai_san, "trang_thai": r.trang_thai,
            "nguyen_gia": r.gia_tri_tai_san, "con_lai": r.gia_tri_con_lai,
        } for r in recs]}
    if ten == "tao_phieu":
        loai = "thu" if args.get("loai") == "thu" else "chi"
        nguoi = env["nhan_vien"].search([], limit=1)
        if not nguoi:
            return {"loi": "Chua co nhan vien. Vao Quan ly Nhan su tao nhan vien truoc."}
        phieu = env["tai_chinh.phieu_thu_chi"].create({
            "loai_phieu": loai, "nguon_goc": "khac",
            "ten_noi_dung": args.get("noi_dung", "(khong co noi dung)"),
            "so_tien": args.get("so_tien", 0),
            "nguoi_lap_id": nguoi.id,
        })
        return {"ma_phieu": phieu.ma_phieu,
                "ket_qua": "Da tao phieu %s o trang thai Nhap" % loai}
    return {"loi": "Ham khong ho tro: %s" % ten}


def chat_agent(env, cau_hoi):
    api_key = env["ir.config_parameter"].sudo().get_param(
        "quan_ly_tai_chinh.gemini_api_key", "")
    if not api_key:
        return ("Chua cau hinh Gemini API key. Vao Quan ly Tai chinh > Cau hinh > "
                "Cai dat chung de nhap key.")
    url = GEMINI_URL + "?key=" + api_key
    he_thong = ("Ban la AI Agent cua phan mem Quan ly Tai san va Tai chinh cua cong ty "
                "kinh doanh linh kien dien tu may tinh tai Viet Nam. Ban CO THE goi ham "
                "de tra cuu du lieu that va tao phieu thu/chi. Khi nguoi dung hoi so lieu, "
                "hay goi ham phu hop roi tra loi bang tieng Viet co dau, ngan gon, ro rang.")
    contents = [{"role": "user", "parts": [{"text": he_thong + "\n\nYeu cau: " + (cau_hoi or "")}]}]
    try:
        for _ in range(5):
            payload = {"contents": contents, "tools": TOOLS,
                       "generationConfig": {"temperature": 0.3}}
            r = requests.post(url, json=payload, timeout=45)
            r.raise_for_status()
            cand = r.json()["candidates"][0]["content"]
            parts = cand.get("parts", [])
            fcalls = [p["functionCall"] for p in parts if "functionCall" in p]
            if not fcalls:
                return "".join(p.get("text", "") for p in parts) or "(AI khong tra loi)"
            contents.append(cand)
            resp_parts = []
            for fc in fcalls:
                kq = _thuc_thi(env, fc.get("name"), fc.get("args"))
                resp_parts.append({"functionResponse": {"name": fc.get("name"), "response": kq}})
            contents.append({"role": "function", "parts": resp_parts})
        return "AI da xu ly nhieu buoc. Thu hoi lai ro hon nhe."
    except Exception as e:
        _logger.error("AI Agent loi (fallback chat thuong): %s", e)
        try:
            from .gemini_helper import ask_gemini
            return ask_gemini(api_key, he_thong + "\n\nCau hoi: " + (cau_hoi or ""))
        except Exception:
            return "Loi khi goi AI: %s" % str(e)
