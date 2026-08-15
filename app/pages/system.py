import streamlit as st
from app.services.engine_adapter import EngineAdapter
from app.components.ui_blocks import render_metric
from app.utils.localization import t_type, t_domain

st.title("Hệ thống")
st.markdown("Tình trạng Nhân Thuật")

adapter = EngineAdapter()

col1, col2, col3, col4 = st.columns(4)
with col1:
    render_metric("Kho tri thức", f"{adapter.get_total_units()}+ tri thức")
with col2:
    domains = adapter.get_all_domains()
    render_metric("Lĩnh vực", f"{len(domains)}+")
with col3:
    render_metric("Lăng kính triết học", "5")
    st.caption("Hùng Biện, Nho, Pháp, Đạo, Tuân Tử")
with col4:
    types = adapter.get_all_types()
    render_metric("Loại tri thức", f"{len(types)}")

st.markdown("---")

col_a, col_b = st.columns(2)
with col_a:
    render_metric("Runtime", "Đang hoạt động")
    st.caption("KnowledgeEngine + Resolver + Graph + Evaluator")
with col_b:
    synth_status = "Đã cấu hình (LLM)" if adapter.synthesizer.provider_configured else "Fallback deterministic"
    render_metric("LLM synthesis", synth_status)
    st.caption("Capability NHANTHUAT-CAP-002 — EPIC 5")

st.markdown("---")

with st.expander("Chi tiết kỹ thuật"):
    st.markdown("""
    **KnowledgeEngine**: Động cơ lõi quản lý dữ liệu, nạp và xác thực cấu trúc YAML.
    
    **Resolver**: Thành phần chịu trách nhiệm tìm kiếm, truy xuất và liên kết tri thức dựa trên truy vấn.
    
    **Graph**: Đồ thị liên kết các điểm tri thức, hiển thị quan hệ nhân quả và phụ thuộc.
    
    **Prompt Builder**: Trình tạo ngữ cảnh, đóng gói dữ liệu tri thức để chuyển cho LLM tổng hợp.
    
    **Evaluator**: Thành phần đánh giá mức độ phù hợp và nhận diện rủi ro sai lệch của hệ thống.
    """)

