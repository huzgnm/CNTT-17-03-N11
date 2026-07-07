# -*- coding: utf-8 -*-
import logging
from .ai_client import hoi_text

_logger = logging.getLogger(__name__)


def phan_tich_tai_san(env, bao_cao):
    """Tao prompt tu du lieu bao cao, goi AI, tra ve phan tich."""
    chi_tiet = []
    for ct in bao_cao.chi_tiet_ids:
        chi_tiet.append(
            "  - %s: %d tai san, nguyen gia %.0f VND, con lai %.0f VND (%.1f%%)" % (
                ct.danh_muc_loai_tai_san_id.ten_loai_tai_san if ct.danh_muc_loai_tai_san_id else "Khac",
                ct.so_tai_san, ct.tong_nguyen_gia, ct.tong_gia_tri_con_lai, ct.ty_le_con_lai,
            )
        )
    prompt = """Ban la chuyen gia quan ly tai san doanh nghiep tai Viet Nam.
Hay phan tich bao cao tai san duoi day va dua ra nhan xet, khuyen nghi bang tieng Viet co dau.

BAO CAO TAI SAN NAM %d:
- Tong so tai san: %d
- Tong nguyen gia: %s VND
- Tong da khau hao: %s VND
- Tong gia tri con lai: %s VND (%.1f%% nguyen gia)
- Chi phi bao tri trong nam: %s VND
- Thu tu thanh ly: %s VND

Chi tiet theo loai:
%s

Yeu cau:
1. Danh gia tong quan tinh trang tai san
2. Nhan xet muc do khau hao (tai san nao can thay the sap?)
3. Danh gia hieu qua chi phi bao tri
4. De xuat uu tien cho nam tiep theo

Tra loi ngan gon, ro rang, thuc te.""" % (
        bao_cao.nam_bao_cao, bao_cao.tong_tai_san,
        "{:,.0f}".format(bao_cao.tong_nguyen_gia),
        "{:,.0f}".format(bao_cao.tong_da_khau_hao),
        "{:,.0f}".format(bao_cao.tong_gia_tri_con_lai),
        (bao_cao.tong_gia_tri_con_lai / bao_cao.tong_nguyen_gia * 100) if bao_cao.tong_nguyen_gia else 0,
        "{:,.0f}".format(bao_cao.tong_chi_phi_bao_tri),
        "{:,.0f}".format(bao_cao.tong_thu_thanh_ly),
        "\n".join(chi_tiet) if chi_tiet else "  (Chua co du lieu chi tiet)",
    )
    return hoi_text(env, prompt)
