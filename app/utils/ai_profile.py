"""AI-powered Community Health Profile generator using Gemini."""
import os
import json
import streamlit as st

# Measures and their display names for readable profiles
MEASURE_LABELS = {
    'DIABETES': 'Diabetes prevalence',
    'OBESITY': 'Obesity rate',
    'MHLTH': 'Poor mental health days',
    'PHLTH': 'Poor physical health days',
    'BPHIGH': 'High blood pressure',
    'CHD': 'Coronary heart disease',
    'STROKE': 'Stroke prevalence',
    'COPD': 'COPD prevalence',
    'DEPRESSION': 'Depression rate',
    'CSMOKING': 'Smoking rate',
    'ACCESS2': 'Uninsured rate (18-64)',
    'CHECKUP': 'Annual checkup rate',
    'DENTAL': 'Dental visit rate',
    'BINGE': 'Binge drinking rate',
    'LPA': 'Physical inactivity rate',
    'SLEEP': 'Short sleep duration',
}


def _sf(val, default=0):
    """Safely convert to float."""
    if val is None:
        return default
    try:
        f = float(val)
        return default if str(f) == 'nan' else f
    except (ValueError, TypeError):
        return default


def build_profile_context(county, state_avg, national_avg):
    """Build structured data context for the LLM prompt."""
    
    context = {
        'county_name': county.get('county_name', 'Unknown'),
        'state': county.get('state_abbr', ''),
        'population': int(_sf(county.get('population'))),
        'health_equity_index': round(_sf(county.get('health_equity_index')), 1),
        'national_percentile': int(_sf(county.get('hei_national_percentile'))),
        'tier': str(county.get('hei_tier', 'Unknown')),
        'subindices': {
            'Health Outcomes': round(_sf(county.get('health_outcomes_subindex')), 1),
            'Healthcare Access': round(_sf(county.get('healthcare_access_subindex')), 1),
            'Social Determinants': round(_sf(county.get('social_determinants_subindex')), 1),
            'Food Environment': round(_sf(county.get('food_environment_subindex')), 1),
        },
        'health_measures': {},
        'social_economic': {},
        'food_access': {},
        'comparisons': {'state_avg': {}, 'national_avg': {}},
    }
    
    # Health measures with comparisons
    for col, label in MEASURE_LABELS.items():
        val = county.get(col)
        fval = _sf(val, None)
        if fval is not None:
            entry = {'value': round(fval, 1), 'label': label}
            s_val = state_avg.get(col) if state_avg is not None else None
            n_val = national_avg.get(col) if national_avg is not None else None
            if _sf(s_val, None) is not None:
                entry['state_avg'] = round(_sf(s_val), 1)
            if _sf(n_val, None) is not None:
                entry['national_avg'] = round(_sf(n_val), 1)
            context['health_measures'][col] = entry
    
    # Social/economic
    for col, label in [
        ('median_household_income', 'Median household income'),
        ('poverty_rate', 'Poverty rate'),
        ('uninsured_rate', 'Uninsured rate'),
        ('bachelors_or_higher_pct', 'Bachelor\'s degree or higher'),
        ('unemployment_rate', 'Unemployment rate'),
    ]:
        val = _sf(county.get(col), None)
        if val is not None:
            context['social_economic'][col] = {
                'value': round(val, 1) if col != 'median_household_income' else int(val),
                'label': label,
            }
    
    # Food access
    for col, label in [
        ('low_access_pct', 'Low food access population'),
        ('lila_pct', 'Low income + low access'),
        ('snap_participation_pct', 'SNAP participation rate'),
    ]:
        val = _sf(county.get(col), None)
        if val is not None:
            context['food_access'][col] = {'value': round(val, 1), 'label': label}
    
    return context


def generate_profile_prompt(context):
    """Build the LLM prompt for generating a community health profile."""
    return f"""You are a public health analyst writing a Community Health Profile brief.
Based on the data below, write a professional 1-page profile following this structure:

1. **Overview**: County name, state, population, Health Equity Index score and national percentile.
2. **Key Strengths** (2-3): Areas where this county performs ABOVE state/national benchmarks.
3. **Areas of Concern** (2-3): Areas where disparities are most pronounced compared to benchmarks.
4. **Social Determinants Context**: How income, education, food access, and employment correlate with health outcomes in this county.
5. **Benchmark Comparison**: Concise comparison to state and national averages.
6. **Suggested Focus Areas** (2-3): Data-driven suggestions for where interventions could have the most impact.

RULES:
- Use "correlates with" and "associated with" — NEVER "causes."
- Reference specific numbers from the data.
- Keep tone professional and neutral — this is an analytical brief, not advocacy.
- Use Markdown formatting.

DATA:
{json.dumps(context, indent=2)}
"""


def generate_profile(county, state_avg, national_avg, api_key=None):
    """Generate a community health profile using Gemini."""
    context = build_profile_context(county, state_avg, national_avg)
    
    # Check for API key first — don't even try importing Gemini without one
    key = api_key or os.environ.get('GEMINI_API_KEY')
    try:
        secrets_key = st.secrets.get('GEMINI_API_KEY')
        if secrets_key:
            key = key or secrets_key
    except Exception:
        pass
    
    if not key:
        return _fallback_profile(context)
    
    # Only import and call Gemini if we have a key
    prompt = generate_profile_prompt(context)
    try:
        import google.generativeai as genai
        genai.configure(api_key=key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.warning(f"AI generation failed: {e}. Using template profile.")
        return _fallback_profile(context)


def _fallback_profile(ctx):
    """Template-based profile when AI is unavailable."""
    name = ctx['county_name']
    state = ctx['state']
    pop = ctx['population']
    hei = ctx['health_equity_index']
    pct = ctx['national_percentile']
    tier = ctx['tier']
    
    subs = ctx['subindices']
    best_sub = max(subs, key=subs.get)
    worst_sub = min(subs, key=subs.get)
    
    return f"""# Community Health Profile: {name}, {state}

## Overview
{name} is located in {state} with a population of {pop:,}. The county has a Health Equity Index score of **{hei}/100**, placing it in the **{pct}th percentile** nationally ({tier} tier).

## Sub-Index Scores
| Dimension | Score |
|-----------|-------|
| Health Outcomes | {subs['Health Outcomes']} |
| Healthcare Access | {subs['Healthcare Access']} |
| Social Determinants | {subs['Social Determinants']} |
| Food Environment | {subs['Food Environment']} |

## Key Finding
The strongest dimension is **{best_sub}** ({subs[best_sub]}/100), while **{worst_sub}** ({subs[worst_sub]}/100) represents the greatest area for improvement.

---
*Profile generated using LifeLens Health Equity Data Intelligence Platform. Data sources: CDC PLACES, US Census ACS, USDA Food Access Research Atlas.*
"""
