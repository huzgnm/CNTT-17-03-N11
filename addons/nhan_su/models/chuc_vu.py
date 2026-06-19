from odoo import models, fields  # Import các module models và fields từ Odoo

class ChucVu(models.Model):  # Định nghĩa một model mới có tên là ChucVu, kế thừa từ models.Model
    _name = 'chuc_vu'  # Định danh (tên kỹ thuật) của model, dùng để lưu vào database
    _description = 'Bảng chứa thông tin chức vụ'  # Mô tả về model (hiển thị trong giao diện quản trị)
    _rec_name = "ten_chuc_vu"  # Xác định trường được hiển thị đại diện khi tham chiếu đến model này

    ma_chuc_vu = fields.Char("Mã chức vụ", required=True)  # Trường kiểu chuỗi (Char), bắt buộc nhập
    ten_chuc_vu = fields.Char("Tên chức vụ", required=True)  # Trường kiểu chuỗi (Char), bắt buộc nhập

