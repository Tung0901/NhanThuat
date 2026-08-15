import time

import streamlit as st

from app.components.ui_blocks import render_unit_card
from app.services.engine_adapter import EngineAdapter
from app.utils.localization import t_domain

st.title("Hỏi Nhân Thuật")
st.markdown("Đặt một câu hỏi hoặc mô tả một tình huống. Nhân Thuật sẽ tìm các quy luật, hiện tượng hành vi, mô hình và nguyên tắc liên quan.")

adapter = EngineAdapter()

query = st.text_input("Câu hỏi", placeholder="Ví dụ: Tại sao khách hàng biết sản phẩm phù hợp nhưng vẫn trì hoãn quyết định mua?", label_visibility="collapsed")

if query:
    with st.spinner("Đang phân tích với Nhân Thuật..."):
        time.sleep(0.5) # Slight delay for UX
        
        # 1. Resolve Query (real resolver scores)
        scored_units = adapter.resolve_scored(query, limit=5)
        top_units = [unit for _, unit in scored_units]
        scores = {unit.id: score for score, unit in scored_units}
        
        if not top_units:
            st.warning("Không tìm thấy tri thức liên quan. Vui lòng thử cách diễn đạt khác.")
            st.stop()
            
        # 2. Build Context
        context_str = adapter.build_context(top_units)
        
        # 3. Evaluate Content
        eval_result = adapter.evaluate_content(query, top_units)
        
        # 4. Synthesize (LLM if configured, deterministic fallback)
        synthesis = adapter.synthesize(query, top_units)

    # 5. Present Results
    st.markdown("### Kết luận")
    if synthesis.get("warning"):
        st.caption(synthesis["warning"])
    st.write(synthesis["synthesis"])
    
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Dòng truy xuất tri thức")
        st.caption("Câu hỏi → Tìm tri thức liên quan → Kiểm tra tri thức nền → Xây dựng bối cảnh → Đánh giá rủi ro")
        for unit in top_units:
            score = scores.get(unit.id, 0)
            render_unit_card(unit, score=score)
            
        st.markdown("### Trích dẫn")
        for citation in synthesis.get("citations", []):
            st.markdown(f"- **{citation['title']}** — `{citation['id']}` ({t_domain(citation['domain'])})")
            
        audit = synthesis.get("audit", {})
        st.caption(f"Kiểm tra: `{audit.get('correlation_id', '')}` | Nhà cung cấp: {audit.get('provider')} | Mô hình: {audit.get('model') or '—'} | {audit.get('latency_ms', 0)} ms")
            
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

