import sys
from pathlib import Path
root_path = Path(__file__).resolve().parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))
src_path = root_path / 'src'
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import streamlit as st

from app.components.ui_blocks import render_tag_pill
from app.services.engine_adapter import EngineAdapter
from app.utils.localization import t_domain, t_evidence, t_title, t_type

st.title("Chi tiết Tri thức")

adapter = EngineAdapter()
all_units = adapter.engine.units_by_id

unit_id = st.selectbox("Chọn Mã Tri thức", [""] + sorted(all_units.keys()))

if unit_id:
    # Need KnowledgeUnit model
    iu = all_units[unit_id]
    # Re-instantiate KnowledgeUnit from raw dict
    from nhan_thuat.models import KnowledgeUnit
    unit = KnowledgeUnit.from_mapping(iu.raw_data, source_path=None)
    
    st.markdown("---")
    
    type_vn = t_type(unit.type)
    title_vn = t_title(unit.title)
    
    st.markdown(f"[{type_vn}]")
    st.markdown(f"## {title_vn}")
    if title_vn != unit.title:
        st.caption(unit.title)
    
    type_badge = render_tag_pill(type_vn.upper(), unit.type)
    domain_badge = render_tag_pill(t_domain(unit.primary_domain).upper(), "")
    st.markdown(f"{type_badge} {domain_badge}", unsafe_allow_html=True)
    
    st.markdown("### Mô tả ngắn")
    st.markdown(unit.summary)
    
    st.markdown("### Đây là gì?")
    st.info(unit.definition)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if unit.mechanism:
            st.markdown("### Cơ chế")
            for m in unit.mechanism:
                st.markdown(f"- {m}")
                
        if unit.conditions:
            st.markdown("### Khi nào nên chú ý?")
            for c in unit.conditions:
                st.markdown(f"- {c}")
                
        if unit.exceptions:
            st.markdown("### Giới hạn áp dụng")
            for e in unit.exceptions:
                st.markdown(f"- {e}")
                
    with col2:
        if unit.risks:
            st.markdown("### Rủi ro")
            for r in unit.risks:
                st.markdown(f"- <span style='color:var(--pastel-red-text);'>{r}</span>", unsafe_allow_html=True)
                
        st.markdown("### Tri thức liên quan")
        deps = adapter.resolve_dependencies(unit.id)
        if deps:
            for d in deps:
                st.markdown(f"- **{d.id}**: {t_title(d.title)}")
        else:
            st.caption("Không có tri thức liên quan.")

    st.markdown("---")
    st.markdown("## Bằng chứng")
    
    if unit.evidence:
        st.markdown(f"**Loại bằng chứng:** `{t_evidence(unit.evidence.level).upper()}`")
        if unit.evidence.references:
            st.markdown("**Nguồn:**")
            for ref in unit.evidence.references:
                st.markdown(f"- {ref}")
        else:
            st.caption("Không có nguồn trích dẫn.")

    st.markdown("---")
    st.markdown("## Xuất dữ liệu")
    col_e1, col_e2 = st.columns(2)
    json_export = adapter.engine.units_by_id[unit.id].raw_data
    markdown_export = f"# {unit.title}\n- Mã: {unit.id}\n- Loại: {unit.type}\n- Lĩnh vực: {unit.primary_domain}\n\n## Tóm tắt\n{unit.summary}\n\n## Định nghĩa\n{unit.definition}"
    with col_e1:
        st.download_button("Tải JSON", data=str(json_export), file_name=f"{unit.id}.json", mime="application/json")
    with col_e2:
        st.download_button("Tải Markdown", data=markdown_export, file_name=f"{unit.id}.md", mime="text/markdown")
