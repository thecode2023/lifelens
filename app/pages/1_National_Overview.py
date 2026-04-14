import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.theme import inject_css, PAGE_CONFIG
from utils.db import get_all_counties, get_national_avg
from utils.charts import choropleth_map, TIER_COLORS

st.set_page_config(page_title="National Overview | LifeLens", **PAGE_CONFIG)
inject_css()

st.title("National Overview")
st.markdown('<p class="page-subtitle">Health Equity Index scores across US counties</p>', unsafe_allow_html=True)

counties = get_all_counties()

# Filter out ghost records from outer join (no real name/state/population)
valid = counties[
    (counties['county_name'].notna()) & 
    (~counties['county_name'].str.startswith('County ')) &
    (counties['state_abbr'].notna()) &
    (counties['state_abbr'] != '') &
    (counties['state_abbr'] != 'None') &
    (counties['population'] > 0)
].copy()

# Metric selector
metric = st.selectbox("Map metric", [
    'health_equity_index',
    'health_outcomes_subindex',
    'healthcare_access_subindex',
    'social_determinants_subindex',
    'food_environment_subindex',
], format_func=lambda x: x.replace('_', ' ').replace('subindex', 'sub-index').title(),
   label_visibility='collapsed')

# Choropleth — use all counties with HEI scores for map coverage
fig = choropleth_map(counties.dropna(subset=[metric]), value_col=metric)
st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# Tier summary bar
st.markdown("<div style="font-size: 0.8rem; font-weight: 600; color: #6b7280; text-transform: uppercase; letter-spacing: 0.06em; margin-top: 16px; margin-bottom: 8px;">Counties by Health Equity Tier</div>", unsafe_allow_html=True)
tier_cols = st.columns(5)
for col, (tier, color) in zip(tier_cols, TIER_COLORS.items()):
    count = int((valid['hei_tier'] == tier).sum())
    with col:
        st.markdown(f"""
        <div style="text-align:center; background: linear-gradient(135deg, rgba(17,24,39,0.8), rgba(15,23,42,0.6));
             border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; padding: 14px 8px;
             border-left: 3px solid {color};">
            <div style="font-size: 1.4rem; font-weight: 800; color: {color};
                 font-family: 'JetBrains Mono', monospace;">{count}</div>
            <div style="font-size: 0.72rem; font-weight: 500; color: #9ca3af; margin-top: 2px;
                 text-transform: uppercase; letter-spacing: 0.05em;">{tier}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height: 24px'></div>", unsafe_allow_html=True)

# Rankings
c1, c2 = st.columns(2)

with c1:
    st.markdown("""
    <div style="font-size: 0.85rem; font-weight: 600; color: #10b981; margin-bottom: 8px;
         text-transform: uppercase; letter-spacing: 0.05em;">▲ Highest Equity</div>
    """, unsafe_allow_html=True)
    top = valid.nlargest(10, 'health_equity_index')[
        ['county_name', 'state_abbr', 'health_equity_index', 'population']].copy()
    top.columns = ['County', 'State', 'HEI', 'Population']
    top['Population'] = top['Population'].apply(lambda x: f"{x:,.0f}")
    top['HEI'] = top['HEI'].apply(lambda x: f"{x:.1f}")
    st.dataframe(top, hide_index=True, use_container_width=True)

with c2:
    st.markdown("""
    <div style="font-size: 0.85rem; font-weight: 600; color: #ef4444; margin-bottom: 8px;
         text-transform: uppercase; letter-spacing: 0.05em;">▼ Lowest Equity</div>
    """, unsafe_allow_html=True)
    bottom = valid.nsmallest(10, 'health_equity_index')[
        ['county_name', 'state_abbr', 'health_equity_index', 'population']].copy()
    bottom.columns = ['County', 'State', 'HEI', 'Population']
    bottom['Population'] = bottom['Population'].apply(lambda x: f"{x:,.0f}")
    bottom['HEI'] = bottom['HEI'].apply(lambda x: f"{x:.1f}")
    st.dataframe(bottom, hide_index=True, use_container_width=True)
