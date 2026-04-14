import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.theme import inject_css, PAGE_CONFIG
from utils.db import get_all_counties
from utils.charts import scatter_correlation, COLORS

st.set_page_config(page_title="Social Determinants | LifeLens", **PAGE_CONFIG)
inject_css()

st.title("Social Determinants Explorer")
st.markdown('<p class="page-subtitle">How socioeconomic and environmental factors correlate with health outcomes</p>',
            unsafe_allow_html=True)

counties = get_all_counties()

# Only show options for columns that actually exist in the data
_X_ALL = {
    'median_household_income': 'Median Household Income ($)',
    'poverty_rate': 'Poverty Rate (%)',
    'bachelors_or_higher_pct': 'Bachelor\'s Degree+ (%)',
    'uninsured_rate': 'Uninsured Rate (%)',
    'unemployment_rate': 'Unemployment Rate (%)',
    'low_access_pct': 'Low Food Access (%)',
    'lila_pct': 'Low Income + Low Access (%)',
    'snap_participation_pct': 'SNAP Participation (%)',
}

_Y_ALL = {
    'health_equity_index': 'Health Equity Index',
    'DIABETES': 'Diabetes Prevalence (%)',
    'OBESITY': 'Obesity Rate (%)',
    'MHLTH': 'Poor Mental Health Days (%)',
    'DEPRESSION': 'Depression Rate (%)',
    'BPHIGH': 'High Blood Pressure (%)',
    'CSMOKING': 'Smoking Rate (%)',
    'LPA': 'Physical Inactivity (%)',
    'COPD': 'COPD Prevalence (%)',
    'health_outcomes_subindex': 'Health Outcomes Sub-Index',
}

# Filter to columns present in data with at least some non-null values
X_OPTIONS = {k: v for k, v in _X_ALL.items() if k in counties.columns and counties[k].notna().sum() > 10}
Y_OPTIONS = {k: v for k, v in _Y_ALL.items() if k in counties.columns and counties[k].notna().sum() > 10}

col1, col2 = st.columns(2)
with col1:
    x_col = st.selectbox("X-axis (Social Determinant)", list(X_OPTIONS.keys()),
                         format_func=lambda k: X_OPTIONS[k])
with col2:
    y_col = st.selectbox("Y-axis (Health Outcome)", list(Y_OPTIONS.keys()),
                         format_func=lambda k: Y_OPTIONS[k])

fig = scatter_correlation(counties, x_col, y_col, X_OPTIONS[x_col], Y_OPTIONS[y_col])
st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# Interpretation
with st.expander("How to read this chart"):
    st.markdown("""
    Each dot is a US county — larger dots represent larger populations. The dashed line shows the linear trend.

    **R²** measures how much variation in the Y variable is associated with the X variable:
    **> 0.5** strong · **0.2–0.5** moderate · **< 0.2** weak

    ⚠️ Correlation ≠ causation. These are county-level aggregates subject to ecological fallacy.
    """)

st.divider()

# Key correlations
st.markdown("""
<div style="font-size: 0.85rem; font-weight: 600; color: #9ca3af; margin-bottom: 16px;
     text-transform: uppercase; letter-spacing: 0.05em;">Key Correlations</div>
""", unsafe_allow_html=True)

insight_pairs = [
    ('poverty_rate', 'DIABETES', 'Poverty & Diabetes'),
    ('median_household_income', 'health_equity_index', 'Income & Equity'),
    ('low_access_pct', 'OBESITY', 'Food Access & Obesity'),
    ('bachelors_or_higher_pct', 'DEPRESSION', 'Education & Depression'),
]

# Filter to pairs where both columns exist
insight_pairs = [(x, y, t) for x, y, t in insight_pairs 
                 if x in counties.columns and y in counties.columns]

if insight_pairs:
    cols = st.columns(len(insight_pairs))
    for i, (x, y, title) in enumerate(insight_pairs):
        with cols[i]:
            valid = counties[[x, y]].dropna()
            if len(valid) > 2:
                corr = valid[x].corr(valid[y])
                direction = "positive" if corr > 0 else "negative"
                strength = "Strong" if abs(corr) > 0.5 else "Moderate" if abs(corr) > 0.3 else "Weak"
                color = '#ef4444' if abs(corr) > 0.5 else '#f59e0b' if abs(corr) > 0.3 else '#6b7280'

                st.markdown(f"""
                <div class="ll-card" style="text-align: center; padding: 16px 12px;">
                    <div style="font-size: 1.3rem; font-weight: 800; color: {color};
                         font-family: 'JetBrains Mono', monospace;">r = {corr:.3f}</div>
                    <div style="font-size: 0.78rem; font-weight: 600; color: #e5e7eb; margin-top: 6px;">{title}</div>
                    <div style="font-size: 0.68rem; color: #6b7280; margin-top: 2px;">{strength} {direction}</div>
                </div>
                """, unsafe_allow_html=True)
