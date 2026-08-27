import yaml

files_to_update = {
    'knowledge/units/anti-patterns/NT-ANTI-PATTERN-0036-positional-bargaining-lock.yaml': {
        'summary': 'Trạng thái bế tắc xảy ra khi các bên đàm phán bám chặt vào lập trường cứng nhắc ban đầu thay vì tập trung vào lợi ích cốt lõi, dẫn đến tổn hại mối quan hệ và bỏ lỡ cơ hội hợp tác.',
        'definition': 'Bế tắc thương lượng theo vị thế là một hội chứng hành vi trong đàm phán, nơi cái tôi và thể diện bị trói buộc vào một lập trường cố định. Thay vì khám phá các phương án giải quyết vấn đề, các bên tiêu tốn tài nguyên để bảo vệ vị thế, tạo ra các tối hậu thư và từ chối nhượng bộ, làm leo thang xung đột không cần thiết.',
        'conditions': ['Xảy ra trong các cuộc đàm phán có tính cạnh tranh cao (phân bổ nguồn lực khan hiếm), thiếu niềm tin giữa các bên.', 'Khi người đàm phán bị áp lực phải chứng tỏ năng lực với tổ chức của họ.'],
        'exceptions': ['Các đàm phán một lần (one-off) không cần duy trì mối quan hệ lâu dài.', 'Khi vị thế của một bên áp đảo hoàn toàn đối phương (mô hình Zero-sum game).'],
        'applications': {'governance': ['Đào tạo đội ngũ cách tách bạch "con người" khỏi "vấn đề" trong đàm phán.', 'Xây dựng cơ chế BATNA (Best Alternative to a Negotiated Agreement) chuẩn hóa cho các giao dịch lớn.']},
        'risks': ['Kéo dài thời gian đàm phán một cách vô ích.', 'Đạt được những thỏa thuận dưới mức tối ưu (sub-optimal agreements).', 'Phá vỡ các mối quan hệ đối tác chiến lược lâu dài.']
    },
    'knowledge/units/anti-patterns/NT-ANTI-PATTERN-0015-culture-fit-trap.yaml': {
        'summary': 'Sự thiên lệch trong tuyển dụng và thăng tiến khi các nhà quản lý ưu tiên những cá nhân có tính cách giống mình, dẫn đến một tổ chức đồng nhất và mất khả năng đổi mới.',
        'definition': 'Bẫy "Phù hợp Văn hóa" là sự đánh đồng sai lệch giữa "sự dễ chịu khi làm việc cùng" (likability) với "sự phù hợp về giá trị cốt lõi". Nó tạo ra một buồng vang (echo chamber) trong tổ chức, nơi các ý kiến trái chiều bị triệt tiêu, và những cá nhân khác biệt bị loại trừ.',
        'conditions': ['Phổ biến ở các startup đang phát triển nóng.', 'Các phòng ban do một nhà lãnh đạo có cá tính quá mạnh chi phối.', 'Các tổ chức thiếu khung năng lực hành vi (behavioral competency framework) rõ ràng.'],
        'exceptions': ['Các tổ chức quy mô siêu nhỏ (dưới 5 người) ở giai đoạn sinh tồn, nơi sự đồng điệu cá nhân tuyệt đối là yếu tố sống còn.'],
        'applications': {'governance': ['Thay thế tiêu chí "Culture Fit" bằng "Culture Add" (Bổ sung văn hóa).', 'Thiết kế các bài phỏng vấn hành vi có cấu trúc khắt khe.', 'Đưa các thành viên có nền tảng đa dạng vào hội đồng đánh giá.']},
        'risks': ['Suy giảm nghiêm trọng năng lực đổi mới sáng tạo.', 'Tăng rủi ro thiên vị vô thức (unconscious bias) trong môi trường làm việc.', 'Tạo ra văn hóa bài trừ sự khác biệt và rò rỉ nhân tài đa dạng.']
    }
}

for filepath, new_data in files_to_update.items():
    with open(filepath, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    for key, value in new_data.items():
        data[key] = value
        
    with open(filepath, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

print("Updated 2 files.")
