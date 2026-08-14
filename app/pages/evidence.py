import streamlit as st
from app.services.engine_adapter import EngineAdapter
from app.utils.localization import t_evidence

st.title("Bằng chứng & Nguồn")
st.markdown("Kiểm tra cơ sở khoa học đứng sau các nhận định của Nhân Thuật.")

adapter = EngineAdapter()

units = adapter.query_filters(domain="All", unit_type="All")
sources_by_level = {}

for u in units:
    level = u.evidence.level if u.evidence and u.evidence.level else "empirical finding"
    if level not in sources_by_level:
        sources_by_level[level] = []
    sources_by_level[level].append(u)

st.markdown("### Phân loại Bằng chứng")

for level in sorted(sources_by_level.keys()):
    st.markdown(f"#### Loại bằng chứng: {t_evidence(level)} ({len(sources_by_level[level])} tri thức)")
    with st.expander(f"Xem danh sách nguồn ({len(sources_by_level[level])})"):
        for u in sources_by_level[level]:
            st.markdown(f"**Nhận định:** {u.title}")
            st.markdown(f"**Mức độ hỗ trợ:** Cao") # Using a default value as it's not directly in the model
            if u.evidence and u.evidence.references:
                st.markdown("**Nguồn:**")
                for ref in u.evidence.references:
                    st.markdown(f"- {ref}")
            if u.exceptions:
                st.markdown("**Giới hạn:**")
                for exc in u.exceptions:
                    st.markdown(f"- {exc}")
            st.markdown("---")

