import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from utils.theme import PAGE_CONFIG, inject_css, stat_card

st.set_page_config(page_title="LifeLens | Health Equity Intelligence", **PAGE_CONFIG)
inject_css()

from utils.db import get_all_counties, get_national_avg

counties = get_all_counties()
nat = get_national_avg()

# Hero section
st.markdown("""
<div style="text-align:center; padding: 40px 0 20px;">
    <div style="font-size: 3.2rem; font-weight: 800; letter-spacing: -0.03em;
         background: linear-gradient(135deg, #e5e7eb 0%, #60a5fa 50%, #10b981 100%);
         -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
        LifeLens
    </div>
    <div style="color: #6b7280; font-size: 1.05rem; margin-top: 4px; font-weight: 400;">
        Health Equity Data Intelligence Platform
    </div>
</div>
""", unsafe_allow_html=True)

# Key metrics bar
critical_count = int((counties['hei_tier'] == 'Critical').sum())
avg_hei = float(nat['health_equity_index'])

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(stat_card(f"{len(counties):,}", "Counties Tracked"), unsafe_allow_html=True)
with c2:
    st.markdown(stat_card(f"{avg_hei:.1f}", "National Avg HEI", color="#3b82f6"), unsafe_allow_html=True)
with c3:
    st.markdown(stat_card(str(critical_count), "Critical Tier", color="#ef4444"), unsafe_allow_html=True)
with c4:
    st.markdown(stat_card("3", "Data Sources"), unsafe_allow_html=True)

st.markdown("<div style='height: 24px'></div>", unsafe_allow_html=True)

# About section in cards
col1, col2 = st.columns([3, 2])

with col1:
    st.markdown("""
    <div class="ll-card">
        <h4>What is LifeLens?</h4>
        <p>LifeLens integrates three federal datasets into a composite <strong style="color:#60a5fa">Health Equity Index</strong> —
        a 0–100 score measuring outcomes, access, social determinants, and food environment at the county level.
        It surfaces disparities through interactive mapping, statistical analysis, and AI-generated community health profiles.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="ll-card">
        <h4>Data Sources</h4>
        <p>
        <strong style="color:#e5e7eb">CDC PLACES</strong> — Health outcomes & preventive care<br>
        <strong style="color:#e5e7eb">Census ACS</strong> — Income, poverty, education<br>
        <strong style="color:#e5e7eb">USDA Food Atlas</strong> — Food access & desert indicators
        </p>
    </div>
    """, unsafe_allow_html=True)

# Navigation cards
st.markdown("<div style='height: 8px'></div>", unsafe_allow_html=True)

n1, n2, n3, n4 = st.columns(4)
nav_items = [
    ("📍", "National Overview", "Choropleth map colored by Health Equity Index"),
    ("🔎", "County Deep Dive", "Detailed profile for any US county"),
    ("🧬", "Social Determinants", "Correlation analysis with R² values"),
    ("📋", "Health Profile", "AI-generated profiles with PDF export"),
]
for col, (icon, title, desc) in zip([n1, n2, n3, n4], nav_items):
    with col:
        st.markdown(f"""
        <div class="ll-card" style="text-align:center; padding: 20px 12px;">
            <div style="font-size: 1.8rem; margin-bottom: 8px;">{icon}</div>
            <h4 style="font-size: 0.85rem; margin-bottom: 4px;">{title}</h4>
            <p style="font-size: 0.75rem; margin: 0;">{desc}</p>
        </div>
        """, unsafe_allow_html=True)

# Tier distribution preview
st.markdown("<div style='height: 16px'></div>", unsafe_allow_html=True)
st.markdown("""
<div class="ll-card">
    <h4>Counties by Health Equity Tier</h4>
    <p style="font-size: 0.75rem; color: #6b7280; margin-top: -4px;">Number of US counties in each scoring band (0–100 scale)</p>
</div>
""", unsafe_allow_html=True)

tier_cols = st.columns(5)
tier_data = [
    ('High', '#10b981', '75–100'),
    ('Good', '#3b82f6', '60–75'),
    ('Moderate', '#f59e0b', '40–60'),
    ('Low', '#f97316', '25–40'),
    ('Critical', '#ef4444', '0–25'),
]
for col, (tier, color, range_str) in zip(tier_cols, tier_data):
    count = int((counties['hei_tier'] == tier).sum())
    with col:
        st.markdown(f"""
        <div style="text-align:center; padding: 12px;">
            <div style="font-size: 1.6rem; font-weight: 800; color: {color};
                 font-family: 'JetBrains Mono', monospace;">{count}</div>
            <div style="font-size: 0.8rem; font-weight: 600; color: {color}; margin-top: 2px;">{tier}</div>
            <div style="font-size: 0.65rem; color: #6b7280; margin-top: 2px;">{range_str}</div>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="ll-footer">
    Built by Yusuf Masood · <a href="https://github.com/thecode2023/lifelens">GitHub</a> ·
    Data: CDC PLACES, Census ACS, USDA Food Access
</div>
""", unsafe_allow_html=True)
