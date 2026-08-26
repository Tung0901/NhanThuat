import os
from datetime import datetime

import google.generativeai as genai
import streamlit as st
from dotenv import load_dotenv
from streamlit_option_menu import option_menu

# --- 1. CONFIG & ENV ---
load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

st.set_page_config(page_title="Nhân Sinh OS", page_icon="🏛️", layout="wide", initial_sidebar_state="expanded")

# --- 2. SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Chào anh/chị. Hôm nay có câu chuyện gì vui hay một chút bận lòng nào trong công việc, gia đình... anh/chị cứ chia sẻ, chúng ta cùng đàm đạo nhé."}]

# --- 3. CSS TÙY CHỈNH (LIGHT MODE & HERO BANNER SANG TRỌNG) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    * { font-family: 'Plus Jakarta Sans', sans-serif; }
    #MainMenu, footer, header { visibility: hidden; }
    
    .stApp { 
        background: linear-gradient(180deg, #FFFFFF 0%, #F4F8FB 50%, #EBF3FA 100%) !important; 
        color: #202124 !important; 
        background-attachment: fixed;
    }
    
    section[data-testid="stSidebar"] { 
        background-color: #FFFFFF !important; 
        border-right: 1px solid #E2E8F0 !important; 
    }
    section[data-testid="stSidebar"] * { color: #334155 !important; }
    
    /* Hero Banner Tinh Tế, Sang Trọng */
    .hero-box { 
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%); 
        border: 1px solid #334155; 
        border-radius: 16px; 
        padding: 24px 30px; 
        margin-bottom: 20px; 
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.1); 
    }
    .hero-title { 
        font-size: 26px; 
        font-weight: 800; 
        letter-spacing: -0.02em; 
        color: #F8FAFC; 
        margin-bottom: 6px; 
    }
    .hero-sub { 
        color: #94A3B8; 
        font-size: 13px; 
        font-weight: 600; 
        text-transform: uppercase; 
        letter-spacing: 0.05em; 
    }
    
    [data-testid="stChatInput"] { 
        background-color: #FFFFFF !important; 
        border: 1px solid #CBD5E1 !important; 
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.08) !important; 
        border-radius: 30px !important;
        padding: 4px 12px !important;
        margin-bottom: 10px !important;
    }
    [data-testid="stChatInput"] textarea { color: #1E293B !important; font-size: 15px !important; }
    
    [data-testid="stChatMessageContent"] { 
        color: #1E293B !important; 
        background-color: #FFFFFF !important; 
        border: 1px solid #E2E8F0; 
        border-radius: 20px; 
        padding: 18px 22px; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.03); 
    }
    [data-testid="stChatMessageContent"] * { color: #1E293B !important; }
    
    /* Avatar & Nút bấm tinh tế */
    [data-testid="chatAvatarIcon-assistant"] svg, [data-testid="chatAvatarIcon-user"] svg { display: none !important; }
    [data-testid="chatAvatarIcon-assistant"]::after { content: "💡"; font-size: 16px; }
    [data-testid="chatAvatarIcon-user"]::after { content: "👤"; font-size: 16px; }
    [data-testid="chatAvatarIcon-assistant"] { background-color: #E8F0FE !important; display: flex; align-items: center; justify-content: center; }
    [data-testid="chatAvatarIcon-user"] { background-color: #1A73E8 !important; display: flex; align-items: center; justify-content: center; }
    
    @media (max-width: 768px) {
        .stApp { padding: 0px !important; }
        [data-testid="stChatInput"] { bottom: 15px !important; }
    }
    
    div[data-testid="stButton"] > button { background-color: #1A73E8 !important; color: #FFFFFF !important; font-weight: 600 !important; border-radius: 20px !important; padding: 8px 20px !important; border: none !important; transition: all 0.2s ease !important; }
    div[data-testid="stButton"] > button:hover { background-color: #1557B0 !important; box-shadow: 0 4px 12px rgba(26, 115, 232, 0.3) !important; }
</style>
""", unsafe_allow_html=True)

# --- 4. KHO TRI THỨC ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KNOWLEDGE_DIR = os.path.join(BASE_DIR, "docs", "knowledge")
THUC_CHIEN_PATH = os.path.join(KNOWLEDGE_DIR, "10_THUC_CHIEN_NHAN_SINH.md")
os.makedirs(KNOWLEDGE_DIR, exist_ok=True)
if not os.path.exists(THUC_CHIEN_PATH):
    with open(THUC_CHIEN_PATH, "w", encoding="utf-8") as f:
        f.write("# 📂 KHO TÀNG THỰC CHIẾN NHÂN SINH\n\n*Hồ sơ lưu trữ các ca xử lý ứng xử & chiến lược.*\n\n---\n")

BOOKS = [
    {"title": "Nho Gia & Thu Phục", "path": os.path.join(KNOWLEDGE_DIR, "02_TU_THU_KNOWLEDGE_PACK.md")},
    {"title": "Đạo Gia & Tĩnh Tâm", "path": os.path.join(KNOWLEDGE_DIR, "04_TRANG_TU_KNOWLEDGE_PACK.md")},
    {"title": "Chủ Nghĩa Khắc Kỷ", "path": os.path.join(KNOWLEDGE_DIR, "07_CHU_NGHIA_KHAC_KY.md")},
    {"title": "Nhân Thuật & Ứng Xử", "path": os.path.join(KNOWLEDGE_DIR, "06_NHAN_THUAT_UNG_XU.md")},
    {"title": "Pháp Gia & Thống Trị", "path": os.path.join(KNOWLEDGE_DIR, "03_HAN_PHI_TU_KNOWLEDGE_PACK.md")},
    {"title": "Tuân Tử & Quản Trị", "path": os.path.join(KNOWLEDGE_DIR, "05_TUAN_TU_KNOWLEDGE_PACK.md")},
    {"title": "Thuật Hùng Biện", "path": os.path.join(KNOWLEDGE_DIR, "01_THUAT_HUNG_BIEN.md")},
    {"title": "Binh Pháp Tôn Tử", "path": os.path.join(KNOWLEDGE_DIR, "08_BINH_PHAP_TON_TU.md")},
    {"title": "Tâm Lý Học Hành Vi", "path": os.path.join(KNOWLEDGE_DIR, "09_TAM_LY_HOC_HANH_VI.md")},
    {"title": "⭐ Kho Thực Chiến", "path": THUC_CHIEN_PATH},
]

# --- 5. SIDEBAR MENU ---
with st.sidebar:
    st.markdown("""
        <div style='padding: 10px 0;'>
            <h1 style='color: #1A73E8; font-size: 22px; font-weight: 800; letter-spacing: -0.02em; margin-bottom: 2px; text-transform: uppercase;'>
                🏛️ NHÂN SINH OS
            </h1>
            <p style='color: #5F6368; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; margin-top: 0;'>
                Executive & Life Wisdom
            </p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    selected = option_menu(
        menu_title=None,
        options=["THAM MƯU TÌNH HUỐNG", "THƯ VIỆN TRI THỨC"],
        icons=["chat-square-dots-fill", "book-half"],
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#1A73E8", "font-size": "18px"},
            "nav-link": {"font-size": "14px", "text-align": "left", "margin": "5px 0", "color": "#374151"},
            "nav-link-selected": {"background-color": "#E8F0FE", "color": "#1A73E8", "font-weight": "700"},
        }
    )

# --- 6. HERO BANNER CHUẨN XÁC ---
st.markdown("""
<div class="hero-box">
    <div class="hero-title">CỐ VẤN ỨNG XỬ & CHIẾN LƯỢC NHÂN SINH</div>
    <div class="hero-sub">Nghệ thuật đối nhân xử thế, thấu hiểu tâm lý & giải quyết vấn đề đa chiều.</div>
</div>
""", unsafe_allow_html=True)

# --- 7. MAIN CONTENT ---
if selected == "THAM MƯU TÌNH HUỐNG":
    if not GEMINI_API_KEY and not DEEPSEEK_API_KEY:
        st.error("⚠️ Chưa cấu hình biến môi trường DEEPSEEK_API_KEY hoặc GEMINI_API_KEY trong file .env")
    else:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"], unsafe_allow_html=True)
                
        if len(st.session_state.messages) > 1:
            col_space, col_btn = st.columns([4, 1.5])
            with col_btn:
                if st.button("💾 Lưu Ca Này Vào Kho"):
                    last_user = next((m["content"] for m in reversed(st.session_state.messages) if m["role"] == "user"), "")
                    last_ai = next((m["content"] for m in reversed(st.session_state.messages) if m["role"] == "assistant"), "")
                    now_str = datetime.now().astimezone().strftime("%d/%m/%Y %H:%M:%S")
                    record = f"\n\n## 🕒 Ca xử lý: {now_str}\n\n**TÌNH HUỐNG:**\n> {last_user}\n\n**PHÁN QUYẾT:**\n{last_ai}\n\n---\n"
                    with open(THUC_CHIEN_PATH, "a", encoding="utf-8") as f:
                        f.write(record)
                    st.toast("✅ Đã lưu vào Kho Thực Chiến Nhân Sinh!")

        if prompt_text := st.chat_input("Nhập câu chuyện hoặc tình huống anh/chị đang băn khoăn..."):
            st.session_state.messages.append({"role": "user", "content": prompt_text})
            with st.chat_message("user"):
                st.markdown(prompt_text, unsafe_allow_html=True)
                
            with st.chat_message("assistant"), st.spinner("Đang thấu cảm & thiết lập phương pháp..."):
                    sys_prompt = f"""Bạn là một Cố Vấn Chiến Lược & Nhân Sinh Cấp Cao, hiện thân cho trí tuệ Binh pháp, Nhân thuật và phong cách sống thâm trầm, từng trải của người dùng.

                    TÌNH HUỐNG HIỆN TẠI CỦA NGƯỜI DÙNG: {prompt_text}

                    CHỈ ĐẠO CỐT LÕI VỀ TƯ DUY & VĂN PHONG Á ĐÔNG:
                    1. **Tuyệt đối không ấn định mốc thời gian cứng nhắc** (Không dùng 24h, 3 ngày, 1 tuần...). Hãy chia chiến lược theo **Trình tự Binh thế** (Thủ thế -> Lập thế -> Định cục).
                    2. **Văn phong Á Đông sâu sắc:** Dùng trí tuệ nhân thuật, lấy tĩnh chế động, hòa mà không tan. Ngôn từ đầm, mộc mạc, thấu hiểu quy luật nhân quả và tâm lý con người.
                    3. **Thực chiến & Ranh giới:** Phân tích đúng bản chất thực tế, có ranh giới chịu đựng rõ ràng và kịch bản ứng phó 2 chiều sắc bén.
                    4. **Trình bày thoáng đãng:** Tuyệt đối không lạm dụng bôi đen/in đậm vô tội vạ.
                    5. **Xưng hô:** Tự nhiên, chân thành: gọi người dùng là "anh/chị", xưng "tôi" hoặc "em".

                    TRẢ LỜI BẰNG MARKDOWN THEO ĐÚNG CÁC PHẦN SAU:
                    
                    ### 🌊 1. PHÂN TÍCH BẢN CHẤT & DIỄN BIẾN TÂM LÝ
                    - **Chỉ số Tín nhiệm (Trust Index):** [X/10]
                    - **Chỉ số Sức ép cảm xúc (Emotional Heat):** [X/10]
                    - **Bản chất vấn đề & Quy luật chi phối:** [Phân tích thấu đáo thực trạng, động cơ ngầm của các bên dưới lăng kính Binh pháp và Nhân thuật Á Đông].
                    
                    ### ⚙️ 2. TRÌNH TỰ HÀNH ĐỘNG THỰC CHIẾN (THEO THỜI & THẾ)
                    - **Giai đoạn 1 - Quyền Biến & Thủ Thế:** [Kiểm soát cảm xúc, thu thập dữ kiện, tạo khoảng lặng chiến lược để ngăn chặn thiệt hại tức thì. Rủi ro có thể gặp & Cách chốt chặn].
                    - **Giai đoạn 2 - Lập Thế & Cân Bằng:** [Hành động trọng tâm xoáy vào gốc rễ vấn đề, dùng sự chân thành kết hợp với uy lực ngầm để buộc đối phương đi vào quỹ đạo. Ranh giới giới hạn (Stop-loss)].
                    - **Giai đoạn 3 - Định Cục & Thu Phục:** [Thiết lập lại trật tự mới, tạo đường lui danh dự cho các bên nhưng bảo vệ tuyệt đối lợi ích và nguyên tắc cốt lõi].
                    
                    ### 💬 3. KỊCH BẢN ỨNG XỬ THỰC TẾ (ĐỐI ĐÁP 2 CHIỀU)
                    - **Bối cảnh & Tông giọng:** [Thái độ, không gian và thời điểm phù hợp để cất lời]
                    - **Thông điệp chủ đạo:** [Lời thoại cụ thể, vừa thấu tình vừa đạt lý]
                    - **Kịch bản phản đòn:** [Nếu đối phương cố tình lấn lướt hoặc không hợp tác -> Câu chốt hạ để giữ vững vị thế]
                    
                    <details>
                    <summary><b>📝 Dự phòng phương án tồi tệ nhất (Bấm để xem)</b></summary>
                    [Phương án rút lui an toàn, bảo toàn đại cuộc nếu mọi thương lượng đổ vỡ].
                    </details>
                    """
                    success = False
                    last_err = ""
                    
                    if DEEPSEEK_API_KEY:
                        import requests
                        try:
                            resp = requests.post(
                                "https://api.deepseek.com/chat/completions",
                                headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
                                json={
                                    "model": "deepseek-chat",
                                    "messages": [{"role": "user", "content": sys_prompt}],
                                    "temperature": 0.4
                                },
                                timeout=60
                            )
                            resp.raise_for_status()
                            text = resp.json()["choices"][0]["message"]["content"]
                            if text:
                                st.markdown(text, unsafe_allow_html=True)
                                st.session_state.messages.append({"role": "assistant", "content": text})
                                success = True
                        except Exception as e:
                            last_err = f"Deepseek Error: {str(e)}"
                            
                    if not success and GEMINI_API_KEY:
                        candidate_models = ['gemini-3.6-flash', 'gemini-3.5-flash', 'gemini-3-flash']
                        for model_name in candidate_models:
                            try:
                                model = genai.GenerativeModel(model_name)
                                res = model.generate_content(sys_prompt)
                                if res and res.text:
                                    st.markdown(res.text, unsafe_allow_html=True)
                                    st.session_state.messages.append({"role": "assistant", "content": res.text})
                                    success = True
                                    break
                            except Exception as e:  # noqa: BLE001 - try next candidate model
                                last_err = f"Gemini Error: {str(e)}"
                                continue
                    if not success:
                        st.error(f"Lỗi hệ thống: {last_err}")

else:
    st.markdown("### 📚 Hệ Sinh Thái Tri Thức Nhân Sinh")
    book_titles = [b["title"] for b in BOOKS]
    selected_title = st.selectbox("Chọn tài liệu:", book_titles)
    selected_book = next(b for b in BOOKS if b["title"] == selected_title)
    
    if os.path.exists(selected_book["path"]):
        with open(selected_book["path"], "r", encoding="utf-8") as f:
            content = f.read()
        st.download_button("📥 Tải File", data=content, file_name=os.path.basename(selected_book["path"]))
        st.markdown('<div style="background-color:#FFFFFF; padding:20px; border-radius:12px; border:1px solid #E5E7EB; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">', unsafe_allow_html=True)
        st.markdown(content)
        st.markdown('</div>', unsafe_allow_html=True)
