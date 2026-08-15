import sys
from pathlib import Path

# Ensure the root and src directories are in the Python path
root_path = Path(__file__).parent.parent
src_path = root_path / "src"
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import streamlit as st

from app.styles.custom_css import inject_minimalist_css

# Page Configuration
st.set_page_config(
    page_title="Nhân Thuật | Kho Tri thức",
    page_icon="♟️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject CSS
inject_minimalist_css()

# Global Branding (Sticky Header)
st.markdown("""
<div style="text-align: center; position: sticky; top: 3.5rem; z-index: 999; background: rgba(248, 250, 252, 0.9); backdrop-filter: blur(8px); padding: 1rem 0; border-bottom: 1px solid var(--border); margin: -4rem -4rem 2rem -4rem;">
    <h1 style='margin-bottom: 0; font-size: 2.2rem;'>♟️ Nhân Thuật</h1>
    <p style='font-style: italic; color: var(--text-secondary); margin-bottom: 0; font-size: 1.1rem;'>Nghệ thuật thấu hiểu và quản trị con người</p>
</div>
""", unsafe_allow_html=True)

# Pages
ask_page = st.Page("pages/ask.py", title="Hỏi Nhân Thuật", icon="🔍", default=True)
explorer_page = st.Page("pages/explorer.py", title="Khám phá Tri thức", icon="📚")
domains_page = st.Page("pages/domains.py", title="Lĩnh vực", icon="🏛️")
evidence_page = st.Page("pages/evidence.py", title="Bằng chứng & Nguồn", icon="⚖️")
system_page = st.Page("pages/system.py", title="Hệ thống", icon="⚙️")
detail_page = st.Page("pages/detail.py", title="Chi tiết Tri thức", icon="📄")

pg = st.navigation([ask_page, explorer_page, domains_page, evidence_page, system_page, detail_page])
pg.run()
