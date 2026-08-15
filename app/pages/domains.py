import streamlit as st

from app.components.ui_blocks import render_metric, render_unit_card
from app.services.engine_adapter import EngineAdapter
from app.utils.localization import t_domain, t_domain_desc, t_type

st.title("Lĩnh vực")
st.markdown("Khám phá các lĩnh vực tri thức mà Nhân Thuật nghiên cứu và áp dụng.")

adapter = EngineAdapter()
domains = adapter.get_all_domains()

if not domains:
    st.info("Không tìm thấy lĩnh vực nào.")
else:
    selected_domain = st.selectbox("Chọn Lĩnh vực", domains, format_func=t_domain)
    st.markdown("---")
    
    if selected_domain:
        st.markdown(f"## {t_domain(selected_domain)}")
        st.caption(f"Mã lĩnh vực: `{selected_domain}`")
        
        st.markdown("### Lĩnh vực này nghiên cứu vấn đề gì?")
        st.write(t_domain_desc(selected_domain))
        
        units = adapter.query_filters(domain=selected_domain, unit_type="All")
        
        st.markdown("### Thống kê")
        col1, col2 = st.columns(2)
        with col1:
            render_metric("Tổng số tri thức", str(len(units)))
        
        units_by_type = {}
        for u in units:
            if u.type not in units_by_type:
                units_by_type[u.type] = []
            units_by_type[u.type].append(u)
            
        with col2:
            render_metric("Các loại tri thức", str(len(units_by_type)))
        
        st.markdown("### Tri thức tiêu biểu")
        for u_type in sorted(units_by_type.keys()):
            st.markdown(f"#### {t_type(u_type).upper()} ({len(units_by_type[u_type])})")
            for u in units_by_type[u_type][:3]: # show a few as typical
                render_unit_card(u)
            if len(units_by_type[u_type]) > 3:
                with st.expander(f"Xem tất cả {len(units_by_type[u_type])} {t_type(u_type).lower()}"):
                    for u in units_by_type[u_type][3:]:
                        render_unit_card(u)
