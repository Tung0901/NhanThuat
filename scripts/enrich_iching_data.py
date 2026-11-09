"""
Enrich iching_64_hexagrams.json with mathematically rigorous I Ching structures:
- Trigrams, Binary Patterns (6 lines: 1..6)
- Nuclear (Hỗ), Opposite (Thác), Inverted (Tung)
- 12 Sovereign Hexagrams (Thập Nhị Tức Quái)
- 6 Lines (Lục Hào) with Line names, Yin/Yang type, Org Roles and Action Advice
- Strategic Stance (Tiến, Thoái, Thủ, Biến)
- Diagnostic Tags & Knowledge Unit Links
"""

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

DATA_FILE = Path(__file__).resolve().parent.parent / "backend" / "app" / "engine" / "philosophies" / "iching_64_hexagrams.json"

TRIGRAMS = {
    "Càn": {"name": "Càn", "symbol": "☰", "nature": "Thiên", "element": "Kim", "pattern": "111"},
    "Đoài": {"name": "Đoài", "symbol": "☱", "nature": "Trạch", "element": "Kim", "pattern": "110"},
    "Ly": {"name": "Ly", "symbol": "☲", "nature": "Hỏa", "element": "Hỏa", "pattern": "101"},
    "Chấn": {"name": "Chấn", "symbol": "☳", "nature": "Lôi", "element": "Mộc", "pattern": "100"},
    "Tốn": {"name": "Tốn", "symbol": "☴", "nature": "Phong", "element": "Mộc", "pattern": "011"},
    "Khảm": {"name": "Khảm", "symbol": "☵", "nature": "Thủy", "element": "Thủy", "pattern": "010"},
    "Cấn": {"name": "Cấn", "symbol": "☶", "nature": "Sơn", "element": "Thổ", "pattern": "001"},
    "Khôn": {"name": "Khôn", "symbol": "☷", "nature": "Địa", "element": "Thổ", "pattern": "000"},
}

HEXAGRAM_TRIGRAM_PAIRS = [
    ("Càn", "Càn"),      # 1
    ("Khôn", "Khôn"),    # 2
    ("Khảm", "Chấn"),    # 3
    ("Cấn", "Khảm"),     # 4
    ("Khảm", "Càn"),     # 5
    ("Càn", "Khảm"),     # 6
    ("Khôn", "Khảm"),    # 7
    ("Khảm", "Khôn"),    # 8
    ("Tốn", "Càn"),      # 9
    ("Càn", "Đoài"),     # 10
    ("Khôn", "Càn"),     # 11
    ("Càn", "Khôn"),     # 12
    ("Càn", "Ly"),       # 13
    ("Ly", "Càn"),       # 14
    ("Khôn", "Cấn"),     # 15
    ("Chấn", "Khôn"),    # 16
    ("Đoài", "Chấn"),    # 17
    ("Cấn", "Tốn"),      # 18
    ("Khôn", "Đoài"),    # 19
    ("Tốn", "Khôn"),     # 20
    ("Ly", "Chấn"),      # 21
    ("Cấn", "Ly"),       # 22
    ("Cấn", "Khôn"),     # 23
    ("Khôn", "Chấn"),    # 24
    ("Càn", "Chấn"),     # 25
    ("Cấn", "Càn"),      # 26
    ("Cấn", "Chấn"),     # 27
    ("Đoài", "Tốn"),     # 28
    ("Khảm", "Khảm"),    # 29
    ("Ly", "Ly"),        # 30
    ("Đoài", "Cấn"),     # 31
    ("Chấn", "Tốn"),     # 32
    ("Càn", "Cấn"),      # 33
    ("Chấn", "Càn"),     # 34
    ("Ly", "Khôn"),      # 35
    ("Khôn", "Ly"),      # 36
    ("Tốn", "Ly"),       # 37
    ("Ly", "Đoài"),      # 38
    ("Khảm", "Cấn"),     # 39
    ("Chấn", "Khảm"),    # 40
    ("Cấn", "Đoài"),     # 41
    ("Tốn", "Chấn"),     # 42
    ("Đoài", "Càn"),     # 43
    ("Càn", "Tốn"),      # 44
    ("Đoài", "Khôn"),    # 45
    ("Khôn", "Tốn"),     # 46
    ("Đoài", "Khảm"),    # 47
    ("Khảm", "Tốn"),     # 48
    ("Đoài", "Ly"),      # 49
    ("Ly", "Tốn"),       # 50
    ("Chấn", "Chấn"),    # 51
    ("Cấn", "Cấn"),      # 52
    ("Tốn", "Cấn"),      # 53
    ("Chấn", "Đoài"),    # 54
    ("Chấn", "Ly"),      # 55
    ("Ly", "Cấn"),       # 56
    ("Tốn", "Tốn"),      # 57
    ("Đoài", "Đoài"),    # 58
    ("Tốn", "Khảm"),     # 59
    ("Khảm", "Đoài"),    # 60
    ("Tốn", "Đoài"),     # 61
    ("Chấn", "Cấn"),     # 62
    ("Khảm", "Ly"),      # 63
    ("Ly", "Khảm"),      # 64
]

SOVEREIGN_HEXAGRAMS_MAP = {
    24: {"order": 1, "phase": "Chớm phục hồi", "ratio": "1 Dương - 5 Âm"},
    19: {"order": 2, "phase": "Đà tăng trưởng", "ratio": "2 Dương - 4 Âm"},
    11: {"order": 3, "phase": "Hưng thịnh cân bằng", "ratio": "3 Dương - 3 Âm"},
    34: {"order": 4, "phase": "Khí thế dâng cao", "ratio": "4 Dương - 2 Âm"},
    43: {"order": 5, "phase": "Quyết liệt làm sạch", "ratio": "5 Dương - 1 Âm"},
    1:  {"order": 6, "phase": "Đỉnh cao cực thịnh", "ratio": "6 Dương - 0 Âm"},
    44: {"order": 7, "phase": "Mầm họa manh nha", "ratio": "5 Dương - 1 Âm"},
    33: {"order": 8, "phase": "Rút lui bảo toàn", "ratio": "4 Dương - 2 Âm"},
    12: {"order": 9, "phase": "Bế tắc giao tiếp", "ratio": "3 Dương - 3 Âm"},
    20: {"order": 10, "phase": "Quan sát tĩnh lặng", "ratio": "2 Dương - 4 Âm"},
    23: {"order": 11, "phase": "Bào mòn nền tảng", "ratio": "1 Dương - 5 Âm"},
    2:  {"order": 12, "phase": "Tĩnh lặng tích lũy", "ratio": "0 Dương - 6 Âm"},
}

STRATEGIC_STANCES = {
    # 1..64 classifications
    1: "Tiến", 2: "Thủ", 3: "Biến", 4: "Thủ", 5: "Thủ", 6: "Biến", 7: "Tiến", 8: "Tiến",
    9: "Thủ", 10: "Thủ", 11: "Tiến", 12: "Thoái", 13: "Tiến", 14: "Tiến", 15: "Thủ", 16: "Tiến",
    17: "Biến", 18: "Biến", 19: "Tiến", 20: "Thủ", 21: "Biến", 22: "Thủ", 23: "Thoái", 24: "Tiến",
    25: "Thủ", 26: "Thủ", 27: "Thủ", 28: "Biến", 29: "Thoái", 30: "Tiến", 31: "Tiến", 32: "Thủ",
    33: "Thoái", 34: "Tiến", 35: "Tiến", 36: "Thoái", 37: "Thủ", 38: "Biến", 39: "Thoái", 40: "Biến",
    41: "Thoái", 42: "Tiến", 43: "Tiến", 44: "Biến", 45: "Tiến", 46: "Tiến", 47: "Thoái", 48: "Thủ",
    49: "Biến", 50: "Biến", 51: "Biến", 52: "Thủ", 53: "Tiến", 54: "Thoái", 55: "Tiến", 56: "Thoái",
    57: "Biến", 58: "Tiến", 59: "Biến", 60: "Thủ", 61: "Thủ", 62: "Thoái", 63: "Thủ", 64: "Biến"
}

DIAGNOSTIC_TAGS_MAP = {
    1: ["lãnh_đạo", "bành_trướng", "ngạo_mạn", "đỉnh_cao"],
    2: ["hậu_cần", "phò_tá", "dung_chứa", "nền_tảng"],
    3: ["khởi_nghiệp_sơ_khai", "hỗn_loạn", "xây_dựng_đội_ngũ"],
    4: ["đội_ngũ_non_trẻ", "đào_tạo", "thiếu_kỹ_năng"],
    5: ["chờ_thời", "tích_lũy_vốn", "kiên_nhẫn"],
    6: ["tranh_chấp_hợp_đồng", "bất_đồng_cổ_đông", "xung_đột"],
    7: ["kỷ_luật_thời_chiến", "quản_trị_khủng_hoảng", "tập_hợp_lực_lượng"],
    8: ["liên_minh_chiến_lược", "M&A", "hợp_tác_chia_sẻ"],
    9: ["nguồn_lực_giới_hạn", "tích_lũy_nhỏ", "bước_đệm"],
    10: ["khách_hàng_vip", "đối_tác_độc_quyền", "thận_trọng"],
    11: ["tăng_trưởng_thuận_lợi", "gắn_kết_nội_bộ", "hưng_thịnh"],
    12: ["dòng_tiền_nghẽn", "thị_trường_đóng_băng", "bế_tắc_nội_bộ"],
    13: ["văn_hóa_đồng_thuận", "sứ_mệnh_chung", "tập_hợp_nhân_tài"],
    14: ["vị_thế_độc_tôn", "thâu_tóm_thị_phần", "dồi_dào_vốn"],
    15: ["khiêm_tốn", "giữ_kín_tiếng", "bảo_vệ_nội_lực"],
    16: ["khích_lệ_tinh_thần", "truyền_cảm_hứng", "chuẩn_bị_ra_quân"],
    17: ["thích_ứng_thị_trường", "xoay_trục", "linh_hoạt"],
    18: ["sửa_chữa_sai_lầm", "tái_cấu_trúc_nội_bộ", "thanh_lọc"],
    19: ["tiếp_cận_hiện_trường", "mở_rộng_quy_mô", "đà_tăng_trưởng"],
    20: ["quan_sát_toàn_cục", "đánh_giá_nội_lực", "khảo_sát"],
    21: ["siết_chặt_pháp_chế", "xử_lý_sai_phạm", "thực_thi_kỷ_luật"],
    22: ["xây_dựng_thương_hiệu", "trang_hoàng_bề_nổi", "tinh_chỉnh"],
    23: ["thị_phần_bào_mòn", "rò_rỉ_nhân_sự", "nguy_cơ_sụp_đổ"],
    24: ["tín_hiệu_phục_hồi", "thử_nghiệm_mới", "mầm_sống"],
    25: ["tuân_thủ_quy_luật", "tránh_manh_động", "chân_thực"],
    26: ["tích_lũy_chất_xám", "nguồn_lực_hùng_hậu", "giữ_vững_thế"],
    27: ["quản_trị_dinh_dưỡng_tổ_chức", "chính_sách_đãi_ngộ", "nhân_sự"],
    28: ["quá_tải_áp_lực", "cột_trụ_rạn_nứt", "cải_tổ_khẩn_cấp"],
    29: ["hiểm_nạn_kép", "dòng_tiền_cạn_kiệt", "giữ_vững_niềm_tin"],
    30: ["minh_bạch_hóa", "truyền_thông_rõ_ràng", "dựa_vào_hệ_thống"],
    31: ["thấu_cảm_khách_hàng", "kết_nối_cảm_xúc", "thu_hút_nhân_tâm"],
    32: ["duy_trì_tính_bền_vững", "hệ_thống_ổn_định", "cam_kết_dài_hạn"],
    33: ["chủ_động_rút_lui", "cắt_lỗ_kịp_thời", "bảo_toàn_vốn"],
    34: ["sức_mạnh_vượt_trội", "nguy_cơ_vượt_rào", "kiềm_chế_quyền_lực"],
    35: ["thăng_tiến_nhanh", "thời_cơ_tỏa_sáng", "được_cấp_trên_tin_cậy"],
    36: ["ẩn_mình_trong_nghịch_cảnh", "giấu_sáng_giữ_mình", "áp_lực_bức_hại"],
    37: ["kỷ_cương_gia_đình_tổ_chức", "đồng_lòng_hậu_phương", "nội_bộ_gắn_kết"],
    38: ["bất_đồng_quan_điểm", "chia_rẽ_nội_bộ", "tìm_điểm_chung_nhỏ"],
    39: ["bế_tắc_khó_khăn", "dừng_lại_tìm_cố_vấn", "tránh_húc_đầu_vào_đá"],
    40: ["hóa_giải_nguy_cơ", "khoan_thư_sức_dân", "tha_thứ_lỗi_nhỏ"],
    41: ["cắt_giảm_chi_phí", "tối_ưu_tinh_gọn", "hy_sinh_ngắn_hạn"],
    42: ["mở_rộng_đầu_tư", "gia_tăng_phúc_lợi", "thừa_thắng_xông_lên"],
    43: ["thanh_lọc_triệt_để", "cắt_bỏ_u_nhọt", "công_bố_sự_thật"],
    44: ["mầm_họa_manh_nha", "lỗ_hổng_kỷ_luật", "chặn_đứng_từ_đầu"],
    45: ["tụ_họp_quần_chúng", "huy_động_vốn_cộng_đồng", "gắn_kết"],
    46: ["thăng_tiến_bền_bỉ", "từng_bước_đi_lên", "tích_tiểu_thành_đại"],
    47: ["kiệt_quệ_tài_chính", "bị_cô_lập", "bản_lĩnh_thép"],
    48: ["giá_trị_cốt_lõi", "khai_thác_nội_lực", "nâng_cấp_giếng_nước"],
    49: ["cải_cách_toàn_diện", "xoay_trục_mô_hình", "thay_máu"],
    50: ["thể_chế_mới", "đổi_mới_sáng_tạo", "nấu_lại_nồi_cơm"],
    51: ["cú_sốc_bất_ngờ", "khủng_hoảng_đột_ngột", "giữ_vững_tâm_thế"],
    52: ["dừng_lại_tĩnh_tâm", "thiền_định_chiến_lược", "định_tâm"],
    53: ["tiến_từ_từ_chắc_chắn", "kết_hôn_chiến_lược", "quy_trình_chuẩn"],
    54: ["vào_sai_thế", "hợp_tác_bất_lợi", "chấp_nhận_thực_tế"],
    55: ["đỉnh_cao_thịnh_vượng", "chuẩn_bị_cho_suy_thoái", "quyết_đoán"],
    56: ["mở_rộng_thị_trường_xa", "thích_nghi_xứ_người", "khiêm_cung"],
    57: ["truyền_thông_thẩm_thấu", "mệnh_lệnh_sâu_rộng", "mềm_mỏng"],
    58: ["thuyết_phục_vui_vẻ", "đàm_phán_thương_lượng", "truyền_cảm_hứng"],
    59: ["giải_tỏa_ách_tắc", "hòa_tan_mâu_thuẫn", "kết_nối_lại"],
    60: ["thiết_lập_hạn_mức", "tiết_chế_chi_tiêu", "ranh_giới_rõ_ràng"],
    61: ["chân_thành_tuyệt_đối", "chữ_tín_thương_hiệu", "thấu_suốt"],
    62: ["chi_tiết_nhỏ_quan_trọng", "thận_trọng_từng_ly", "không_liều_lĩnh"],
    63: ["đã_hoàn_thành_mục_tiêu", "đề_phòng_lơ_là", "giữ_thành_quả"],
    64: ["chưa_kết_thúc", "chuẩn_bị_chu_kỳ_mới", "thận_trọng_chặng_cuối"]
}

RELATED_KNOWLEDGE_MAP = {
    1: ["NT-LAW-0001", "NT-ANTI-PATTERN-0016", "NT-PRINCIPLE-0004"],
    2: ["NT-PRINCIPLE-0001", "NT-LAW-0007", "NT-MODEL-0001"],
    3: ["NT-STRATEGY-0001", "NT-ANTI-PATTERN-0027", "NT-LAW-0004"],
    4: ["NT-LAW-0007", "NT-PRINCIPLE-0004", "NT-ANTI-PATTERN-0001"],
    5: ["NT-STRATEGY-0001", "NT-LAW-0001"],
    6: ["NT-LAW-0004", "NT-ANTI-PATTERN-0001"],
    7: ["NT-LAW-0007", "NT-STRATEGY-0001"],
    8: ["NT-PRINCIPLE-0001", "NT-LAW-0004"],
    9: ["NT-STRATEGY-0001", "NT-LAW-0007"],
    10: ["NT-LAW-0004", "NT-ANTI-PATTERN-0016"],
    11: ["NT-PRINCIPLE-0001", "NT-LAW-0001"],
    12: ["NT-ANTI-PATTERN-0001", "NT-LAW-0004"],
    13: ["NT-PRINCIPLE-0001", "NT-LAW-0004"],
    14: ["NT-LAW-0001", "NT-ANTI-PATTERN-0016"],
    15: ["NT-LAW-0004", "NT-PRINCIPLE-0001"],
    16: ["NT-PRINCIPLE-0004", "NT-LAW-0001"],
    17: ["NT-LAW-0004", "NT-STRATEGY-0001"],
    18: ["NT-ANTI-PATTERN-0001", "NT-LAW-0007"],
    19: ["NT-LAW-0001", "NT-PRINCIPLE-0004"],
    20: ["NT-LAW-0004", "NT-PRINCIPLE-0001"],
    21: ["NT-LAW-0007", "NT-ANTI-PATTERN-0001"],
    22: ["NT-LAW-0004", "NT-ANTI-PATTERN-0016"],
    23: ["NT-ANTI-PATTERN-0001", "NT-LAW-0007"],
    24: ["NT-LAW-0001", "NT-STRATEGY-0001"],
    25: ["NT-LAW-0001", "NT-ANTI-PATTERN-0016"],
    26: ["NT-STRATEGY-0001", "NT-LAW-0007"],
    27: ["NT-LAW-0007", "NT-PRINCIPLE-0004"],
    28: ["NT-ANTI-PATTERN-0027", "NT-LAW-0007"],
    29: ["NT-STRATEGY-0001", "NT-ANTI-PATTERN-0001"],
    30: ["NT-PRINCIPLE-0001", "NT-LAW-0004"],
    31: ["NT-PRINCIPLE-0001", "NT-LAW-0004"],
    32: ["NT-LAW-0007", "NT-PRINCIPLE-0004"],
    33: ["NT-STRATEGY-0001", "NT-LAW-0001"],
    34: ["NT-ANTI-PATTERN-0016", "NT-LAW-0007"],
    35: ["NT-LAW-0001", "NT-PRINCIPLE-0004"],
    36: ["NT-STRATEGY-0001", "NT-LAW-0004"],
    37: ["NT-PRINCIPLE-0001", "NT-LAW-0007"],
    38: ["NT-ANTI-PATTERN-0001", "NT-LAW-0004"],
    39: ["NT-STRATEGY-0001", "NT-LAW-0004"],
    40: ["NT-LAW-0001", "NT-PRINCIPLE-0004"],
    41: ["NT-STRATEGY-0001", "NT-LAW-0007"],
    42: ["NT-PRINCIPLE-0004", "NT-LAW-0001"],
    43: ["NT-ANTI-PATTERN-0001", "NT-LAW-0007"],
    44: ["NT-ANTI-PATTERN-0016", "NT-LAW-0004"],
    45: ["NT-PRINCIPLE-0001", "NT-LAW-0004"],
    46: ["NT-LAW-0001", "NT-PRINCIPLE-0004"],
    47: ["NT-STRATEGY-0001", "NT-ANTI-PATTERN-0001"],
    48: ["NT-LAW-0007", "NT-PRINCIPLE-0001"],
    49: ["NT-LAW-0007", "NT-ANTI-PATTERN-0027"],
    50: ["NT-LAW-0001", "NT-PRINCIPLE-0004"],
    51: ["NT-ANTI-PATTERN-0027", "NT-LAW-0001"],
    52: ["NT-STRATEGY-0001", "NT-LAW-0004"],
    53: ["NT-LAW-0001", "NT-PRINCIPLE-0004"],
    54: ["NT-LAW-0004", "NT-ANTI-PATTERN-0016"],
    55: ["NT-LAW-0001", "NT-ANTI-PATTERN-0016"],
    56: ["NT-LAW-0004", "NT-STRATEGY-0001"],
    57: ["NT-PRINCIPLE-0004", "NT-LAW-0004"],
    58: ["NT-PRINCIPLE-0001", "NT-LAW-0004"],
    59: ["NT-LAW-0001", "NT-PRINCIPLE-0004"],
    60: ["NT-LAW-0007", "NT-STRATEGY-0001"],
    61: ["NT-PRINCIPLE-0001", "NT-LAW-0004"],
    62: ["NT-LAW-0007", "NT-STRATEGY-0001"],
    63: ["NT-LAW-0001", "NT-ANTI-PATTERN-0016"],
    64: ["NT-LAW-0001", "NT-STRATEGY-0001"]
}

def generate_lines_detail(num, name, pattern, action_script):
    """Generate 6 lines data with organizational role and action."""
    lines = []
    role_titles = [
        "Tuyến đầu & Nhân sự thừa hành (Sơ khởi)",
        "Quản lý cấp trung & Trưởng nhóm (Cân bằng)",
        "Giám đốc chức năng & Trọng trách then chốt (Áp lực)",
        "Ban cố vấn & Phó tướng sát cánh (Cận quân)",
        "Người đứng đầu & CEO định đoạt (Chính vị)",
        "Cố vấn tối cao / Chuyển pha sau đỉnh (Thoái trào)"
    ]
    
    # Specific nuanced actions for famous hexagrams
    if num == 1: # Thuần Càn
        actions = [
            "Tiềm long vật dụng: Giữ mình, tích lũy năng lực ngầm, tuyệt đối không manh động.",
            "Hiện long tại điền: Tích cực thể hiện phẩm chất, tìm kiếm lãnh đạo minh triết.",
            "Quân tử chung nhật càn càn: Ngày đêm tự sửa mình, cảnh giác bẫy tự mãn.",
            "Hoặc dược tại uyên: Đứng trước ngã rẽ bước ngoặt, chủ động chuẩn bị Plan B.",
            "Phi long tại thiên: Đạt đỉnh cao quyền lực, dùng Đức trị và phân quyền thể chế.",
            "Kháng long hữu hối: Lên quá cao kiêu ngạo tất bại; chủ động lùi về hậu phương."
        ]
    elif num == 2: # Thuần Khôn
        actions = [
            "Lý sương kiên băng chí: Thấy sương rơi biết băng dày sắp đến; nhận biết rủi ro sớm.",
            "Trực phương đại: Giữ tâm chính trực, quy trình vuông vức, bao dung dung nạp cấp dưới.",
            "Hàm chương khả trinh: Giữ kín tài năng, phục vụ mục tiêu chung, chớ tranh công.",
            "Quát nang vô cữu: Thắt túi kín miệng, giữ gìn bảo mật cơ mật chiến lược.",
            "Hoàng thường nguyên cát: Khiêm nhu ôn hòa trong vai trò vận hành hậu cần cốt cán.",
            "Long chiến vu dã: Tránh tranh đoạt quyền lực với người đứng đầu dẫn đến tổn thương cả hai."
        ]
    else:
        # Template based on yin/yang line
        actions = []
        for i, bit in enumerate(pattern):
            line_no = i + 1
            if bit == "1":
                if line_no in (1, 2):
                    actions.append(f"Chủ động dấn thân, giữ vững định hướng ban đầu của {name}.")
                elif line_no in (3, 4):
                    actions.append("Gia tăng kỷ luật, chịu đựng áp lực điều phối tại mắt xích này.")
                elif line_no == 5:
                    actions.append("Quyết đoán chỉ đạo, xác lập uy quyền và định hình luật chơi rõ ràng.")
                else:
                    actions.append("Cương nhu đúng lúc, tránh bảo thủ khi thời thế sắp chuyển pha.")
            else:
                if line_no in (1, 2):
                    actions.append("Thuận tòng quy trình, lắng nghe phản hồi thực tế từ tuyến đầu.")
                elif line_no in (3, 4):
                    actions.append("Khéo léo hóa giải mâu thuẫn, giữ vai trò dung hòa giữa các phe phái.")
                elif line_no == 5:
                    actions.append("Khiêm nhường lắng nghe, ủy quyền cho các chuyên gia thực chiến.")
                else:
                    actions.append("Mềm mỏng buông bỏ những thứ không còn giá trị, chuẩn bị đón thời cơ mới.")

    for i, bit in enumerate(pattern):
        line_num = i + 1
        is_yang = bit == "1"
        line_name = ""
        if line_num == 1:
            line_name = "Sơ Cửu" if is_yang else "Sơ Lục"
        elif line_num == 2:
            line_name = "Cửu Nhị" if is_yang else "Lục Nhị"
        elif line_num == 3:
            line_name = "Cửu Tam" if is_yang else "Lục Tam"
        elif line_num == 4:
            line_name = "Cửu Tứ" if is_yang else "Lục Tứ"
        elif line_num == 5:
            line_name = "Cửu Ngũ" if is_yang else "Lục Ngũ"
        elif line_num == 6:
            line_name = "Thượng Cửu" if is_yang else "Thượng Lục"

        lines.append({
            "line": line_num,
            "name": line_name,
            "type": "yang" if is_yang else "yin",
            "symbol": "───" if is_yang else "-- --",
            "org_role": role_titles[i],
            "action": actions[i]
        })
    return lines

def main():
    if not DATA_FILE.exists():
        print(f"File not found: {DATA_FILE}")
        return

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    hex_list = data.get("hexagrams", [])
    print(f"Loaded {len(hex_list)} hexagrams.")

    # 1. First pass: compute binary pattern for all 64 hexagrams
    pattern_to_number = {}
    for i, h in enumerate(hex_list):
        num = int(h["number"])
        upper_name, lower_name = HEXAGRAM_TRIGRAM_PAIRS[num - 1]
        upper_trig = TRIGRAMS[upper_name]
        lower_trig = TRIGRAMS[lower_name]
        # Pattern from bottom line 1 to top line 6: lower trigram (1..3) + upper trigram (4..6)
        binary_pattern = lower_trig["pattern"] + upper_trig["pattern"]
        pattern_to_number[binary_pattern] = num

    print(f"Computed binary patterns for {len(pattern_to_number)} unique hexagrams.")
    assert len(pattern_to_number) == 64, f"Expected 64 unique patterns, got {len(pattern_to_number)}"

    # 2. Second pass: enrich each hexagram
    enriched_hexagrams = []
    for h in hex_list:
        num = int(h["number"])
        upper_name, lower_name = HEXAGRAM_TRIGRAM_PAIRS[num - 1]
        upper_trig = TRIGRAMS[upper_name]
        lower_trig = TRIGRAMS[lower_name]
        pattern = lower_trig["pattern"] + upper_trig["pattern"]

        # Nuclear hexagram (Hỗ quái): lines 2, 3, 4 as lower; lines 3, 4, 5 as upper
        # pattern index 0=line1, 1=line2, 2=line3, 3=line4, 4=line5, 5=line6
        nuclear_pattern = pattern[1] + pattern[2] + pattern[3] + pattern[2] + pattern[3] + pattern[4]
        nuclear_num = pattern_to_number.get(nuclear_pattern, num)

        # Opposite hexagram (Thác quái): flip all bits
        opposite_pattern = "".join("1" if b == "0" else "0" for b in pattern)
        opposite_num = pattern_to_number.get(opposite_pattern, num)

        # Inverted hexagram (Tung quái): reverse lines 1..6
        inverted_pattern = pattern[::-1]
        inverted_num = pattern_to_number.get(inverted_pattern, num)

        # Twelve Sovereign
        sovereign_info = SOVEREIGN_HEXAGRAMS_MAP.get(num)
        twelve_sovereign = {
            "is_sovereign": bool(sovereign_info),
            "phase_order": sovereign_info["order"] if sovereign_info else None,
            "phase_name": sovereign_info["phase"] if sovereign_info else None,
            "energy_ratio": sovereign_info["ratio"] if sovereign_info else None,
        }

        # Stance & tags
        stance = STRATEGIC_STANCES.get(num, "Biến")
        tags = DIAGNOSTIC_TAGS_MAP.get(num, ["quản_trị", "thời_thế"])
        related_units = RELATED_KNOWLEDGE_MAP.get(num, ["NT-LAW-0001", "NT-PRINCIPLE-0001"])

        # Lines detail
        lines_detail = generate_lines_detail(num, h["name"], pattern, h.get("action_script", ""))

        enriched_item = dict(h)
        enriched_item["element"] = upper_trig["element"]
        enriched_item["upper_trigram"] = {
            "name": upper_trig["name"],
            "symbol": upper_trig["symbol"],
            "nature": upper_trig["nature"],
            "element": upper_trig["element"],
            "pattern": upper_trig["pattern"],
        }
        enriched_item["lower_trigram"] = {
            "name": lower_trig["name"],
            "symbol": lower_trig["symbol"],
            "nature": lower_trig["nature"],
            "element": lower_trig["element"],
            "pattern": lower_trig["pattern"],
        }
        enriched_item["binary_pattern"] = pattern
        enriched_item["nuclear_hex_number"] = nuclear_num
        enriched_item["opposite_hex_number"] = opposite_num
        enriched_item["inverted_hex_number"] = inverted_num
        enriched_item["twelve_sovereign"] = twelve_sovereign
        enriched_item["six_lines"] = lines_detail
        enriched_item["strategic_stance"] = stance
        enriched_item["diagnostic_tags"] = tags
        enriched_item["related_knowledge_units"] = related_units

        enriched_hexagrams.append(enriched_item)

    data["hexagrams"] = enriched_hexagrams
    data["metadata"]["version"] = "2.0.0"
    data["metadata"]["description"] = "Ma trận cấu trúc hóa 64 Quẻ Kinh Dịch Quản Trị V2: Tọa độ Bát Cung 8x8, Chu kỳ 12 Tức Quái, Động lực chuyển pha Lục Hào, và liên kết Tri thức Điều hành."

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Successfully enriched {len(enriched_hexagrams)} hexagrams in {DATA_FILE}")

if __name__ == "__main__":
    main()
