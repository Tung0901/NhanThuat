"""Custom CSS injection for Streamlit following minimalist-ui design system."""

import streamlit as st

def inject_minimalist_css():
    """Injects minimalist-ui styles overriding Streamlit defaults."""
    
    css = """
    <style>
    /* Premium Utilitarian Minimalism */
    
    /* Global Typography & Palette */
    :root {
        /* Design Tokens */
        --background: #F8FAFC;
        --surface: #FFFFFF;
        --border: #E2E8F0;
        --text-primary: #0F172A;
        --text-secondary: #64748B;
        --accent: #0284C7;
        --success: #059669;
        --warning: #D97706;
        --danger: #DC2626;
        
        /* Muted Pastels for Badges */
        --badge-law-bg: #FEF2F2;
        --badge-law-text: #991B1B;
        --badge-phenomenon-bg: #F0FDF4;
        --badge-phenomenon-text: #166534;
        --badge-principle-bg: #F0F9FF;
        --badge-principle-text: #075985;
        --badge-model-bg: #FFFBEB;
        --badge-model-text: #92400E;
        --badge-antipattern-bg: #F8FAFC;
        --badge-antipattern-text: #475569;
        --badge-antipattern-border: #CBD5E1;
        
        --font-sans: 'Plus Jakarta Sans', 'Inter', -apple-system, sans-serif;
        --font-serif: 'Lyon Text', 'Newsreader', 'Playfair Display', serif;
        --font-mono: 'Geist Mono', 'SF Mono', 'JetBrains Mono', monospace;
    }
    
    /* Base Body overrides */
    .stApp {
        background-color: var(--background);
        color: var(--text-primary);
        font-family: var(--font-sans);
        line-height: 1.65;
    }
    
    /* Typography Hierarchy */
    h1, h2, h3, h4, h5, h6 {
        font-family: var(--font-serif) !important;
        color: var(--text-primary) !important;
        letter-spacing: -0.015em !important;
    }
    
    h1 { font-size: 2.25rem !important; line-height: 1.2 !important; margin-bottom: 1.5rem !important; }
    h2 { font-size: 1.75rem !important; line-height: 1.3 !important; margin-bottom: 1.25rem !important; }
    h3 { font-size: 1.25rem !important; font-family: var(--font-sans) !important; font-weight: 600 !important; margin-bottom: 1rem !important; }
    
    /* Hide Streamlit branding and header */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {background: transparent !important;}
    
    /* Bento Box / Editorial Article Cards */
    .knowledge-card {
        background-color: var(--surface);
        border: 1px solid var(--border);
        border-radius: 6px;
        padding: 32px;
        margin-bottom: 24px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    
    /* Tags / Badges */
    .badge {
        display: inline-flex;
        align-items: center;
        border-radius: 4px;
        padding: 4px 10px;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-right: 8px;
        margin-bottom: 8px;
        font-family: var(--font-mono);
    }
    .badge-law { background: var(--badge-law-bg); color: var(--badge-law-text); }
    .badge-phenomenon { background: var(--badge-phenomenon-bg); color: var(--badge-phenomenon-text); }
    .badge-principle { background: var(--badge-principle-bg); color: var(--badge-principle-text); }
    .badge-model { background: var(--badge-model-bg); color: var(--badge-model-text); }
    .badge-anti-pattern { background: var(--badge-antipattern-bg); color: var(--badge-antipattern-text); border: 1px solid var(--badge-antipattern-border); }
    
    /* Streamlit Input Overrides */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea, .stSelectbox > div > div > div {
        border-radius: 4px !important;
        border: 1px solid var(--border) !important;
        background-color: var(--surface) !important;
        color: var(--text-primary) !important;
        box-shadow: none !important;
    }
    .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus, .stSelectbox > div > div > div:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 1px var(--accent) !important;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: var(--text-primary) !important;
        color: #FFFFFF !important;
        border-radius: 4px !important;
        border: none !important;
        padding: 8px 24px !important;
        font-weight: 500 !important;
        font-family: var(--font-sans) !important;
    }
    .stButton > button:hover {
        background-color: var(--accent) !important;
        color: #FFFFFF !important;
    }
    
    /* Code and Meta */
    code, pre {
        font-family: var(--font-mono) !important;
        background-color: var(--background) !important;
        border: 1px solid var(--border) !important;
        border-radius: 4px !important;
        font-size: 0.85rem !important;
    }
    
    /* Metrics / Callouts */
    .metric-label {
        text-transform: uppercase;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        color: var(--text-secondary);
        font-family: var(--font-sans);
    }
    .metric-value {
        font-family: var(--font-serif);
        font-size: 2.5rem;
        font-weight: 400;
        color: var(--text-primary);
        line-height: 1.2;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: var(--surface) !important;
        border-right: 1px solid var(--border) !important;
    }
    
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
