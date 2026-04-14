import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils.theme import inject_css, PAGE_CONFIG
from utils.db import get_county_list, get_county_with_meta, get_state_avg, get_national_avg
from utils.ai_profile import generate_profile
from utils.pdf_export import markdown_to_pdf
from utils.charts import TIER_COLORS

st.set_page_config(page_title="Community Health Profile | LifeLens", **PAGE_CONFIG)
inject_css()

st.title("Community Health Profile")
st.markdown('<p class="page-subtitle">AI-generated narrative profiles for any US county, with PDF export</p>',
            unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="font-size: 0.8rem; font-weight: 600; color: #9ca3af; margin-bottom: 8px;
         text-transform: uppercase; letter-spacing: 0.05em;">AI Settings</div>
    """, unsafe_allow_html=True)
    api_key = st.text_input("Gemini API Key", type="password",
                            help="Optional. Without a key, a structured template profile is generated.")
    st.caption("Free key at [aistudio.google.com](https://aistudio.google.com/apikey)")

# County selector
county_list = get_county_list()
county_list = county_list.dropna(subset=['county_fips', 'county_name', 'state_abbr', 'health_equity_index'])
county_list = county_list[county_list['county_name'].str.strip() != '']
county_list['label'] = county_list['county_name'] + ', ' + county_list['state_abbr'] + \
    '  (HEI: ' + county_list['health_equity_index'].round(1).astype(str) + ')'

selected = st.selectbox(
    "Select a county to profile",
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

    # Summary metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Health Equity Index", f"{hei:.1f}/100")
    m2.metric("National Percentile", f"{int(county['hei_national_percentile'])}th")
    m3.metric("Tier", tier)
    m4.metric("Population", f"{int(county['population']):,}")

    st.markdown("<div style='height: 12px'></div>", unsafe_allow_html=True)

    # Generate button
    if st.button("🧠 Generate Health Profile", type="primary", use_container_width=True):
        with st.spinner("Analyzing county data and generating profile..."):
            profile_text = generate_profile(county, state_avg, nat_avg, api_key=api_key or None)
            st.session_state['profile_text'] = profile_text
            st.session_state['profile_county'] = county['county_name']
            st.session_state['profile_state'] = county['state_abbr']

    # Display profile
    if 'profile_text' in st.session_state:
        st.markdown("""
        <div class="ll-card" style="border-left: 4px solid #3b82f6;">
        """, unsafe_allow_html=True)
        st.markdown(st.session_state['profile_text'])
        st.markdown("</div>", unsafe_allow_html=True)

        # PDF export
        county_name = st.session_state.get('profile_county', 'county')
        state_name = st.session_state.get('profile_state', '')
        try:
            pdf_bytes = markdown_to_pdf(st.session_state['profile_text'], county_name)
            filename = f"LifeLens_{county_name.replace(' ', '_')}_{state_name}.pdf"

            st.download_button(
                label="📄 Download as PDF",
                data=pdf_bytes,
                file_name=filename,
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"PDF generation failed: {e}")

    else:
        st.markdown("""
        <div class="ll-card" style="text-align: center; padding: 40px 24px;">
            <div style="font-size: 2rem; margin-bottom: 12px;">📋</div>
            <div style="color: #9ca3af; font-size: 0.9rem;">
                Select a county and click <strong style="color: #60a5fa;">Generate Health Profile</strong>
                to create an AI-powered narrative assessment.
            </div>
            <div style="color: #6b7280; font-size: 0.75rem; margin-top: 8px;">
                Profiles include key strengths, areas of concern, and data-driven intervention suggestions.
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("📊 Raw data for this county"):
            import pandas as pd
            display_cols = {
                'DIABETES': 'Diabetes %', 'OBESITY': 'Obesity %', 'MHLTH': 'Poor Mental Health %',
                'DEPRESSION': 'Depression %', 'BPHIGH': 'High BP %', 'CSMOKING': 'Smoking %',
                'ACCESS2': 'Uninsured %', 'CHECKUP': 'Annual Checkup %',
                'median_household_income': 'Median Income', 'poverty_rate': 'Poverty %',
                'bachelors_or_higher_pct': "Bachelor's+ %",
                'low_access_pct': 'Low Food Access %', 'lila_pct': 'Low Income+Low Access %',
            }
            data = {}
            for col_name, label in display_cols.items():
                val = county.get(col_name)
                if val is not None:
                    if col_name == 'median_household_income':
                        data[label] = f"${int(val):,}"
                    else:
                        data[label] = f"{float(val):.1f}%"
            st.dataframe(pd.DataFrame([data]).T.rename(columns={0: 'Value'}), use_container_width=True)
