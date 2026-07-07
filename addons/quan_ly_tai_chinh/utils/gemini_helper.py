# -*- coding: utf-8 -*-
import logging
import requests

_logger = logging.getLogger(__name__)

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"


def ask_gemini(api_key: str, prompt: str) -> str:
    """
    Gui prompt den Gemini API va tra ve van ban phan tich.
    Cau hinh: Settings -> Technical -> System Parameters
      quan_ly_tai_chinh.gemini_api_key
    """
    url = "%s?key=%s" % (GEMINI_URL, api_key)
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": 1024,
        },
    }
    try:
        resp = requests.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        _logger.error("Gemini API loi: %s", str(e))
        raise


def phan_tich_tai_san(env, bao_cao) -> str:
    """
    Tao prompt tu du lieu bao cao, gui Gemini, tra ve phan tich.
    """
    ICP = env["ir.config_parameter"].sudo()
    api_key = ICP.get_param("quan_ly_tai_chinh.gemini_api_key", "")
    if not api_key:
        return "Chua cau hinh Gemini API key. Vao Settings > Technical > System Parameters, them khoa: quan_ly_tai_chinh.gemini_api_key"

    chi_tiet = []
    for ct in bao_cao.chi_tiet_ids:
        chi_tiet.append(
            "  - %s: %d tai san, nguyen gia %.0f VND, con lai %.0f VND (%.1f%%)"
            % (
                ct.danh_muc_loai_tai_san_id.ten_loai_tai_san if ct.danh_muc_loai_tai_san_id else "Khac",
                ct.so_tai_san,
                ct.tong_nguyen_gia,
                ct.tong_gia_tri_con_lai,
                ct.ty_le_con_lai,
            )
        )

    prompt = """Ban la chuyen gia quan ly tai san doanh nghiep tai Viet Nam.
Hay phan tich bao cao tai san duoi day va dua ra nhan xet, khuyen nghi bang tieng Viet.

BAO CAO TAI SAN NAM %d:
- Tong so tai san: %d
- Tong nguyen gia: %s VND
- Tong da khau hao: %s VND
- Tong gia tri con lai: %s VND (%.1f%% nguyen gia)
- Chi phi bao tri trong nam: %s VND
- Thu tu thanh ly: %s VND

Chi tiet theo loai:
%s

Yeu cau phan tich:
1. Danh gia tong quan tinh trang tai san
2. Nhan xet muc do khau hao (co tai san nao can thay the sap?)
3. Danh gia hieu qua chi phi bao tri
4. De xuat uu tien cho nam tiep theo (ngan sach bao tri, mua sam, thanh ly)

Tra loi ngan gon, ro rang, thuc te.""" % (
        bao_cao.nam_bao_cao,
        bao_cao.tong_tai_san,
        "{:,.0f}".format(bao_cao.tong_nguyen_gia),
        "{:,.0f}".format(bao_cao.tong_da_khau_hao),
        "{:,.0f}".format(bao_cao.tong_gia_tri_con_lai),
        (bao_cao.tong_gia_tri_con_lai / bao_cao.tong_nguyen_gia * 100) if bao_cao.tong_nguyen_gia else 0,
        "{:,.0f}".format(bao_cao.tong_chi_phi_bao_tri),
        "{:,.0f}".format(bao_cao.tong_thu_thanh_ly),
        "\n".join(chi_tiet) if chi_tiet else "  (Chua co du lieu chi tiet)",
    )

    return ask_gemini(api_key, prompt)
