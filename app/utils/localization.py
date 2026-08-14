"""Vietnamese Localization Layer for Nhan Thuat UI."""

def t_type(type_id: str) -> str:
    if not type_id:
        return type_id
    mapping = {
        "law": "Quy luật",
        "phenomenon": "Hiện tượng hành vi",
        "principle": "Nguyên lý",
        "model": "Mô hình",
        "anti-pattern": "Mẫu hành vi cần tránh",
        "all": "Tất cả"
    }
    return mapping.get(type_id.lower(), type_id)

def t_taxonomy(tax_id: str) -> str:
    if not tax_id:
        return tax_id
    mapping = {
        "philosophy lens": "Lăng kính triết học",
        "domain area": "Lĩnh vực ứng dụng",
        "category": "Tầng tri thức",
        "core human nature": "Bản chất con người",
        "behavioral science": "Khoa học hành vi",
        "applied management": "Quản trị ứng dụng",
    }
    return mapping.get(tax_id.lower(), tax_id)

def t_domain(domain_id: str) -> str:
    if not domain_id:
        return domain_id
    mapping = {
        "tu-than": "Tự Thân",
        "tri-nhan": "Trí Nhân",
        "dung-nhan": "Dùng Nhân",
        "hop-chung": "Hợp Chúng",
        "thanh-su": "Thành Sự",
        "cognitive-science": "Khoa học nhận thức & Kiến tạo ý nghĩa",
        "cognitive-science-sensemaking": "Khoa học nhận thức & Kiến tạo ý nghĩa",
        "human-nature": "Bản chất con người",
        "decision-making": "Ra quyết định",
        "leadership": "Lãnh đạo",
        "learning": "Học tập",
        "conflict": "Xung đột",
        "motivation": "Động lực",
        "personality": "Tính cách",
        "hiring": "Tuyển dụng",
        "team-building": "Xây dựng đội ngũ",
        "delegation": "Giao việc",
        "communication": "Giao tiếp",
        "incentives": "Động cơ & Phần thưởng",
        "trust": "Niềm tin",
        "negotiation": "Đàm phán",
        "authority": "Thẩm quyền",
        "influence": "Ảnh hưởng",
        "strategy": "Chiến lược",
        "execution": "Thực thi",
        "culture": "Văn hóa",
        "ethics": "Đạo đức",
        "all": "Tất cả"
    }
    return mapping.get(domain_id.lower(), domain_id.replace('-', ' ').title())

def t_domain_desc(domain_id: str) -> str:
    if not domain_id:
        return ""
    mapping = {
        "cognitive-science": "Nghiên cứu cách con người tiếp nhận thông tin, chú ý, ghi nhớ, hình thành mô hình tinh thần, sử dụng lối tắt tư duy và đánh giá chính suy nghĩ của mình.",
        "cognitive-science-sensemaking": "Nghiên cứu cách con người tiếp nhận thông tin, chú ý, ghi nhớ, hình thành mô hình tinh thần, sử dụng lối tắt tư duy và đánh giá chính suy nghĩ của mình.",
        "tu-than": "Nghiên cứu các cơ chế rèn luyện, kiểm soát nội tại và làm chủ bản thân của người lãnh đạo.",
        "tri-nhan": "Nghiên cứu cách thấu hiểu, đánh giá và nhận diện năng lực, bản chất của người khác.",
        "dung-nhan": "Nghiên cứu các mô hình, quy luật để bố trí, giao việc và tạo động lực cho nhân sự.",
        "hop-chung": "Nghiên cứu cơ chế vận hành đội ngũ, xây dựng văn hóa và gắn kết tập thể.",
        "thanh-su": "Nghiên cứu các chiến lược ra quyết định, thực thi và quản trị rủi ro để đạt mục tiêu."
    }
    return mapping.get(domain_id.lower(), "Nghiên cứu và ứng dụng các quy luật hành vi trong lĩnh vực này.")

def t_evidence(ev_id: str) -> str:
    if not ev_id:
        return ev_id
    mapping = {
        "empirical finding": "Phát hiện thực nghiệm",
        "empirical": "Phát hiện thực nghiệm",
        "theory": "Lý thuyết",
        "model": "Mô hình",
        "synthesis": "Tổng hợp"
    }
    return mapping.get(ev_id.lower(), ev_id)

def t_title(title: str) -> str:
    if not title:
        return title
    # Provide safe translations for known titles, otherwise return original
    mapping = {
        "anchoring effect": "Hiện tượng neo nhận thức",
        "homogeneity trap": "Bẫy đồng nhất",
        "cognitive load": "Tải trọng nhận thức",
    }
    return mapping.get(title.lower(), title)

