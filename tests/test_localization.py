import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.localization import t_type, t_domain, t_taxonomy

def test_localization_layer():
    """Verify localization mapping works as expected."""
    # Types
    assert t_type("phenomenon") == "Hiện tượng hành vi"
    assert t_type("law") == "Quy luật"
    assert t_type("anti-pattern") == "Mẫu hành vi cần tránh"
    
    # Domains
    assert t_domain("tu-than") == "Tự Thân"
    assert t_domain("cognitive-science") == "Khoa học nhận thức & Kiến tạo ý nghĩa"
    
    # Taxonomy
    assert t_taxonomy("Philosophy Lens") == "Lăng kính triết học"
    
    # Fallback to original
    assert t_type("Unknown Type") == "Unknown Type"
