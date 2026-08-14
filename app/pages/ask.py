import streamlit as st
import time
from app.services.engine_adapter import EngineAdapter
from app.components.ui_blocks import render_unit_card, render_tag_pill

st.title("Hỏi Nhân Thuật")
st.markdown("Đặt một câu hỏi hoặc mô tả một tình huống. Nhân Thuật sẽ tìm các quy luật, hiện tượng hành vi, mô hình và nguyên tắc liên quan.")

adapter = EngineAdapter()

query = st.text_input("Query", placeholder="Ví dụ: Tại sao khách hàng biết sản phẩm phù hợp nhưng vẫn trì hoãn quyết định mua?", label_visibility="collapsed")

if query:
    with st.spinner("Đang phân tích với Nhân Thuật..."):
        time.sleep(0.5) # Slight delay for UX
        
        # 1. Resolve Query
        top_units = adapter.resolve_query(query, limit=5)
        
        if not top_units:
            st.warning("Không tìm thấy tri thức liên quan. Vui lòng thử cách diễn đạt khác.")
            st.stop()
            
        # 2. Build Context
        context_str = adapter.build_context(top_units)
        
        # 3. Evaluate Content
        eval_result = adapter.evaluate_content(query, top_units)

    # 4. Present Results
    st.markdown("### Kết luận")
    st.info("*(Synthesis is in mock mode for v0.1. Capability NHANTHUAT-CAP-002 (Philosophical Routing and Reasoning) is PLANNED; LLM integration lands in EPIC 5. Below is the deterministic knowledge retrieval flow.)*")
    st.write(f"Dựa trên **{len(top_units)}** tri thức cốt lõi được truy xuất, hành vi này có thể được lý giải qua sự tương tác giữa {', '.join([u.title.lower() for u in top_units[:2]])}.")
    
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Dòng truy xuất tri thức")
        st.caption("Câu hỏi → Tìm tri thức liên quan → Kiểm tra tri thức nền → Xây dựng bối cảnh → Đánh giá rủi ro")
        st.caption("PLANNED: score từ ranker chính thức (EPIC 5)")
        for i, unit in enumerate(top_units):
            score = round(0.95 - (i * 0.1), 2)
            render_unit_card(unit, score=score)
            
    with col2:
        st.markdown("### Đánh giá rủi ro")
        
        score_val = eval_result.get("score", 0)
        color = "green" if score_val > 80 else "orange" if score_val > 50 else "red"
        st.markdown(f"<div style='font-size:2rem; color:{color}; font-weight:bold;'>Độ phù hợp: {score_val}%</div>", unsafe_allow_html=True)
        
        if eval_result.get("aligned_units"):
            st.markdown("**Đã đối chiếu:**")
            for au in eval_result["aligned_units"]:
                st.markdown(f"- {au}")
                
        if eval_result.get("warnings"):
            st.markdown("**Cảnh báo:**")
            for w in eval_result["warnings"]:
                st.markdown(f"- <span style='color:#787774;'>{w}</span>", unsafe_allow_html=True)
                
        if eval_result.get("violations"):
            st.markdown("**Rủi ro kích hoạt:**")
            for v in eval_result["violations"]:
                st.markdown(f"- <span style='color:#9F2F2D;'>{v}</span>", unsafe_allow_html=True)

