"""UI Block helpers for Nhan Thuat Streamlit WebApp."""

import streamlit as st
from nhan_thuat.models import KnowledgeUnit
from app.utils.localization import t_type, t_domain

def render_tag_pill(label: str, type_class: str = ""):
    """Renders a styled pill tag safely."""
    # We will use st.html for just the tiny inline badge, or markdown
    css_class = f"badge badge-{type_class.lower()}" if type_class else "badge"
    return f'<span class="{css_class}">{label}</span>'

def render_unit_card(unit: KnowledgeUnit, score: float = None):
    """Renders an editorial knowledge card for a knowledge unit using native Streamlit containers."""
    
    with st.container(border=True):
        col1, col2 = st.columns([0.8, 0.2])
        with col1:
            type_badge = render_tag_pill(t_type(unit.type).upper(), unit.type)
            domain_badge = render_tag_pill(t_domain(unit.primary_domain).upper(), "")
            st.markdown(f"{type_badge} {domain_badge}", unsafe_allow_html=True)
            
            # Title
            st.markdown(f"### {unit.title}")
            
            # Summary
            st.markdown(f"**{unit.summary}**")
            
            # Definition
            if unit.definition:
                st.caption(f"_{unit.definition}_")
                
        with col2:
            if score is not None:
                st.markdown(f"<div style='text-align: right; color: var(--text-secondary); font-size: 0.85rem;'>Độ phù hợp: {score:.2f}</div>", unsafe_allow_html=True)

def render_metric(label: str, value: str):
    """Renders a minimalist editorial metric."""
    st.metric(label=label, value=value)

