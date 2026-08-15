import sys
from pathlib import Path
root_path = Path(__file__).resolve().parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))
src_path = root_path / 'src'
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import streamlit as st

from app.components.ui_blocks import render_metric, render_unit_card
from app.services.engine_adapter import EngineAdapter
from app.utils.localization import t_domain, t_type

st.title("Khám phá Tri thức")
st.markdown("Khám phá toàn bộ kho tri thức của Nhân Thuật.")

adapter = EngineAdapter()

all_domains = adapter.get_all_domains()
all_types = adapter.get_all_types()

col1, col2, col3 = st.columns(3)

with col1:
    domain_filter = st.selectbox("Lĩnh vực ứng dụng", ["All"] + all_domains, format_func=t_domain)
with col2:
    type_filter = st.selectbox("Loại tri thức", ["All"] + all_types, format_func=t_type)
with col3:
    st.write("")
    st.write("")
    
filtered_units = adapter.query_filters(
    domain=None if domain_filter == "All" else domain_filter,
    unit_type=None if type_filter == "All" else type_filter
)

st.markdown("---")
render_metric("Tổng số tri thức", str(len(filtered_units)))

for unit in filtered_units:
    render_unit_card(unit)
