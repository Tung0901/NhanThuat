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
        "crisis-management": "Quản trị khủng hoảng",
        "power-dynamics": "Động lực quyền lực",
        "cognitive-bias": "Thiên kiến nhận thức",
        "organizational-resilience": "Khả năng phục hồi tổ chức",
        "innovation-management": "Quản trị đổi mới",
        "behavioral-economics-choice-architecture": "Kinh tế hành vi & Kiến trúc lựa chọn",
        "behavioral-design": "Thiết kế hành vi",
        "social-psychology": "Tâm lý xã hội",
        "persuasion-influence": "Thuyết phục & Ảnh hưởng",
        "consumer-psychology": "Thấu hiểu Khách hàng",
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
        "thanh-su": "Nghiên cứu các chiến lược ra quyết định, thực thi và quản trị rủi ro để đạt mục tiêu.",
        "crisis-management": "Nghiên cứu cách chuẩn bị, ứng phó và phục hồi tổ chức khi đối mặt với khủng hoảng, bảo toàn niềm tin và uy tín.",
        "power-dynamics": "Nghiên cứu cấu trúc quyền lực, sự phân bố và vận hành của quyền lực trong tổ chức và quan hệ con người.",
        "cognitive-bias": "Nghiên cứu các thiên kiến nhận thức — những lối tắt tư duy có hệ thống ảnh hưởng đến phán đoán và quyết định.",
        "organizational-resilience": "Nghiên cứu năng lực thích nghi, chống chịu và phục hồi của tổ chức trước biến động, khủng hoảng.",
        "innovation-management": "Nghiên cứu quy trình khơi nguồn, đánh giá và triển khai ý tưởng mới trong tổ chức.",
        "behavioral-economics-choice-architecture": "Nghiên cứu cách thiết kế bối cảnh lựa chọn để định hướng hành vi mà không hạn chế quyền tự do quyết định.",
        "behavioral-design": "Nghiên cứu việc áp dụng các quy luật hành vi để thiết kế sản phẩm, chính sách và trải nghiệm.",
        "social-psychology": "Nghiên cứu cách con người suy nghĩ, cảm nhận và hành xử dưới ảnh hưởng của người khác và bối cảnh xã hội.",
        "persuasion-influence": "Nghiên cứu các cơ chế thuyết phục, tác động và chuyển hóa quan điểm của người khác một cách có nguyên tắc.",
        "human-nature": "Nghiên cứu bản chất cốt lõi của con người — các khuynh hướng, giới hạn và quy luật chi phối hành vi.",
        "motivation": "Nghiên cứu các cơ chế thúc đẩy, định hướng và duy trì hành vi của con người.",
        "decision-making": "Nghiên cứu quá trình ra quyết định, các yếu tố tác động và lối tắt tư duy trong lựa chọn.",
        "leadership": "Nghiên cứu nghệ thuật dẫn dắt, truyền cảm hứng và tạo ảnh hưởng của người lãnh đạo.",
        "learning": "Nghiên cứu cơ chế tiếp thu, ghi nhớ và chuyển hóa kinh nghiệm thành năng lực.",
        "conflict": "Nghiên cứu nguồn gốc, diễn biến và phương thức xử lý xung đột trong tổ chức.",
        "personality": "Nghiên cứu cấu trúc tính cách và cách dự đoán hành vi từ đặc điểm cá nhân.",
        "hiring": "Nghiên cứu phương pháp nhận diện, đánh giá và tuyển chọn nhân tài.",
        "team-building": "Nghiên cứu cách hình thành, gắn kết và vận hành đội ngũ hiệu quả.",
        "delegation": "Nghiên cứu nghệ thuật giao việc, trao quyền và chịu trách nhiệm.",
        "communication": "Nghiên cứu cơ chế truyền thông tin và tạo hiệu ứng trong giao tiếp.",
        "incentives": "Nghiên cứu hệ thống động cơ, phần thưởng và tác động của chúng lên hành vi.",
        "trust": "Nghiên cứu cơ chế hình thành, củng cố và sụp đổ của niềm tin.",
        "negotiation": "Nghiên cứu nghệ thuật thương lượng và đạt thỏa thuận có lợi cho các bên.",
        "authority": "Nghiên cứu thẩm quyền, uy tín và cách quyền lực hợp pháp vận hành.",
        "influence": "Nghiên cứu các kỹ thuật tác động và thuyết phục người khác.",
        "strategy": "Nghiên cứu tư duy chiến lược và nghệ thuật định vị, cạnh tranh.",
        "execution": "Nghiên cứu cơ chế chuyển hóa ý định thành hành động và kết quả.",
        "culture": "Nghiên cứu văn hóa tổ chức và ảnh hưởng của nó lên hành vi tập thể.",
        "ethics": "Nghiên cứu nguyên tắc đạo đức và giới hạn ứng xử trong quản trị.",
        "consumer-psychology": "Nghiên cứu quá trình tâm lý, cảm xúc và hành vi của người tiêu dùng trong quyết định mua sắm và lòng trung thành."
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
        "synthesis": "Tổng hợp",
        "strong": "Mạnh",
        "supported": "Được hỗ trợ",
        "provisional": "Dự kiến (tạm thời)",
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

