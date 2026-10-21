"""Deterministic pilot content generator, recovery tool, and anti-boilerplate validator.

This module replaces ad-hoc scratch scripts with a repository-resident, deterministic
CLI tool that:
1. Supports ``--dry-run`` and ``--manifest <path>`` output.
2. Never automatically mutates ``status``, ``evidence``, or ``version`` during content
   generation.
3. Enforces anti-boilerplate, uncertainty-posture, and evidence-truthfulness checks.
4. Supports controlled recovery of the 352 modified knowledge units.
"""

from __future__ import annotations

import argparse
import io
import json
import re
import subprocess
import sys
import tarfile
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
YAML_LOADER = getattr(yaml, "CSafeLoader", yaml.SafeLoader)

BANNED_BOILERPLATE_PHRASES: tuple[str, ...] = (
    "mọi thất bại trong việc xử lý",
    "Chúng ta không đánh cược vận mệnh dự án",
    "Trong một phiên họp quyết định nhân sự",
    "con người luôn vận hành trên hai tầng sóng",
    "cửa sổ duy nhất phơi bày cấu trúc nhân cách thật sự",
    "chân lý bất biến",
    "mọi thất bại",
    "duy nhất",
)

REQUIRED_PILOT_SECTIONS: tuple[str, ...] = (
    "Điều kiện áp dụng",
    "Ngoại lệ",
    "Mức bất định",
    "Rủi ro diễn giải sai",
    "Nguồn truy nguyên",
)

SOURCE_CLASS_TAGS: tuple[str, ...] = (
    "[Nghiên cứu thực nghiệm]",
    "[Nguồn cổ điển]",
    "[Sách phổ thông]",
    "[Suy luận biên tập]",
)

PILOT_UNIT_SPECS: dict[str, dict[str, Any]] = {
    "NT-LAW-3201": {
        "evidence": {
            "level": "supported",
            "references": [
                ("[Nghiên cứu thực nghiệm] Plassmann, H., O'Doherty, J., Shiv, B., & Rangel, A. "
                "(2008). Marketing actions can modulate neural representations of experienced "
                "pleasantness. PNAS, 105(3), 1050-1054 (Thực nghiệm fMRI về định giá và cảm nhận)."),
                ("[Nghiên cứu thực nghiệm] Thaler, R. H. (1985). Mental accounting and consumer "
                "choice. Marketing Science, 4(3), 199-214 (Cơ chế lợi ích giao dịch và giá tham chiếu)."),
                ("[Sách phổ thông] Sutherland, R. (2019). Alchemy: The Dark Art and Curious Science "
                "of Creating Magic in Brands, Business, and Life. William Morrow."),
                ("[Suy luận biên tập] Phân tích biên giới giữa định vị giá trị cảm nhận và rủi ro "
                "đứt gãy kỳ vọng sau mua trong thương mại B2B/B2C."),
            ],
        },
        "content": """### 1. Cơ chế Hình thành Giá trị Cảm nhận
**Quy luật Giá trị Cảm nhận** (`NT-LAW-3201`) phản ánh hiện tượng người mua đánh giá sản phẩm thông qua khung tham chiếu bối cảnh, tín hiệu uy tín và mức giải tỏa lo âu hơn là chỉ cộng dồn chi phí sản xuất vật lý. Trong kinh tế học hành vi, Richard Thaler (1985) phân tách tổng hữu dụng thành *hữu dụng thu nhận* (acquisition utility) và *hữu dụng giao dịch* (transaction utility): mức sẵn sàng chi trả phụ thuộc mạnh vào điểm neo tham chiếu mà bối cảnh giao dịch thiết lập.

### 2. Điều kiện áp dụng & Ngoại lệ
- **Điều kiện áp dụng:**
  - Giao dịch có độ bất đối xứng thông tin cao hoặc chất lượng khó kiểm định ngay trước khi sử dụng (dịch vụ tư vấn, phần mềm doanh nghiệp, sản phẩm trải nghiệm).
  - Người mua chịu áp lực trách nhiệm giải trình trước tập thể và cần tín hiệu giảm rủi ro tâm lý.
- **Ngoại lệ:**
  - Hàng hóa tiêu chuẩn hóa (commodity) có thông số kỹ thuật minh bạch, mua sắm qua đấu thầu định lượng hoặc hợp đồng kỳ hạn.
  - Bối cảnh người mua có quy trình kiểm thử kỹ thuật độc lập (blind testing) tách rời thương hiệu khỏi hiệu năng thực tế.

### 3. Mức bất định & Rủi ro diễn giải sai
- **Mức bất định:** Trung bình (phụ thuộc vào độ trưởng thành thông tin của thị trường và tần suất lặp lại giao dịch). Hiệu ứng bối cảnh mạnh ở lần mua đầu nhưng suy giảm nhanh ở các chu kỳ gia hạn nếu hiệu năng vận hành thực tế không đáp ứng kỳ vọng.
- **Rủi ro diễn giải sai:**
  - Nhầm lẫn quy luật này thành lời khuyên coi nhẹ chất lượng cốt lõi để tập trung vào hình thức bề ngoài.
  - Áp dụng định giá cảm xúc vào nhóm khách hàng kỹ thuật chuyên sâu khiến đối tác nghi ngờ tính minh bạch.

### 4. Nguồn truy nguyên & Đối chiếu Đông - Tây
- **Nguồn truy nguyên:** Kết hợp thực nghiệm thần kinh học tiêu dùng (Plassmann et al., 2008), lý thuyết kế toán tâm lý (Thaler, 1985) và quan sát thực hành định vị của Rory Sutherland (2019).
- **Đối chiếu cổ điển `[Nguồn cổ điển]`:** Chiến Quốc Sách (tích *Sở vương hiếu tế yêu* và tích *Bá Nhạc xem ngựa*) chỉ ra rằng giá trị trao đổi trên thị trường biến thiên theo tín hiệu thẩm định của người có uy tín và bối cảnh khan hiếm, nhưng về dài hạn vẫn phải chịu sự kiểm chứng của công năng thực tế (*Hàn Phi Tử — Công Danh*).
""",
    },
    "NT-LAW-4102": {
        "evidence": {
            "level": "strong",
            "references": [
                ("[Nghiên cứu thực nghiệm] Kahneman, D., & Tversky, A. (1979). Prospect Theory: "
                "An Analysis of Decision under Risk. Econometrica, 47(2), 263-291 (Hàm giá trị "
                "bất đối xứng giữa vùng lãi và vùng lỗ)."),
                ("[Nghiên cứu thực nghiệm] Walasek, L., & Stewart, N. (2015). How to make loss "
                "aversion disappear and reverse. Journal of Experimental Psychology: General, "
                "144(1), 7-11 (Điều kiện biên làm suy giảm hoặc đảo chiều hệ số ngại mất mát)."),
                ("[Nguồn cổ điển] Tôn Vũ — Tôn Tử Binh Pháp, thiên Cửu Địa (Phân tích tâm lý sĩ tốt "
                "khi rơi vào thế tử địa so với tán địa)."),
                ("[Suy luận biên tập] Khung hiệu chỉnh thiên kiến phòng thủ trong quyết định phân bổ "
                "vốn và cắt lỗ dự án."),
            ],
        },
        "content": """### 1. Cơ chế Bất đối xứng giữa Lợi ích và Tổn thất
**Quy luật Ngại Mất Mát (Loss Aversion)** (`NT-LAW-4102`) mô tả xu hướng xác suất trong đó một khoản tổn thất tiềm năng tạo ra cường độ phản ứng tâm lý lớn hơn so với một khoản thu lợi tương đương tính từ cùng điểm tham chiếu (Kahneman & Tversky, 1979). Hệ quả quản trị là cá nhân và ủy ban thường trì hoãn dừng các dự án kém hiệu quả (để tránh hiện thực hóa khoản lỗ) hoặc từ chối các khoản đầu tư có kỳ vọng dương nhưng biến động ngắn hạn.

### 2. Điều kiện áp dụng & Ngoại lệ
- **Điều kiện áp dụng:**
  - Quyết định được đóng khung quanh một điểm tham chiếu hiện trạng (status quo) rõ rệt như ngân sách năm trước, biên lợi nhuận hiện hữu hoặc quyền hạn đang nắm giữ.
  - Cơ chế đánh giá nhân sự phạt nặng sai sót hữu hình hơn là chi phí cơ hội vô hình.
- **Ngoại lệ:**
  - Khi quy mô tiền cược nhỏ so với tổng tài sản hoặc khi phạm vi giá trị khả dĩ của lợi ích rộng hơn nhiều so với tổn thất (Walasek & Stewart, 2015).
  - Những nhà vận hành chuyên nghiệp giao dịch theo quy tắc định lượng tự động (algorithmic / rule-based stop-loss).

### 3. Mức bất định & Rủi ro diễn giải sai
- **Mức bất định:** Hệ số ngại mất mát không phải hằng số cố định cho mọi cá nhân hay văn hóa; các nghiên cứu lặp lại cho thấy hệ số này dao động mạnh theo cách trình bày thông tin, kinh nghiệm chuyên môn và trạng thái tâm lý.
- **Rủi ro diễn giải sai:**
  - Giả định cứng nhắc rằng con người lúc nào cũng sợ rủi ro; thực tế trong vùng tổn thất sâu, chủ thể lại có xu hướng tìm kiếm rủi ro cao (risk-seeking in the domain of losses) để gỡ gạc.
  - Lạm dụng thông điệp đe dọa mất mát trong quản trị nội bộ gây co cụm phòng thủ và triệt tiêu sáng kiến.

### 4. Nguồn truy nguyên & Đối chiếu Đông - Tây
- **Nguồn truy nguyên:** Lý thuyết Triển vọng (Kahneman & Tversky, 1979) kết hợp nghiên cứu thực nghiệm hiện đại về giới hạn điều kiện của Loss Aversion (Walasek & Stewart, 2015).
- **Đối chiếu cổ điển `[Nguồn cổ điển]`:** Tôn Tử Binh Pháp (thiên *Cửu Địa*) phân biệt rõ hành vi của con người khi còn đường lui (dễ dao động để bảo toàn cái đang có) với khi rơi vào *tử địa* (chuyển sang liều lĩnh tìm đường sống), tương ứng với sự đảo chiều khẩu vị rủi ro ở vùng tổn thất của Lý thuyết Triển vọng.
""",
    },
    "NT-LAW-2101": {
        "evidence": {
            "level": "supported",
            "references": [
                ("[Nghiên cứu thực nghiệm] Weick, K. E. (1993). The collapse of sensemaking in "
                "organizations: The Mann Gulch disaster. Administrative Science Quarterly, "
                "38(4), 628-652 (Sự tan rã cấu trúc nhận thức khi khủng hoảng thiếu phản hồi)."),
                ("[Nguồn cổ điển] Tôn Vũ — Tôn Tử Binh Pháp, thiên Binh Thế & Cửu Biến (Quản trị "
                "nhịp độ và cắt đứt hiệu ứng dây chuyền khi biến cố phát sinh)."),
                ("[Sách phổ thông] Perrow, C. (1984). Normal Accidents: Living with High-Risk "
                "Technologies. Basic Books (Cơ chế khuếch đại sự cố trong hệ thống liên kết chặt)."),
                ("[Suy luận biên tập] Quy trình phân lập sự cố và thiết lập nhịp thông tin trong "
                "vận hành doanh nghiệp."),
            ],
        },
        "content": """### 1. Cơ chế Khuếch đại Độ nhiễu trong Khủng hoảng
**Định luật Entropy trong Khủng hoảng** (`NT-LAW-2101`) chỉ ra rằng trong các hệ thống tổ chức có độ liên kết chặt (tightly coupled systems), khoảng trống thông tin và độ trễ chỉ huy không giữ nguyên trạng thái tĩnh mà thường kích hoạt các phản ứng suy đoán, tự vệ cục bộ và lan truyền sự cố sang các bộ phận lân cận.

### 2. Điều kiện áp dụng & Ngoại lệ
- **Điều kiện áp dụng:**
  - Các sự cố vận hành, thanh khoản, an ninh dữ liệu hoặc truyền thông có tốc độ lan truyền nhanh và liên quan đến nhiều bên phụ thuộc lẫn nhau.
  - Kênh thông tin chính thức bị gián đoạn khiến các đơn vị cơ sở tự hành động theo tin đồn hoặc giả định cục bộ.
- **Ngoại lệ:**
  - Các sự cố kỹ thuật đã được phân lập vật lý hoặc có cầu chì ngắt tự động (circuit breakers) tách biệt hoàn toàn khỏi hệ thống chính.
  - Những biến động diễn tiến chậm, có dữ liệu quan trắc đầy đủ; trong trường hợp này việc can thiệp vội vã có thể gây nhiễu nhiều hơn việc quan sát thêm.

### 3. Mức bất định & Rủi ro diễn giải sai
- **Mức bất định:** Trung bình - Cao. Tốc độ gia tăng độ hỗn loạn phụ thuộc lớn vào cấu trúc phân quyền sẵn có và mức độ tập dượt quy trình ứng phó sự cố trước đó (Weick, 1993).
- **Rủi ro diễn giải sai:**
  - Đồng nhất việc phản ứng kịp thời với việc ra lệnh chuyên quyền thiếu kiểm chứng, dẫn đến sửa sai chỗ này nhưng làm vỡ cấu trúc chỗ khác.
  - Hoang mang phóng đại các sự cố cục bộ nhỏ thành khủng hoảng toàn diện làm kiệt sức đội ngũ.

### 4. Nguồn truy nguyên & Đối chiếu Đông - Tây
- **Nguồn truy nguyên:** Nghiên cứu thực địa về sự sụp đổ kiến tạo ý nghĩa trong thảm họa Mann Gulch của Karl Weick (1993) và lý thuyết tai nạn hệ thống của Charles Perrow (1984).
- **Đối chiếu cổ điển `[Nguồn cổ điển]`:** Tôn Tử Binh Pháp (thiên *Binh Thế*) phân biệt giữa *loạn* sinh ra từ *trị* khi có phân định bộ ngũ, hiệu lệnh rõ ràng với sự hỗn loạn dây chuyền khi đứt gãy thông tin chỉ huy.
""",
    },
    "NT-PRINCIPLE-4101": {
        "evidence": {
            "level": "strong",
            "references": [
                ("[Nghiên cứu thực nghiệm] Sweller, J. (1988). Cognitive load during problem "
                "solving: Effects on learning. Cognitive Science, 12(2), 257-285 (Phân loại tải "
                "nhận thức nội tại, ngoại lai và kiến tạo)."),
                ("[Nghiên cứu thực nghiệm] Cowan, N. (2001). The magical number 4 in short-term "
                "memory: A reconsideration of mental storage capacity. Behavioral and Brain "
                "Sciences, 24(1), 87-114."),
                ("[Nguồn cổ điển] Hàn Phi Tử — Thiên Dụ Lão & Thuyết Nan (Nguyên lý giản lược quy "
                "tắc thực thi để trăm họ và thuộc cấp dễ hiểu, dễ tuân hành)."),
                "[Suy luận biên tập] Thiết kế quy trình phê duyệt và bảng điều khiển giảm tải ngoại lai.",
            ],
        },
        "content": """### 1. Cơ chế Tối ưu Hóa Bộ nhớ Làm việc
**Nguyên tắc Giảm Tải trọng Nhận thức (Cognitive Load Reduction)** (`NT-PRINCIPLE-4101`) dựa trên giới hạn dung lượng của bộ nhớ làm việc (Cowan, 2001) và Lý thuyết Tải nhận thức của John Sweller (1988). Lý thuyết này tách bạch ba loại tải: *tải nội tại* (độ phức tạp vốn có của bài toán), *tải ngoại lai* (nhiễu do cách trình bày, thủ tục rườm rà) và *tải kiến tạo* (nỗ lực tư duy để hình thành cấu trúc hiểu biết sâu). Mục tiêu của nguyên tắc là cắt giảm tải ngoại lai chứ không phải xóa bỏ tư duy phân tích.

### 2. Điều kiện áp dụng & Ngoại lệ
- **Điều kiện áp dụng:**
  - Thiết kế quy trình vận hành chuẩn (SOP), giao diện hệ thống điều hành, báo cáo giao ban hoặc hướng dẫn xử lý sự cố dưới áp lực thời gian.
  - Khi người thực thi mới tiếp cận quy trình hoặc phải xử lý đồng thời nhiều luồng thông tin.
- **Ngoại lệ:**
  - Các phiên thẩm định chiến lược, kiểm toán rủi ro hoặc nghiên cứu chuyên sâu — nơi việc tạo độ trễ nhận thức có chủ đích (desirable difficulties) là cần thiết để kích hoạt tư duy phản biện.
  - Nhóm chuyên gia đã tự động hóa kỹ năng (expertise reversal effect): hướng dẫn chia nhỏ quá chi tiết lại gây vướng víu và làm giảm hiệu suất của họ.

### 3. Mức bất định & Rủi ro diễn giải sai
- **Mức bất định:** Thấp đối với tác vụ thao tác chuẩn hóa; Trung bình đối với tác vụ ra quyết định phức hợp vì ngưỡng quá tải phụ thuộc vào kinh nghiệm nền của từng cá nhân.
- **Rủi ro diễn giải sai:**
  - Đơn giản hóa quá mức các bài toán phức tạp thành khẩu hiệu nhị phân, làm ẩn đi các biến số rủi ro trọng yếu.
  - Biến quy trình thành danh sách đánh dấu máy móc khiến nhân sự ngừng đặt câu hỏi khi bối cảnh thực tế đã thay đổi.

### 4. Nguồn truy nguyên & Đối chiếu Đông - Tây
- **Nguồn truy nguyên:** Thực nghiệm tâm lý học nhận thức của John Sweller (1988) và Nelson Cowan (2001).
- **Đối chiếu cổ điển `[Nguồn cổ điển]`:** Pháp gia (*Hàn Phi Tử*, *Thương Quân Thư*) nhấn mạnh pháp lệnh ban ra phải rõ ràng, giản ước và nhất quán để người thực thi không bị rối loạn bởi các quy định chồng chéo.
""",
    },
    "NT-PRINCIPLE-0063": {
        "evidence": {
            "level": "supported",
            "references": [
                ("[Nghiên cứu thực nghiệm] Edmondson, A. (1999). Psychological safety and learning "
                "behavior in work teams. Administrative Science Quarterly, 44(2), 350-383 "
                "(Tác động của chênh lệch quyền lực lên sự cởi mở thông tin và học hỏi nhóm)."),
                ("[Nghiên cứu thực nghiệm] French, J. R., & Raven, B. (1959). The bases of social "
                "power. In D. Cartwright (Ed.), Studies in Social Power (pp. 150-167). University "
                "of Michigan Press."),
                ("[Nguồn cổ điển] Tư Mã Quang — Tư Trị Thông Giám (Điển tích Đường Thái Tông chủ động "
                "tiết chế uy quyền thiên tử để mở đường can gián cho Ngụy Trưng)."),
                "[Suy luận biên tập] Thiết kế quy tắc phát biểu và trọng số chuyên môn trong hội đồng.",
            ],
        },
        "content": """### 1. Cơ chế Chuyển dịch từ Quyền lực Chức danh sang Thẩm quyền Chuyên môn
**Giảm thiểu quyền lực vai trò** (`NT-PRINCIPLE-0063`) là nguyên tắc thiết kế tương tác quản trị nhằm hạn chế việc dùng cấp bậc hành chính (legitimate/coercive power theo French & Raven, 1959) làm căn cứ kết luận trong các bài toán chuyên môn. Khi người đứng đầu sớm áp đặt ý kiến bằng vị thế, cấp dưới thường điều chỉnh phát biểu theo hướng thuận chiều để giảm rủi ro cá nhân, làm mất nguồn dữ liệu thực địa.

### 2. Điều kiện áp dụng & Ngoại lệ
- **Điều kiện áp dụng:**
  - Các quyết định kỹ thuật, kiến trúc sản phẩm, chẩn đoán nguyên nhân gốc rễ (post-mortem) hoặc đánh giá rủi ro đầu tư — nơi chất lượng thông tin quan trọng hơn tốc độ tuân lệnh.
  - Đội ngũ có đủ năng lực chuyên môn và thiện chí hợp tác để đóng góp ý kiến có căn cứ.
- **Ngoại lệ:**
  - Tình huống ứng cứu khẩn cấp đòi hỏi chuỗi chỉ huy tập trung một đầu mối để hành động tức thời.
  - Các quyết định thuộc thẩm quyền chịu trách nhiệm pháp lý cá nhân không thể ủy quyền của người đại diện theo pháp luật.

### 3. Mức bất định & Rủi ro diễn giải sai
- **Mức bất định:** Trung bình. Hiệu quả của việc giảm sử dụng quyền lực vai trò phụ thuộc vào văn hóa khoảng cách quyền lực (power distance) của tổ chức và mức độ rõ ràng của tiêu chí ra quyết định.
- **Rủi ro diễn giải sai:**
  - Đánh đồng việc tiết chế quyền lực chức danh với việc buông lỏng trách nhiệm chốt quyết định cuối cùng, dẫn đến thảo luận kéo dài không có người chịu trách nhiệm.
  - Tạo khoảng trống quyền lực hình thức khiến các nhóm lợi ích ngầm không chính thức thao túng cuộc họp.

### 4. Nguồn truy nguyên & Đối chiếu Đông - Tây
- **Nguồn truy nguyên:** Phân loại nguồn quyền lực xã hội của French & Raven (1959) và nghiên cứu thực nghiệm về an toàn tâm lý trong nhóm làm việc của Amy Edmondson (1999).
- **Đối chiếu cổ điển `[Nguồn cổ điển]`:** *Tư Trị Thông Giám* ghi lại việc Đường Thái Tông nhận thức rõ uy thế của bậc quân vương dễ khiến quần thần im lặng giữ thân, do đó phải chủ động hạ thấp sắc mặt và thiết lập cơ chế bảo vệ người nói thẳng (*Kiêm thính tắc minh*).
""",
    },
    "NT-MODEL-2101": {
        "evidence": {
            "level": "supported",
            "references": [
                ("[Nghiên cứu thực nghiệm] Bundy, J., Pfarrer, M. D., Short, C. E., & Coombs, W. T. "
                "(2017). Crises and crisis management: Integration, interpretation, and research "
                "development. Journal of Management, 43(6), 1661-1692."),
                ("[Sách phổ thông] Coombs, W. T. (2014). Ongoing Crisis Communication: Planning, "
                "Managing, and Responding. SAGE Publications (Situational Crisis Communication Theory)."),
                ("[Nguồn cổ điển] Tôn Vũ — Tôn Tử Binh Pháp, thiên Cửu Biến (Nguyên tắc phòng bị và "
                "xử lý biến cố đa diện)."),
                ("[Suy luận biên tập] Khung điều phối ba trục Khoanh vùng - Truyền thông - Khắc phục "
                "trong vận hành sự cố."),
            ],
        },
        "content": """### 1. Cấu trúc Ba Trụ cột Điều phối Sự cố
**Tam Giác Ứng Phó Khủng Hoảng** (`NT-MODEL-2101`) cung cấp mô hình phân bổ nguồn lực song song trên ba mặt trận khi xảy ra biến cố tổ chức: (1) *Khoanh vùng kỹ thuật/vận hành* để chặn đà lan rộng của thiệt hại, (2) *Truyền thông có kiểm chứng* để duy trì sự tin cậy với các bên liên quan, và (3) *Khắc phục căn nguyên* để phục hồi hoạt động bền vững.

### 2. Điều kiện áp dụng & Ngoại lệ
- **Điều kiện áp dụng:**
  - Sự cố vận hành, gián đoạn dịch vụ, khủng hoảng uy tín hoặc vi phạm tuân thủ có tác động đồng thời lên cả hệ thống nội bộ lẫn khách hàng/đối tác bên ngoài.
  - Tổ chức có khả năng phân tách vai trò giữa nhóm xử lý kỹ thuật trực tiếp và nhóm điều phối thông tin.
- **Ngoại lệ:**
  - Các lỗi kỹ thuật nội bộ nhỏ được xử lý tự động trước khi ảnh hưởng đến người dùng cuối; việc kích hoạt truyền thông diện rộng trong trường hợp này là không cần thiết.
  - Các cuộc điều tra pháp lý hoặc an ninh mạng đang trong giai đoạn bảo mật theo yêu cầu của cơ quan chức năng (cần giới hạn phạm vi công bố thông tin).

### 3. Mức bất định & Rủi ro diễn giải sai
- **Mức bất định:** Trung bình. Trong giai đoạn đầu của sự cố, dữ liệu nguyên nhân gốc rễ thường chưa đầy đủ; do đó trụ cột truyền thông phải nêu rõ những gì đã xác minh và những gì đang tiếp tục kiểm tra thay vì cam kết tuyệt đối quá sớm.
- **Rủi ro diễn giải sai:**
  - Xem truyền thông khủng hoảng là việc che giấu sự cố hoặc hứa hẹn vượt khả năng khắc phục thực tế, dẫn đến mất uy tín kép khi sự thật được phơi bày.
  - Dồn toàn bộ nhân sự kỹ thuật sang trả lời báo cáo khiến tiến độ khoanh vùng và sửa lỗi bị đình trệ.

### 4. Nguồn truy nguyên & Đối chiếu Đông - Tây
- **Nguồn truy nguyên:** Tổng hợp nghiên cứu quản trị khủng hoảng của Bundy et al. (2017) và Lý thuyết Truyền thông Khủng hoảng theo Tình huống (SCCT) của W. Timothy Coombs (2014).
- **Đối chiếu cổ điển `[Nguồn cổ điển]`:** Tôn Tử Binh Pháp và tư tưởng trị thủy cổ đại đều nhấn mạnh nguyên tắc vừa đắp đê ngăn dòng chảy tràn lan (khoanh vùng), vừa ổn định lòng người (truyền thông), vừa khơi thông dòng chính (khắc phục gốc rễ).
""",
    },
    "NT-MODEL-2201": {
        "evidence": {
            "level": "strong",
            "references": [
                ("[Nghiên cứu thực nghiệm] French, J. R., & Raven, B. (1959). The bases of social "
                "power. In D. Cartwright (Ed.), Studies in Social Power (pp. 150-167). University "
                "of Michigan Press."),
                ("[Nghiên cứu thực nghiệm] Podsakoff, P. M., & Schriesheim, C. A. (1985). Field "
                "studies of French and Raven's bases of power: Critique, reanalysis, and "
                "suggestions for future research. Psychological Bulletin, 97(3), 387-411."),
                ("[Nguồn cổ điển] Hàn Phi Tử — Thiên Nhị Bính & Bát Kinh (Phân tích quyền thưởng phạt "
                "cùng uy thế vị trí và giới hạn khi thiếu thực tài)."),
                "[Suy luận biên tập] Ứng dụng chẩn đoán cơ cấu quyền lực của nhà quản lý trong tổ chức.",
            ],
        },
        "content": """### 1. Cấu trúc Năm Nguồn Quyền lực Tổ chức
**Ma Trận Quyền Lực** (`NT-MODEL-2201`) chuẩn hóa phân loại kinh điển của French & Raven (1959) gồm hai nhóm nguồn lực tác động:
1. *Quyền lực gắn với vị trí (Positional Power)*: Quyền lực hợp pháp (Legitimate), Quyền lực tưởng thưởng (Reward), Quyền lực cưỡng chế (Coercive).
2. *Quyền lực gắn với cá nhân (Personal Power)*: Quyền lực chuyên gia (Expert), Quyền lực tham chiếu/uy tín (Referent).

Các phân tích tổng hợp thực địa (Podsakoff & Schriesheim, 1985) cho thấy quyền lực chuyên gia và tham chiếu có tương quan dương bền vững hơn với sự gắn kết nội tâm, trong khi lạm dụng quyền lực cưỡng chế thường chỉ tạo ra sự phục tùng ngắn hạn kèm chi phí giám sát cao.

### 2. Điều kiện áp dụng & Ngoại lệ
- **Điều kiện áp dụng:**
  - Chẩn đoán nguyên nhân vì sao một chỉ đạo chiến lược không đi vào thực tế (do thiếu thẩm quyền chính thức hay thiếu uy tín chuyên môn).
  - Thiết kế lộ trình phát triển năng lực lãnh đạo cho quản lý cấp trung và chuyên gia đầu ngành.
- **Ngoại lệ:**
  - Các môi trường vận hành có quy định an toàn sinh mạng hoặc kỷ luật quân sự nghiêm ngặt — nơi quyền lực hợp pháp theo vị trí phải được ưu tiên tuân thủ tức thời tại hiện trường.

### 3. Mức bất định & Rủi ro diễn giải sai
- **Mức bất định:** Thấp - Trung bình. Dù phân loại 5 nguồn quyền lực có nền tảng thực nghiệm rộng, hiệu quả tương đối của từng nguồn lực vẫn biến thiên theo văn hóa tổ chức, giai đoạn trưởng thành của nhân sự và mức độ khủng hoảng.
- **Rủi ro diễn giải sai:**
  - Phủ nhận hoàn toàn vai trò của quyền lực vị trí và chế tài hợp pháp, khiến tổ chức thiếu ranh giới kỷ luật đối với các hành vi vi phạm chuẩn mực.
  - Nhầm lẫn sức hút bề nổi nhất thời với quyền lực tham chiếu bền vững dựa trên sự chính trực.

### 4. Nguồn truy nguyên & Đối chiếu Đông - Tây
- **Nguồn truy nguyên:** Mô hình 5 nguồn quyền lực của French & Raven (1959) và tổng quan phê bình thực nghiệm của Podsakoff & Schriesheim (1985).
- **Đối chiếu cổ điển `[Nguồn cổ điển]`:** Hàn Phi Tử phân định rõ *Thế* (vị trí), *Pháp* (quy tắc thưởng phạt công minh) và *Thuật* (năng lực thẩm định), đồng thời Tuân Tử (*Vương Chế*) bổ sung rằng nếu chỉ có *Thế* và *Hình* mà thiếu *Đức/Tín* (tương ứng Referent Power) thì chỉ giữ được sự phục tùng bề mặt.
""",
    },
    "NT-PHENOMENON-4101": {
        "evidence": {
            "level": "supported",
            "references": [
                ("[Nguồn cổ điển] Veblen, T. (1899). The Theory of the Leisure Class: An Economic "
                "Study of Institutions. Macmillan (Khái niệm tiêu dùng phô trương — Conspicuous Consumption)."),
                ("[Nghiên cứu thực nghiệm] Bagwell, L. S., & Bernheim, B. D. (1996). Veblen effects "
                "in a theory of conspicuous consumption. American Economic Review, 86(3), 349-373."),
                ("[Nghiên cứu thực nghiệm] Nelissen, R. M., & Meijers, M. H. (2011). Social benefits "
                "of luxury brands as costly signals of wealth and status. Evolution and Human "
                "Behavior, 32(5), 343-355."),
                "[Suy luận biên tập] Phân tích biên giới của định giá tín hiệu địa vị trong thị trường cao cấp.",
            ],
        },
        "content": """### 1. Cơ chế Tín hiệu Đắt giá và Địa vị Xã hội
**Hiệu ứng Hàng hiệu (Veblen Effect)** (`NT-PHENOMENON-4101`), khởi nguồn từ phân tích xã hội học kinh tế của Thorstein Veblen (1899) và được mô hình hóa bởi Bagwell & Bernheim (1996), mô tả hiện tượng trong một số phân khúc đặc thù, mức giá cao đóng vai trò như một *tín hiệu đắt giá* (costly signal) khó làm giả về nguồn lực hoặc vị thế của người sở hữu. Khi mức giá giảm hoặc độ phổ cập tăng quá rộng, giá trị tín hiệu vị thế suy giảm khiến sức cầu từ nhóm khách hàng tìm kiếm sự khác biệt đi xuống.

### 2. Điều kiện áp dụng & Ngoại lệ
- **Điều kiện áp dụng:**
  - Sản phẩm/dịch vụ được tiêu dùng công khai (visible consumption), gắn với biểu tượng địa vị xã hội và có giới hạn cung ứng đáng tin cậy.
  - Nhóm khách hàng mục tiêu đặt trọng số cao vào sự phân tầng vị thế hơn là tối ưu hóa chi phí trên mỗi đơn vị công năng.
- **Ngoại lệ:**
  - Hàng hóa tiêu dùng nội bộ không mang tính biểu trưng xã hội hoặc mua sắm công nghiệp dựa trên bảng tính hoàn vốn (ROI).
  - Các nền văn hóa hoặc giai đoạn xã hội đề cao sự tiết kiệm, tối giản (inconspicuous consumption) hoặc nhạy cảm cao với việc phô trương tài sản.

### 3. Mức bất định & Rủi ro diễn giải sai
- **Mức bất định:** Trung bình - Cao. Hiệu ứng Veblen chỉ xuất hiện trong một dải giá và tập khách hàng hẹp; ngoài dải này, quy luật cầu thông thường (giá tăng làm giảm lượng cầu) vẫn giữ vai trò chi phối.
- **Rủi ro diễn giải sai:**
  - Ngộ nhận rằng chỉ cần tăng giá cao bất kỳ sản phẩm nào cũng sẽ tự động kích thích nhu cầu, bỏ qua nền tảng di sản thương hiệu, độ khan hiếm thực và chuẩn mực thẩm mỹ.
  - Khuyến mãi giảm giá tràn lan cho dòng sản phẩm định vị cao cấp, làm xói mòn lòng tin của nhóm khách hàng trung thành.

### 4. Nguồn truy nguyên & Đối chiếu Đông - Tây
- **Nguồn truy nguyên:** Tác phẩm cổ điển của Thorstein Veblen (1899), mô hình cân bằng tín hiệu của Bagwell & Bernheim (1996) và thực nghiệm tâm lý học tiến hóa của Nelissen & Meijers (2011).
- **Đối chiếu cổ điển `[Nguồn cổ điển]`:** *Quản Tử* (thiên *Thừa Mã* và *Khinh Trọng*) cùng *Hàn Phi Tử* từng phân tích tâm lý chuộng vật hiếm, ngọc quý của tầng lớp quyền quý và cảnh báo nhà quản trị phải phân biệt rõ giữa giá trị sử dụng thực tế với giá trị biểu trưng do sự khan hiếm tạo nên.
""",
    },
    "NT-PHENOMENON-4102": {
        "evidence": {
            "level": "strong",
            "references": [
                ("[Nghiên cứu thực nghiệm] Huber, J., Payne, J. W., & Puto, C. (1982). Adding "
                "asymmetrically dominated alternatives: Violations of regularity and the "
                "similarity hypothesis. Journal of Consumer Research, 9(1), 90-98 (Nghiên cứu gốc "
                "về hiệu ứng ưu thế bất đối xứng)."),
                ("[Nghiên cứu thực nghiệm] Frederick, S., Lee, L., & Baskin, E. (2014). The limits "
                "of attraction. Journal of Marketing Research, 51(4), 487-507 (Điều kiện giới hạn "
                "của hiệu ứng chim mồi đối với trải nghiệm phi định lượng)."),
                ("[Sách phổ thông] Ariely, D. (2008). Predictably Irrational: The Hidden Forces "
                "That Shape Our Decisions. HarperCollins."),
                "[Suy luận biên tập] Quy tắc đạo đức và giới hạn áp dụng kiến trúc lựa chọn trong định giá.",
            ],
        },
        "content": """### 1. Cơ chế Ưu thế Bất đối xứng trong Kiến trúc Lựa chọn
**Hiệu ứng Chim mồi (Decoy Effect / Asymmetric Dominance Effect)** (`NT-PHENOMENON-4102`), được chứng minh thực nghiệm bởi Huber, Payne & Puto (1982), xảy ra khi người ra quyết định đang phân vân giữa hai phương án có sự đánh đổi khó so sánh (ví dụ: Phương án A rẻ nhưng ít tính năng; Phương án B đắt nhưng nhiều tính năng). Sự xuất hiện của Phương án C (chim mồi) — bị Phương án B áp đảo hoàn toàn nhưng chỉ bị Phương án A áp đảo một phần — cung cấp một điểm tựa so sánh dễ dàng, làm tăng xác suất người mua chọn Phương án B.

### 2. Điều kiện áp dụng & Ngoại lệ
- **Điều kiện áp dụng:**
  - Các thuộc tính của sản phẩm/gói dịch vụ được biểu diễn bằng con số định lượng rõ ràng (dung lượng, số lượng giấy phép, mức giá) đặt cạnh nhau trên cùng bảng so sánh.
  - Người mua chưa có sẵn hàm ưu tiên cố định trước khi xem bảng giá.
- **Ngoại lệ:**
  - Khi các thuộc tính mang tính cảm tính, hình ảnh hoặc trải nghiệm khó quy đổi định lượng trực tiếp (Frederick, Lee & Baskin, 2014 chứng minh hiệu ứng suy yếu mạnh hoặc biến mất trong các bối cảnh này).
  - Người mua chuyên nghiệp đã xác định trước ngân sách trần cứng hoặc nhu cầu kỹ thuật tối thiểu.

### 3. Mức bất định & Rủi ro diễn giải sai
- **Mức bất định:** Trung bình. Hiệu ứng mang tính xác suất thống kê trên tập mẫu lớn, không đảm bảo dịch chuyển lựa chọn của từng cá nhân đơn lẻ.
- **Rủi ro diễn giải sai:**
  - Thiết kế phương án chim mồi quá lộ liễu hoặc vô lý khiến khách hàng cảm thấy bị thao túng và mất thiện cảm với thương hiệu.
  - Lạm dụng thủ thuật trình bày phương án trong báo cáo tham mưu nội bộ để dẫn dắt cấp trên chọn phương án định sẵn thay vì phân tích trung thực các đánh đổi.

### 4. Nguồn truy nguyên & Đối chiếu Đông - Tây
- **Nguồn truy nguyên:** Bài báo nền tảng của Huber, Payne & Puto (1982), nghiên cứu kiểm chứng giới hạn của Frederick et al. (2014) và sách phổ biến khoa học của Dan Ariely (2008).
- **Đối chiếu cổ điển `[Nguồn cổ điển]`:** Nghệ thuật thiết lập phương án so sánh trong *Chiến Quốc Sách* và *Quỷ Cốc Tử* (phép đặt thượng sách - trung sách - hạ sách) cho thấy việc trình bày một phương án đối chiếu giúp người nghe nhận rõ ưu thế tương đối của phương án trọng tâm.
""",
    },
    "NT-PHENOMENON-4103": {
        "evidence": {
            "level": "strong",
            "references": [
                ("[Nghiên cứu thực nghiệm] Hasher, L., Goldstein, D., & Toppino, T. (1977). "
                "Frequency and the conference of referential validity. Journal of Verbal Learning "
                "and Verbal Behavior, 16(1), 107-112 (Thực nghiệm gốc về tần suất lặp và độ tin cậy)."),
                ("[Nghiên cứu thực nghiệm] Fazio, L. K., Brashier, N. M., Payne, B. K., & Marsh, "
                "E. J. (2015). Knowledge does not protect against illusory truth. Journal of "
                "Experimental Psychology: General, 144(5), 993-1002."),
                ("[Nguồn cổ điển] Chiến Quốc Sách — Tần Sách (Điển tích Tăng Sâm giết người và "
                "Lưỡi câu truyền miệng: 'Tam nhân thành hổ')."),
                "[Suy luận biên tập] Cơ chế kiểm chứng chéo nguồn tin độc lập trong quản trị.",
            ],
        },
        "content": """### 1. Cơ chế Lưu loát Nhận thức và Ảo giác Đáng tin
**Hiệu ứng Ảo tưởng Sự thật (Illusory Truth Effect)** (`NT-PHENOMENON-4103`), được xác lập thực nghiệm bởi Hasher, Goldstein & Toppino (1977), chỉ ra rằng khi một mệnh đề được lặp lại qua nhiều lần tiếp xúc, não bộ xử lý mệnh đề đó nhanh và ít tốn nỗ lực hơn (processing fluency). Hệ thống nhận thức thường quy gán nhầm cảm giác quen thuộc và trôi chảy này thành tín hiệu của tính xác thực, ngay cả khi người nghe vốn có kiến thức nền liên quan (Fazio et al., 2015).

### 2. Điều kiện áp dụng & Ngoại lệ
- **Điều kiện áp dụng:**
  - Môi trường thông tin nhiễu loạn, người tiếp nhận bị quá tải nhận thức hoặc không có thời gian đối chiếu dữ liệu gốc tại thời điểm nghe.
  - Cùng một nhận định được lặp lại qua nhiều kênh trung gian có vẻ độc lập nhưng thực chất bắt nguồn từ một nguồn tin ban đầu.
- **Ngoại lệ:**
  - Khi người tiếp nhận đang ở chế độ kiểm toán bằng chứng chủ động (active verification) với dữ liệu đối chứng trực tiếp ngay trước mặt.
  - Khi nguồn phát thông tin đã bị xác nhận là có xung đột lợi ích trực tiếp và người nghe được cảnh báo ngay tại thời điểm mã hóa thông tin.

### 3. Mức bất định & Rủi ro diễn giải sai
- **Mức bất định:** Thấp - Trung bình. Hiệu ứng lặp lại làm dịch chuyển điểm đánh giá độ tin cậy trung bình trên diện rộng, nhưng mức độ chuyển hóa thành hành động thực tế còn phụ thuộc vào chi phí và rủi ro của hành động đó.
- **Rủi ro diễn giải sai:**
  - Trong quản trị nội bộ, nhầm lẫn một nhận định được nhiều phòng ban nhắc lại nhiều lần là dữ liệu đã kiểm chứng (trong khi đó chỉ là sự lặp lại của một giả định ban đầu chưa ai đo lường).
  - Sử dụng sự lặp lại khẩu hiệu để thay thế cho việc giải quyết các bất cập thực tế trong vận hành.

### 4. Nguồn truy nguyên & Đối chiếu Đông - Tây
- **Nguồn truy nguyên:** Thực nghiệm tâm lý học nhận thức của Hasher, Goldstein & Toppino (1977) và nghiên cứu mở rộng của Fazio et al. (2015).
- **Đối chiếu cổ điển `[Nguồn cổ điển]`:** *Chiến Quốc Sách* ghi lại hai điển tích kinh điển là *Tăng Sâm giết người* (mẹ Tăng Sâm ban đầu không tin, nhưng đến người thứ ba báo tin thì hoảng sợ bỏ khung cửi chạy) và *Tam nhân thành hổ* (Bàng Thông tâu với Ngụy Vương về việc ba người cùng nói có hổ ngoài chợ), phản ánh chính xác cơ chế tần suất lặp lại làm biến dạng phán đoán xác thực.
""",
    },
    "NT-ANTI-PATTERN-0012": {
        "evidence": {
            "level": "supported",
            "references": [
                ("[Nghiên cứu thực nghiệm] Khurana, R. (2002). Searching for a Corporate Savior: "
                "The Irrational Quest for Charismatic CEOs. Princeton University Press (Phân tích "
                "thực nghiệm về rủi ro phụ thuộc vào CEO có sức hút cá nhân)."),
                ("[Nghiên cứu thực nghiệm] House, R. J., & Howell, J. M. (1992). Personality and "
                "charismatic leadership. The Leadership Quarterly, 3(2), 81-108 (Phân biệt "
                "socialized vs. personalized charismatic leadership)."),
                ("[Nguồn cổ điển] Hàn Phi Tử — Thiên Thập Quá & Bát Gian (Cảnh báo rủi ro hệ thống "
                "khi sự vận hành đặt lên uy vọng cá nhân thay vì pháp độ và cơ chế kiểm soát)."),
                "[Suy luận biên tập] Thiết kế cơ chế phản biện thể chế và kế nhiệm giảm phụ thuộc cá nhân.",
            ],
        },
        "content": """### 1. Cơ chế Thay thế Thể chế bằng Hào quang Cá nhân
**Bẫy sức hút cá nhân** (`NT-ANTI-PATTERN-0012`) xuất hiện khi tổ chức đặt niềm tin quá mức vào sự tự tin, khả năng hùng biện và thành tích quá khứ của một cá nhân trung tâm, dẫn đến việc nới lỏng các hàng rào kiểm chứng độc lập, hội đồng thẩm định và quy trình kế nhiệm (Khurana, 2002). House & Howell (1992) phân biệt rõ giữa lãnh đạo có sức hút gắn với thể chế chung (socialized charisma) và lãnh đạo tập trung quyền lực vào cái tôi cá nhân (personalized charisma) — nhóm thứ hai làm gia tăng rủi ro điểm mù chiến lược.

### 2. Điều kiện áp dụng & Ngoại lệ
- **Điều kiện áp dụng:**
  - Tổ chức vừa trải qua khủng hoảng hoặc tăng trưởng nóng nhờ một cá nhân dẫn dắt, khiến tập thể hình thành tâm lý quy gán thành công cho một người.
  - Hội đồng quản trị hoặc ban kiểm soát thiếu tính độc lập về thông tin và chuyên môn.
- **Ngoại lệ:**
  - Khi sức hút truyền cảm hứng của người đứng đầu đi kèm với quy trình phản biện bắt buộc, phân quyền rõ ràng và đội ngũ kế cận đủ thẩm quyền phủ quyết kỹ thuật.
  - Giai đoạn khởi nghiệp rất sớm hoặc ứng cứu ngắn hạn khi cấu trúc quy trình chưa kịp hình thành, miễn là sớm chuyển giao sang cơ chế thể chế hóa.

### 3. Mức bất định & Rủi ro diễn giải sai
- **Mức bất định:** Trung bình. Sức hút cá nhân không tất yếu dẫn đến sụp đổ nếu tổ chức chủ động xây dựng cơ chế kiểm soát đối trọng; rủi ro chỉ trở thành hiện thực khi hào quang cá nhân làm tê liệt kênh báo động sớm.
- **Rủi ro diễn giải sai:**
  - Cực đoan hóa thành việc bài xích những nhà lãnh đạo có khả năng truyền cảm hứng và tầm nhìn mạnh mẽ.
  - Áp đặt bộ máy quan liêu cứng nhắc làm triệt tiêu tính quyết đoán cần thiết của người đứng đầu.

### 4. Nguồn truy nguyên & Đối chiếu Đông - Tây
- **Nguồn truy nguyên:** Nghiên cứu định lượng và lịch sử doanh nghiệp của Rakesh Khurana (2002) tại Harvard cùng phân tích tâm lý lãnh đạo của House & Howell (1992).
- **Đối chiếu cổ điển `[Nguồn cổ điển]`:** Pháp gia (*Hàn Phi Tử — Nan Thế*) chỉ rõ bậc hiền tài trăm năm mới xuất hiện một người, trong khi việc trị nước và vận hành tổ chức diễn ra hàng ngày; vì vậy không thể lấy sự kỳ vọng vào một cá nhân phi thường để thay thế cho chuẩn mực quy chế (*Pháp*) và cơ chế kiểm chứng (*Thuật*).
""",
    },
    "NT-ANTI-PATTERN-0013": {
        "evidence": {
            "level": "supported",
            "references": [
                ("[Nghiên cứu thực nghiệm] Kelman, H. C. (1958). Compliance, identification, and "
                "internalization: Three processes of attitude change. Journal of Conflict "
                "Resolution, 2(1), 51-60 (Phân biệt tuân thủ bề mặt do chế tài với đồng nhất hóa "
                "và nội tâm hóa)."),
                ("[Nghiên cứu thực nghiệm] Deci, E. L., Koestner, R., & Ryan, R. M. (1999). A "
                "meta-analytic review of experiments examining the effects of extrinsic rewards "
                "on intrinsic motivation. Psychological Bulletin, 125(6), 627-668."),
                ("[Nguồn cổ điển] Luận Ngữ — Vi Chính (Khổng Tử phân biệt hiệu quả của 'Đạo chi dĩ "
                "chính, tề chi dĩ hình' với 'Đạo chi dĩ đức, tề chi dĩ lễ')."),
                "[Suy luận biên tập] Chỉ số nhận diện tuân thủ đối phó và cơ chế chuyển dịch sang cam kết.",
            ],
        },
        "content": """### 1. Cơ chế Phân tách giữa Phục tùng Bề mặt và Cam kết Nội tâm
**Sự tuân thủ cưỡng ép** (`NT-ANTI-PATTERN-0013`) phản ánh trạng thái mà Herbert Kelman (1958) định nghĩa là *compliance* (chấp hành chỉ để tránh hình phạt hoặc nhận phần thưởng tức thời) thay vì *internalization* (nội tâm hóa mục tiêu vì hiểu rõ giá trị và tính hợp lý). Khi quản lý dùng đe dọa làm công cụ điều hành chủ đạo, nhân sự có xu hướng tối ưu hóa việc tránh lỗi trên giấy tờ, che giấu số liệu xấu và ngừng chủ động xử lý các vấn đề ngoài phạm vi bị giám sát trực tiếp.

### 2. Điều kiện áp dụng & Ngoại lệ
- **Điều kiện áp dụng:**
  - Các công việc đòi hỏi sự chủ động giải quyết vấn đề, chất lượng dịch vụ tinh tế hoặc chia sẻ thông tin trung thực từ tuyến đầu.
  - Khi chi phí giám sát 100% hành vi của nhân viên là bất khả thi hoặc quá tốn kém.
- **Ngoại lệ:**
  - Các quy tắc an toàn lao động tối thiểu, bảo mật thông tin cốt lõi hoặc tuân thủ pháp luật bắt buộc — nơi chế tài nghiêm minh là ranh giới bảo vệ bắt buộc.
  - Tình huống khẩn cấp ngắn hạn cần lập lại trật tự tức thời trước khi giải thích nguyên nhân sâu xa.

### 3. Mức bất định & Rủi ro diễn giải sai
- **Mức bất định:** Thấp - Trung bình. Các phân tích tổng hợp của Lý thuyết Tự quyết (Deci, Koestner & Ryan, 1999) nhất quán chỉ ra rằng kiểm soát cưỡng ép kéo dài làm suy giảm động lực nội tại, dù tốc độ bộc lộ sự suy giảm phụ thuộc vào điều kiện thị trường lao động và khả năng luân chuyển của nhân sự.
- **Rủi ro diễn giải sai:**
  - Nhầm lẫn việc tránh cưỡng ép độc đoán với việc xóa bỏ kỷ luật, tiêu chuẩn đầu ra và trách nhiệm giải trình.
  - Cho rằng mọi nhân sự đều tự giác như nhau mà không cần khung đánh giá minh bạch kèm theo.

### 4. Nguồn truy nguyên & Đối chiếu Đông - Tây
- **Nguồn truy nguyên:** Mô hình ba cấp độ thay đổi thái độ của Herbert Kelman (1958) và Lý thuyết Tự quyết (Self-Determination Theory) của Deci & Ryan (1999).
- **Đối chiếu cổ điển `[Nguồn cổ điển]`:** *Luận Ngữ* (*Vi Chính*) chỉ rõ: dùng mệnh lệnh và hình phạt đơn thuần thì người dưới chỉ tìm cách tránh tội mà không có lòng tự trọng (*dân miễn nhi vô sỉ*); kết hợp chuẩn mực minh bạch với sự thuyết phục và tôn trọng mới tạo ra sự tự giác bền vững (*hữu sỉ thả cách*).
""",
    },
}


def load_head_units(repo_root: Path = REPO_ROOT) -> dict[str, bytes]:
    """Load raw YAML bytes of all ``knowledge/units/**/*.yaml`` from ``HEAD``."""
    tar_bytes = subprocess.check_output(
        ["git", "archive", "HEAD", "knowledge/units"],
        cwd=str(repo_root),
    )
    head_raw: dict[str, bytes] = {}
    with tarfile.open(fileobj=io.BytesIO(tar_bytes)) as archive:
        for member in archive.getmembers():
            if member.isfile() and member.name.endswith(".yaml"):
                extracted = archive.extractfile(member)
                if extracted is not None:
                    head_raw[member.name] = extracted.read()
    return head_raw


def is_placeholder_reference(ref: str) -> bool:
    """Return True if ``ref`` is a placeholder requirement ID such as ``EV-REQ-0001-01``."""
    cleaned = str(ref).strip()
    return cleaned.startswith("EV-REQ-")


def audit_evidence_truthfulness(unit_data: dict[str, Any]) -> list[str]:
    """Verify that evidence level is honest and not inflated by placeholders."""
    issues: list[str] = []
    ev = unit_data.get("evidence") or {}
    level = str(ev.get("level", "")).strip()
    refs = [str(r).strip() for r in (ev.get("references") or []) if str(r).strip()]
    if level in ("supported", "strong"):
        if not refs:
            issues.append(f"{unit_data.get('id')}: level='{level}' has empty references")
        elif all(is_placeholder_reference(r) for r in refs):
            issues.append(
                f"{unit_data.get('id')}: level='{level}' relies solely on placeholder {refs}"
            )
    return issues


def audit_pilot_unit_quality(unit_data: dict[str, Any]) -> list[str]:
    """Audit a pilot unit for banned boilerplate phrases, required sections, and source classes."""
    issues: list[str] = []
    unit_id = str(unit_data.get("id", "UNKNOWN"))
    content = str(unit_data.get("content") or "")
    if len(content.strip()) < 200:
        issues.append(f"{unit_id}: pilot content is missing or too short")

    lower_content = content.lower()
    for phrase in BANNED_BOILERPLATE_PHRASES:
        if phrase.lower() in lower_content:
            issues.append(f"{unit_id}: contains banned boilerplate phrase '{phrase}'")

    for section in REQUIRED_PILOT_SECTIONS:
        if section.lower() not in lower_content:
            issues.append(f"{unit_id}: missing required pilot section '{section}'")

    issues.extend(audit_evidence_truthfulness(unit_data))
    refs = [str(r) for r in (unit_data.get("evidence", {}).get("references") or [])]
    if not refs:
        issues.append(f"{unit_id}: pilot unit must have classified references")
    else:
        for ref in refs:
            if not any(tag in ref for tag in SOURCE_CLASS_TAGS):
                issues.append(
                    f"{unit_id}: reference missing source classification tag: '{ref[:60]}'"
                )
    return issues


def apply_content_without_metadata_mutation(
    original_data: dict[str, Any],
    new_content: str,
) -> dict[str, Any]:
    """Update only ``content`` without mutating ``status``, ``evidence``, or ``version``."""
    updated = dict(original_data)
    updated["content"] = new_content
    assert updated.get("status") == original_data.get("status")
    assert updated.get("version") == original_data.get("version")
    assert updated.get("evidence") == original_data.get("evidence")
    return updated


def dump_unit_yaml(data: dict[str, Any]) -> str:
    """Deterministically serialize a knowledge unit mapping to UTF-8 YAML."""
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=100)


def execute_controlled_recovery(
    repo_root: Path = REPO_ROOT,
    dry_run: bool = False,
    manifest_path: Path | None = None,
) -> dict[str, Any]:
    """Inventory the 352 modified units, roll back mass boilerplate, and apply the 12-unit pilot."""
    head_raw_map = load_head_units(repo_root)
    diff_files = sorted(
        subprocess.check_output(
            ["git", "diff", "--name-only", "HEAD", "--", "knowledge/units/"],
            cwd=str(repo_root),
            text=True,
        ).splitlines()
    )
    # If already recovered, inspect all 352 non-Wave1 units by comparing against commit 27a34bc
    wave1_files = set(
        subprocess.check_output(
            ["git", "show", "--name-only", "--pretty=format:", "HEAD", "--", "knowledge/units/"],
            cwd=str(repo_root),
            text=True,
        ).splitlines()
    )
    target_352_files = sorted(f for f in head_raw_map if f not in wave1_files)

    existing_inventory_by_id: dict[str, dict[str, Any]] = {}
    if manifest_path is not None and manifest_path.exists():
        try:
            prev = json.loads(manifest_path.read_text(encoding="utf-8"))
            for item in prev.get("inventory", []):
                if item.get("boilerplate_generated_in_uncontrolled_batch"):
                    existing_inventory_by_id[str(item.get("id"))] = item
        except (OSError, json.JSONDecodeError, KeyError, TypeError):
            existing_inventory_by_id = {}

    inventory_items: list[dict[str, Any]] = []
    changed_manifest: list[dict[str, Any]] = []

    for rel_path in target_352_files:
        file_path = repo_root / rel_path
        head_bytes = head_raw_map[rel_path]
        head_data = yaml.load(head_bytes.decode("utf-8"), Loader=YAML_LOADER)
        wt_text = file_path.read_text(encoding="utf-8")
        wt_data = yaml.load(wt_text, Loader=YAML_LOADER)

        unit_id = str(head_data["id"])
        head_ev = head_data.get("evidence") or {}
        wt_ev = wt_data.get("evidence") or {}
        wt_content = str(wt_data.get("content") or "")
        had_boilerplate = any(
            phrase.lower() in wt_content.lower() for phrase in BANNED_BOILERPLATE_PHRASES[:6]
        )

        if unit_id in existing_inventory_by_id:
            inventory_items.append(existing_inventory_by_id[unit_id])
        else:
            inventory_items.append(
                {
                    "path": rel_path,
                    "id": unit_id,
                    "type": head_data.get("type"),
                    "status_before": head_data.get("status"),
                    "status_after_uncontrolled_batch": wt_data.get("status"),
                    "version_before": head_data.get("version"),
                    "version_after_uncontrolled_batch": wt_data.get("version"),
                    "evidence_level_before": head_ev.get("level"),
                    "evidence_level_after_uncontrolled_batch": wt_ev.get("level"),
                    "evidence_refs_before": list(head_ev.get("references") or []),
                    "evidence_refs_after_uncontrolled_batch": list(wt_ev.get("references") or []),
                    "boilerplate_generated_in_uncontrolled_batch": had_boilerplate,
                    "in_pilot_batch": unit_id in PILOT_UNIT_SPECS,
                }
            )

        if unit_id in PILOT_UNIT_SPECS:
            pilot_spec = PILOT_UNIT_SPECS[unit_id]
            new_data = dict(head_data)
            # Preserve status and version from HEAD (never self-approve or self-freeze)
            new_data["status"] = head_data["status"]
            new_data["version"] = head_data["version"]
            new_data["evidence"] = dict(pilot_spec["evidence"])
            new_data["content"] = pilot_spec["content"]
            new_bytes = dump_unit_yaml(new_data).encode("utf-8")
            action = "pilot_upgrade"
        else:
            # Start from exact HEAD state to roll back mass boilerplate content and version bumps
            head_refs = [str(r).strip() for r in (head_ev.get("references") or []) if str(r).strip()]
            head_level = str(head_ev.get("level", "")).strip()
            if head_level in ("supported", "strong") and (
                not head_refs or all(is_placeholder_reference(r) for r in head_refs)
            ):
                # Remediate placeholder-only evidence inflation honestly to provisional
                head_text = head_bytes.decode("utf-8")
                patched_text = re.sub(
                    r"^(\s*level:\s*)(?:supported|strong)(\r?\n)",
                    r"\1provisional\2",
                    head_text,
                    count=1,
                    flags=re.MULTILINE,
                )
                new_bytes = patched_text.encode("utf-8")
                action = "revert_boilerplate_and_downgrade_placeholder_evidence"
            else:
                new_bytes = head_bytes
                action = "revert_to_head"

        if file_path.read_bytes() != new_bytes:
            changed_manifest.append(
                {
                    "path": rel_path,
                    "id": unit_id,
                    "action": action,
                    "status": head_data.get("status"),
                }
            )
            if not dry_run:
                file_path.write_bytes(new_bytes)

    summary = {
        "total_target_units": len(target_352_files),
        "initial_diff_count": len(diff_files),
        "frozen_count": sum(1 for item in inventory_items if item["status_before"] == "frozen"),
        "draft_count": sum(1 for item in inventory_items if item["status_before"] == "draft"),
        "pilot_unit_ids": sorted(PILOT_UNIT_SPECS.keys()),
        "pilot_count": len(PILOT_UNIT_SPECS),
        "dry_run": dry_run,
        "files_updated_count": len(changed_manifest),
        "changed_files": changed_manifest,
        "inventory": inventory_items,
    }

    if manifest_path is not None:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return summary


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Compute recovery/pilot changes and manifest without modifying files on disk.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help="Optional path to write JSON manifest and 352-unit inventory.",
    )
    parser.add_argument(
        "--audit-only",
        action="store_true",
        help="Audit pilot units and repository evidence truthfulness without writing.",
    )
    args = parser.parse_args(argv)

    if args.audit_only:
        issues: list[str] = []
        for path in sorted((REPO_ROOT / "knowledge" / "units").rglob("*.yaml")):
            data = yaml.load(path.read_text(encoding="utf-8"), Loader=YAML_LOADER)
            issues.extend(audit_evidence_truthfulness(data))
            if data.get("id") in PILOT_UNIT_SPECS:
                issues.extend(audit_pilot_unit_quality(data))
        if issues:
            for issue in issues:
                print(f"- {issue}", file=sys.stderr)
            return 1
        print("Audit passed: all pilot units and evidence levels are valid.")
        return 0

    summary = execute_controlled_recovery(
        repo_root=REPO_ROOT,
        dry_run=args.dry_run,
        manifest_path=args.manifest,
    )
    print(
        json.dumps(
            {
                "total_target_units": summary["total_target_units"],
                "frozen_count": summary["frozen_count"],
                "draft_count": summary["draft_count"],
                "pilot_count": summary["pilot_count"],
                "dry_run": summary["dry_run"],
                "files_updated_count": summary["files_updated_count"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())