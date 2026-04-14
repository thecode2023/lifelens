"""Shared theme and CSS for LifeLens."""
import streamlit as st

PAGE_CONFIG = dict(
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

def inject_css():
    """Inject global CSS for all pages."""
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');

        /* === Global === */
        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            max-width: 1200px;
        }

        /* === Sidebar === */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0d1321 0%, #0a0f1a 100%);
            border-right: 1px solid rgba(255,255,255,0.04);
        }
        [data-testid="stSidebar"] [data-testid="stMarkdown"] p {
            font-size: 0.85rem;
            color: #9ca3af;
        }

        /* === Metric cards === */
        [data-testid="stMetric"] {
            background: linear-gradient(135deg, rgba(17,24,39,0.8) 0%, rgba(15,23,42,0.6) 100%);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 12px;
            padding: 16px 20px;
            backdrop-filter: blur(8px);
        }
        [data-testid="stMetric"] label {
            color: #6b7280 !important;
            font-size: 0.75rem !important;
            font-weight: 500 !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        [data-testid="stMetric"] [data-testid="stMetricValue"] {
            font-weight: 700 !important;
            font-size: 1.8rem !important;
            color: #e5e7eb !important;
        }
        [data-testid="stMetric"] [data-testid="stMetricDelta"] {
            font-size: 0.75rem !important;
        }

        /* === Headers === */
        h1 {
            font-weight: 800 !important;
            letter-spacing: -0.02em;
            background: linear-gradient(135deg, #e5e7eb 0%, #9ca3af 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        h2, h3 {
            font-weight: 600 !important;
            color: #d1d5db !important;
            letter-spacing: -0.01em;
        }

        /* === Selectbox === */
        [data-testid="stSelectbox"] > div > div {
            background: #111827;
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 8px;
        }

        /* === Tabs === */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0;
            border-bottom: 1px solid rgba(255,255,255,0.06);
        }
        .stTabs [data-baseweb="tab"] {
            padding: 8px 20px;
            font-size: 0.85rem;
            font-weight: 500;
        }

        /* === Dataframes === */
        [data-testid="stDataFrame"] {
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 8px;
            overflow: hidden;
        }

        /* === Buttons === */
        .stButton > button {
            border-radius: 8px;
            font-weight: 600;
            border: none;
            transition: all 0.2s ease;
        }
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(59,130,246,0.3);
        }

        /* === Download button === */
        .stDownloadButton > button {
            border-radius: 8px;
            font-weight: 600;
        }

        /* === Dividers === */
        hr {
            border-color: rgba(255,255,255,0.04) !important;
            margin: 1.5rem 0 !important;
        }

        /* === Expander === */
        .streamlit-expanderHeader {
            font-weight: 500;
            font-size: 0.9rem;
        }

        /* === Custom card class === */
        .ll-card {
            background: linear-gradient(135deg, rgba(17,24,39,0.8) 0%, rgba(15,23,42,0.6) 100%);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 16px;
        }
        .ll-card h4 {
            color: #e5e7eb;
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 8px;
        }
        .ll-card p {
            color: #9ca3af;
            font-size: 0.85rem;
            line-height: 1.5;
        }

        /* === Hero stat === */
        .ll-hero-stat {
            text-align: center;
            padding: 16px;
        }
        .ll-hero-stat .value {
            font-size: 2.5rem;
            font-weight: 800;
            font-family: 'JetBrains Mono', monospace;
            color: #e5e7eb;
            line-height: 1;
        }
        .ll-hero-stat .label {
            font-size: 0.7rem;
            font-weight: 500;
            color: #6b7280;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-top: 6px;
        }

        /* === Tier badges === */
        .tier-critical { color: #ef4444; font-weight: 700; }
        .tier-low { color: #f97316; font-weight: 700; }
        .tier-moderate { color: #f59e0b; font-weight: 700; }
        .tier-good { color: #3b82f6; font-weight: 700; }
        .tier-high { color: #10b981; font-weight: 700; }

        /* === Page subtitle === */
        .page-subtitle {
            color: #6b7280;
            font-size: 0.95rem;
            margin-top: -8px;
            margin-bottom: 24px;
        }

        /* === Footer === */
        .ll-footer {
            color: #4b5563;
            font-size: 0.75rem;
            text-align: center;
            padding: 32px 0 16px;
            border-top: 1px solid rgba(255,255,255,0.04);
        }
        .ll-footer a { color: #3b82f6; text-decoration: none; }
    </style>
    """, unsafe_allow_html=True)


def tier_badge(tier):
    """Return HTML for a colored tier badge."""
    css_class = f'tier-{tier.lower()}'
    return f'<span class="{css_class}">{tier}</span>'


def stat_card(value, label, color=None):
    """Return HTML for a hero stat card."""
    color_style = f'color: {color};' if color else ''
    return f"""
    <div class="ll-hero-stat">
        <div class="value" style="{color_style}">{value}</div>
        <div class="label">{label}</div>
    </div>
    """
