# -*- coding: utf-8 -*-
"""AI Agent qua endpoint kieu OpenAI (function calling / tool calls)."""
import logging
import json
from .ai_client import goi_ai, hoi_text

_logger = logging.getLogger(__name__)

HE_THONG = ("Ban la AI Agent cua phan mem Quan ly Tai san va Tai chinh cua cong ty "
            "kinh doanh linh kien dien tu may tinh tai Viet Nam. Ban CO THE goi ham de "
            "tra cuu du lieu that va tao phieu thu/chi. Khi nguoi dung hoi so lieu, hay goi "
            "ham phu hop roi tra loi bang tieng Viet co dau, ngan gon, ro rang.")

TOOLS = [
    {"type": "function", "function": {
        "name": "dem_tai_san",
        "description": "Dem so tai san. Loc theo trang thai: dang_su_dung, bao_tri, hong, da_thanh_ly. Bo trong de dem tat ca.",
        "parameters": {"type": "object", "properties": {"trang_thai": {"type": "string"}}},
    }},
    {"type": "function", "function": {
        "name": "thong_ke_tai_chinh",
        "description": "Lay tong thu, tong chi da duyet thang hien tai va so phieu cho duyet.",
        "parameters": {"type": "object", "properties": {}},
    }},
    {"type": "function", "function": {
        "name": "danh_sach_tai_san",
        "description": "Liet ke toi da 15 tai san (ten, trang thai, nguyen gia, gia tri con lai).",
        "parameters": {"type": "object", "properties": {"trang_thai": {"type": "string"}}},
    }},
    {"type": "function", "function": {
        "name": "tao_phieu",
        "description": "Tao phieu thu hoac chi moi o trang thai Nhap. loai la 'thu' hoac 'chi'.",
        "parameters": {"type": "object", "properties": {
            "loai": {"type": "string"}, "noi_dung": {"type": "string"}, "so_tien": {"type": "number"}},
            "required": ["loai", "noi_dung", "so_tien"]},
    }},
]


def _thuc_thi(env, ten, args):
    from datetime import date
    args = args or {}
    if ten == "dem_tai_san":
        dom = [("trang_thai", "=", args["trang_thai"])] if args.get("trang_thai") else []
        return {"so_luong": env["tai_san"].search_count(dom)}
    if ten == "thong_ke_tai_chinh":
        t = date.today()
        dau = "%04d-%02d-01" % (t.year, t.month)
        Ph = env["tai_chinh.phieu_thu_chi"]
        thu = sum(Ph.search([("loai_phieu", "=", "thu"), ("trang_thai", "=", "da_duyet"), ("ngay_duyet", ">=", dau)]).mapped("so_tien"))
        chi = sum(Ph.search([("loai_phieu", "=", "chi"), ("trang_thai", "=", "da_duyet"), ("ngay_duyet", ">=", dau)]).mapped("so_tien"))
        cho = Ph.search_count([("trang_thai", "=", "cho_duyet")])
        return {"tong_thu_thang": thu, "tong_chi_thang": chi, "phieu_cho_duyet": cho}
    if ten == "danh_sach_tai_san":
        dom = [("trang_thai", "=", args["trang_thai"])] if args.get("trang_thai") else []
        recs = env["tai_san"].search(dom, limit=15)
        return {"danh_sach": [{"ten": r.ten_tai_san, "trang_thai": r.trang_thai,
                               "nguyen_gia": r.gia_tri_tai_san, "con_lai": r.gia_tri_con_lai} for r in recs]}
    if ten == "tao_phieu":
        loai = "thu" if args.get("loai") == "thu" else "chi"
        nguoi = env["nhan_vien"].search([], limit=1)
        if not nguoi:
            return {"loi": "Chua co nhan vien. Vao Quan ly Nhan su tao nhan vien truoc."}
        phieu = env["tai_chinh.phieu_thu_chi"].create({
            "loai_phieu": loai, "nguon_goc": "khac",
            "ten_noi_dung": args.get("noi_dung", "(khong co noi dung)"),
            "so_tien": args.get("so_tien", 0), "nguoi_lap_id": nguoi.id})
        return {"ma_phieu": phieu.ma_phieu, "ket_qua": "Da tao phieu %s o trang thai Nhap" % loai}
    return {"loi": "Ham khong ho tro: %s" % ten}


def chat_agent(env, cau_hoi):
    messages = [{"role": "system", "content": HE_THONG},
                {"role": "user", "content": cau_hoi or ""}]
    try:
        for _ in range(5):
            data = goi_ai(env, messages, tools=TOOLS)
            msg = data["choices"][0]["message"]
            tcs = msg.get("tool_calls")
            if not tcs:
                return msg.get("content") or "(AI khong tra loi)"
            messages.append(msg)
            for tc in tcs:
                name = tc.get("function", {}).get("name")
                try:
                    args = json.loads(tc.get("function", {}).get("arguments") or "{}")
                except Exception:
                    args = {}
                kq = _thuc_thi(env, name, args)
                messages.append({"role": "tool", "tool_call_id": tc.get("id"),
                                 "content": json.dumps(kq, ensure_ascii=False)})
        return "AI da xu ly nhieu buoc. Thu hoi lai ro hon nhe."
    except Exception as e:
        _logger.error("AI Agent loi (fallback chat thuong): %s", e)
        try:
            return hoi_text(env, HE_THONG + "\n\nCau hoi: " + (cau_hoi or ""))
        except Exception:
            return "Loi khi goi AI: %s" % str(e)
