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

# Sidebar Branding
with st.sidebar:
    st.markdown("<h2 style='text-align: center; margin-bottom: 0;'>♟️ Nhân Thuật</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-style: italic; color: var(--text-secondary);'>Nghệ thuật thấu hiểu và quản trị con người</p>", unsafe_allow_html=True)
    st.divider()

# Pages
ask_page = st.Page("pages/ask.py", title="Hỏi Nhân Thuật", icon="🔍", default=True)
explorer_page = st.Page("pages/explorer.py", title="Khám phá Tri thức", icon="📚")
domains_page = st.Page("pages/domains.py", title="Lĩnh vực", icon="🏛️")
evidence_page = st.Page("pages/evidence.py", title="Bằng chứng & Nguồn", icon="⚖️")
system_page = st.Page("pages/system.py", title="Hệ thống", icon="⚙️")
detail_page = st.Page("pages/detail.py", title="Chi tiết Tri thức", icon="📄")

pg = st.navigation([ask_page, explorer_page, domains_page, evidence_page, system_page, detail_page])
pg.run()
