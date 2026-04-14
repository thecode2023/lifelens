import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.theme import inject_css, PAGE_CONFIG, tier_badge
from utils.db import get_county_list, get_county_with_meta, get_state_avg, get_national_avg
from utils.charts import gauge_chart, bar_comparison, COLORS, TIER_COLORS

st.set_page_config(page_title="County Deep Dive | LifeLens", **PAGE_CONFIG)
inject_css()

st.title("County Deep Dive")
st.markdown('<p class="page-subtitle">Detailed health equity profile for any US county</p>', unsafe_allow_html=True)

county_list = get_county_list()
county_list = county_list.dropna(subset=['county_fips', 'county_name', 'state_abbr'])
county_list = county_list[county_list['county_name'].str.strip() != '']
county_list['label'] = county_list['county_name'] + ', ' + county_list['state_abbr']

selected = st.selectbox(
    "Select a county",
    county_list['county_fips'].tolist(),
    format_func=lambda fips: county_list[county_list['county_fips'] == fips]['label'].values[0],
)

if selected:
    county = get_county_with_meta(selected)
    state_fips = selected[:2]
    state_avg = get_state_avg(state_fips)
    nat_avg = get_national_avg()

    tier = str(county.get('hei_tier', 'Unknown'))
    tier_color = TIER_COLORS.get(tier, '#888')
    hei = float(county['health_equity_index'])
    pctile = int(county['hei_national_percentile'])
    pop = int(county['population'])

    # Header card
    st.markdown(f"""
    <div class="ll-card" style="border-left: 4px solid {tier_color};">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;">
            <div>
                <div style="font-size: 1.5rem; font-weight: 700; color: #e5e7eb;">
                    {county['county_name']}, {county['state_abbr']}
                </div>
                <div style="color: #6b7280; font-size: 0.85rem; margin-top: 4px;">
                    Population: {pop:,} · {pctile}th national percentile
                </div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 2.2rem; font-weight: 800; color: {tier_color};
                     font-family: 'JetBrains Mono', monospace;">{hei:.1f}</div>
                <div style="font-size: 0.7rem; color: #6b7280; text-transform: uppercase;
                     letter-spacing: 0.05em;">Health Equity Index</div>
                <div style="font-size: 0.85rem; font-weight: 600; color: {tier_color};
                     margin-top: 2px;">{tier}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Sub-index gauges
    cols = st.columns(4)
    sub_indices = [
        ('health_outcomes_subindex', 'Health Outcomes'),
        ('healthcare_access_subindex', 'Healthcare Access'),
        ('social_determinants_subindex', 'Social Determinants'),
        ('food_environment_subindex', 'Food Environment'),
    ]
    for col, (key, label) in zip(cols, sub_indices):
        with col:
            raw = county.get(key)
            val = float(raw) if raw is not None and str(raw) != 'nan' else 0.0
            fig = gauge_chart(val, label)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    st.divider()

    # Health measures comparison
    st.markdown("""
    <div style="font-size: 0.85rem; font-weight: 600; color: #9ca3af; margin-bottom: 12px;
         text-transform: uppercase; letter-spacing: 0.05em;">Health Measures vs. National Average</div>
    """, unsafe_allow_html=True)

    measures = {
        'DIABETES': 'Diabetes', 'OBESITY': 'Obesity', 'MHLTH': 'Poor Mental Health',
        'DEPRESSION': 'Depression', 'BPHIGH': 'High Blood Pressure', 'CSMOKING': 'Smoking',
        'LPA': 'Physical Inactivity', 'ACCESS2': 'Uninsured', 'COPD': 'COPD',
    }
    labels, vals, nat_vals = [], [], []
    for col_name, label in measures.items():
        v = county.get(col_name)
        n = nat_avg.get(col_name)
        if v is not None and n is not None:
            try:
                labels.append(label)
                vals.append(float(v))
                nat_vals.append(float(n))
            except (ValueError, TypeError):
                pass

    if labels:
        fig = bar_comparison(labels, vals, nat_vals)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    st.divider()

    # Socioeconomic + Food in two columns
    def _safe(val, default=0):
        """Safely convert to float, handling None/NaN."""
        if val is None or (isinstance(val, float) and str(val) == 'nan'):
            return default
        try:
            return float(val)
        except (ValueError, TypeError):
            return default

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("""
        <div style="font-size: 0.85rem; font-weight: 600; color: #9ca3af; margin-bottom: 12px;
             text-transform: uppercase; letter-spacing: 0.05em;">Socioeconomic</div>
        """, unsafe_allow_html=True)

        income = int(_safe(county.get('median_household_income')))
        income_nat = int(_safe(nat_avg.get('median_household_income')))
        if income > 0:
            st.metric("Median Income", f"${income:,}",
                      delta=f"${income - income_nat:+,} vs nat'l")
        else:
            st.metric("Median Income", "N/A")

        pov = _safe(county.get('poverty_rate'))
        pov_nat = _safe(nat_avg.get('poverty_rate'))
        if pov > 0:
            st.metric("Poverty Rate", f"{pov:.1f}%",
                      delta=f"{pov - pov_nat:+.1f}pp vs nat'l", delta_color="inverse")
        else:
            st.metric("Poverty Rate", "N/A")

        ed = _safe(county.get('bachelors_or_higher_pct'))
        ed_nat = _safe(nat_avg.get('bachelors_or_higher_pct'))
        if ed > 0:
            st.metric("Bachelor's+", f"{ed:.1f}%",
                      delta=f"{ed - ed_nat:+.1f}pp vs nat'l")
        else:
            st.metric("Bachelor's+", "N/A")

    with col_right:
        st.markdown("""
        <div style="font-size: 0.85rem; font-weight: 600; color: #9ca3af; margin-bottom: 12px;
             text-transform: uppercase; letter-spacing: 0.05em;">Food Environment</div>
        """, unsafe_allow_html=True)

        la = _safe(county.get('low_access_pct'))
        st.metric("Low Food Access", f"{la:.1f}%" if la > 0 else "N/A")

        lila = _safe(county.get('lila_pct'))
        st.metric("Low Income + Low Access", f"{lila:.1f}%" if lila > 0 else "N/A")

        snap = _safe(county.get('snap_participation_pct'))
        st.metric("SNAP Participation", f"{snap:.1f}%" if snap > 0 else "N/A")
