# -*- coding: utf-8 -*-
"""AI Agent toan quyen: tra cuu / tao / sua / xoa / goi method tren moi model (OpenAI tool calls)."""
import logging
import json
from .ai_client import goi_ai, hoi_text

_logger = logging.getLogger(__name__)

HE_THONG = (
    "Ban la AI Agent quan tri phan mem Quan ly Tai san va Tai chinh (cong ty kinh doanh "
    "linh kien dien tu may tinh) tren nen Odoo. Ban CO TOAN QUYEN: tra cuu, tao, cap nhat, "
    "xoa va goi method tren MOI model qua cac ham: tra_cuu, tao, cap_nhat, goi_method, xoa.\n\n"
    "CAC MODEL & FIELD CHINH:\n"
    "- tai_san: ten_tai_san, ma_vach, danh_muc_loai_tai_san_id, so_luong, gia_tri_tai_san, "
    "trang_thai (dang_su_dung/bao_tri/hong/mat/da_thanh_ly), ngay_mua, thoi_gian_su_dung, vi_tri\n"
    "- danh_muc_loai_tai_san: ma_loai_tai_san, ten_loai_tai_san, nhom_tai_san_id (Char), thoi_gian_khau_hao\n"
    "- nha_cung_cap: ma_nha_cung_cap, ten_nha_cung_cap, so_dien_thoai, email\n"
    "- nhan_vien: ma_dinh_danh, ho_ten_dem, ten, ngay_sinh (YYYY-MM-DD, PHAI tren 18 tuoi), "
    "email, so_dien_thoai, phong_ban_id, chuc_vu_id\n"
    "- phong_ban: ma_phong_ban, ten_phong_ban ; chuc_vu: ma_chuc_vu, ten_chuc_vu\n"
    "- tai_chinh.phieu_thu_chi: loai_phieu (thu/chi), nguon_goc (bao_tri/mua_sam/thanh_ly/luong/khac), "
    "ten_noi_dung, so_tien, ngay_lap, nguoi_lap_id, trang_thai (nhap/cho_duyet/da_duyet/huy). "
    "Method: action_gui_duyet, action_duyet, action_huy\n"
    "- bao_tri: tai_san_id, ngay_bao_tri, noi_dung_bao_tri, chi_phi_bao_tri, nha_cung_cap_id, "
    "tinh_trang. Method: action_bat_dau_bao_tri, action_hoan_thanh, action_huy\n"
    "- thanh_ly: tai_san_id, nguoi_lap_id, ngay_thanh_ly, ly_do, trang_thai. Method: action_duyet, action_huy\n\n"
    "QUY TAC:\n"
    "- domain la mang, vd [[\"trang_thai\",\"=\",\"nhap\"]]. Rong [] la lay tat ca.\n"
    "- Truoc khi tao ban ghi co Many2one (vd nhan_vien can phong_ban_id, chuc_vu_id), "
    "hay tra_cuu de lay id truoc; neu chua co thi tao moi.\n"
    "- De DUYET phieu: goi_method action_gui_duyet roi action_duyet (phieu phai o trang thai nhap).\n"
    "- Khi tao nhieu ban ghi ngau nhien, tu nghi thong tin hop ly (ten Viet, so tien hop ly).\n"
    "- Tra loi tieng Viet co dau, ngan gon. Sau khi lam xong hay xac nhan ket qua (ma/ten ban ghi)."
)

TOOLS = [
    {"type": "function", "function": {
        "name": "tra_cuu",
        "description": "Tra cuu (search_read) ban ghi cua bat ky model. Tra ve danh sach.",
        "parameters": {"type": "object", "properties": {
            "model": {"type": "string"},
            "domain": {"type": "array", "items": {}},
            "fields": {"type": "array", "items": {"type": "string"}},
            "limit": {"type": "integer"}}, "required": ["model"]}}},
    {"type": "function", "function": {
        "name": "tao",
        "description": "Tao ban ghi moi cho model bat ky. values la dict gia tri field.",
        "parameters": {"type": "object", "properties": {
            "model": {"type": "string"},
            "values": {"type": "object"}}, "required": ["model", "values"]}}},
    {"type": "function", "function": {
        "name": "cap_nhat",
        "description": "Cap nhat (write) cac ban ghi khop domain cho model bat ky.",
        "parameters": {"type": "object", "properties": {
            "model": {"type": "string"},
            "domain": {"type": "array", "items": {}},
            "values": {"type": "object"}}, "required": ["model", "domain", "values"]}}},
    {"type": "function", "function": {
        "name": "goi_method",
        "description": "Goi method (vd action_duyet, action_hoan_thanh) tren cac ban ghi khop domain.",
        "parameters": {"type": "object", "properties": {
            "model": {"type": "string"},
            "domain": {"type": "array", "items": {}},
            "method": {"type": "string"}}, "required": ["model", "domain", "method"]}}},
    {"type": "function", "function": {
        "name": "xoa",
        "description": "Xoa (unlink) cac ban ghi khop domain. Can than, khong hoan tac duoc.",
        "parameters": {"type": "object", "properties": {
            "model": {"type": "string"},
            "domain": {"type": "array", "items": {}}}, "required": ["model", "domain"]}}},
]


def _thuc_thi(env, ten, args):
    args = args or {}
    try:
        if ten == "tra_cuu":
            model = args["model"]
            domain = args.get("domain") or []
            fields = args.get("fields")
            limit = args.get("limit") or 30
            recs = env[model].search(domain, limit=limit)
            if fields:
                return {"ket_qua": recs.read(fields)}
            return {"so_luong": len(recs),
                    "ket_qua": [{"id": r.id, "ten": r.display_name} for r in recs]}
        if ten == "tao":
            rec = env[args["model"]].create(args["values"])
            return {"id": rec.id, "ten": rec.display_name}
        if ten == "cap_nhat":
            recs = env[args["model"]].search(args.get("domain") or [])
            recs.write(args["values"])
            return {"so_ban_ghi_cap_nhat": len(recs)}
        if ten == "goi_method":
            recs = env[args["model"]].search(args.get("domain") or [])
            getattr(recs, args["method"])()
            return {"ket_qua": "Da goi %s tren %d ban ghi" % (args["method"], len(recs))}
        if ten == "xoa":
            recs = env[args["model"]].search(args.get("domain") or [])
            n = len(recs)
            recs.unlink()
            return {"so_ban_ghi_xoa": n}
    except Exception as e:
        return {"loi": str(e)}
    return {"loi": "Ham khong ho tro: %s" % ten}


def chat_agent(env, cau_hoi):
    messages = [{"role": "system", "content": HE_THONG},
                {"role": "user", "content": cau_hoi or ""}]
    try:
        for _ in range(8):
            data = goi_ai(env, messages, tools=TOOLS)
            msg = data["choices"][0]["message"]
            tcs = msg.get("tool_calls")
            if not tcs:
                return msg.get("content") or "(AI khong tra loi)"
            messages.append(msg)
            for tc in tcs:
                name = tc.get("function", {}).get("name")
                try:
                    a = json.loads(tc.get("function", {}).get("arguments") or "{}")
                except Exception:
                    a = {}
                kq = _thuc_thi(env, name, a)
                messages.append({"role": "tool", "tool_call_id": tc.get("id"),
                                 "content": json.dumps(kq, ensure_ascii=False)})
        return "AI da xu ly nhieu buoc. Thu hoi lai ro hon nhe."
    except Exception as e:
        _logger.error("AI Agent loi (fallback): %s", e)
        try:
            return hoi_text(env, HE_THONG + "\n\nCau hoi: " + (cau_hoi or ""))
        except Exception:
            return "Loi khi goi AI: %s" % str(e)
