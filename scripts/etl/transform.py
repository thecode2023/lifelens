"""
Transform pipeline for LifeLens.
1. Load raw CSVs from data/
2. Pivot CDC PLACES from long to wide format
3. Join all sources on FIPS
4. Calculate Health Equity Index (0-100, higher = better equity)
5. Write to SQLite database
"""
import pandas as pd
import numpy as np
import sqlite3
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from fips_crosswalk import standardize_fips, get_state_fips

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
DB_PATH = os.path.join(DATA_DIR, 'lifelens.db')


def load_cdc_places():
    """Load and pivot CDC PLACES data from long to wide format."""
    print("Loading CDC PLACES...")
    df = pd.read_csv(os.path.join(DATA_DIR, 'cdc_places_raw.csv'), low_memory=False)
    
    # Normalize column names to lowercase
    df.columns = df.columns.str.lower().str.strip()
    
    # Handle different column naming conventions (sample vs real API)
    col_remap = {}
    if 'locationid' in df.columns and 'countyfips' not in df.columns:
        col_remap['locationid'] = 'countyfips'
    if 'locationname' in df.columns and 'countyname' not in df.columns:
        col_remap['locationname'] = 'countyname'
    if 'totalpop' in df.columns and 'totalpopulation' not in df.columns:
        col_remap['totalpop'] = 'totalpopulation'
    if col_remap:
        df = df.rename(columns=col_remap)
    
    print(f"  Columns found: {list(df.columns[:15])}")
    
    # Filter to county-level data only (some datasets include state/national rows)
    if 'datalevelareaid' in df.columns:
        # Real CDC data: filter to county level
        pass
    
    df['countyfips'] = df['countyfips'].apply(standardize_fips)
    
    # Filter out non-county FIPS (state-level entries have 2-digit FIPS)
    df = df[df['countyfips'].str.len() == 5].copy()
    
    # Pivot: one row per county, one column per measure
    pivot = df.pivot_table(
        index='countyfips',
        columns='measureid',
        values='data_value',
        aggfunc='first'
    ).reset_index()
    
    pivot.columns.name = None
    
    # Add county metadata from first occurrence
    meta_cols = ['countyfips']
    for c in ['countyname', 'statedesc', 'stateabbr', 'totalpopulation']:
        if c in df.columns:
            meta_cols.append(c)
    
    meta = df.drop_duplicates('countyfips')[meta_cols]
    pivot = pivot.merge(meta, on='countyfips', how='left')
    
    # If totalpopulation is missing, fill with 0
    if 'totalpopulation' not in pivot.columns:
        pivot['totalpopulation'] = 0
    
    print(f"  {len(pivot)} counties, {len([c for c in pivot.columns if c.isupper()])} measures")
    return pivot


def load_census_acs():
    """Load Census ACS data."""
    print("Loading Census ACS...")
    df = pd.read_csv(os.path.join(DATA_DIR, 'census_acs_raw.csv'))
    df.columns = df.columns.str.lower().str.strip()
    
    if 'fips' not in df.columns and 'county_fips' in df.columns:
        df = df.rename(columns={'county_fips': 'fips'})
    
    df['fips'] = df['fips'].apply(standardize_fips)
    print(f"  {len(df)} counties")
    print(f"  Columns: {list(df.columns)}")
    return df


def load_usda_food():
    """Load USDA Food Access data."""
    print("Loading USDA Food Access...")
    df = pd.read_csv(os.path.join(DATA_DIR, 'usda_food_access_raw.csv'))
    df.columns = df.columns.str.lower().str.strip()
    
    # Handle column naming variants
    if 'county_fips' in df.columns and 'fips' not in df.columns:
        df = df.rename(columns={'county_fips': 'fips'})
    
    df['fips'] = df['fips'].apply(standardize_fips)
    print(f"  {len(df)} counties")
    print(f"  Columns: {list(df.columns)}")
    return df


def join_sources(cdc, census, usda):
    """Join all three sources on FIPS code."""
    print("Joining data sources...")
    
    # Rename CDC FIPS column for consistency
    cdc = cdc.rename(columns={'countyfips': 'fips'})
    
    # Standardize column names before joining to avoid collision
    # CDC has: countyname, statedesc, stateabbr, totalpopulation
    # Census has: county_name, state_name, state_abbr, total_population
    # USDA has: county_name, state_name, state_abbr, total_population (or just fips + metrics)
    
    # Join CDC + Census
    merged = cdc.merge(census, on='fips', how='outer', suffixes=('_cdc', '_acs'))
    
    # Join with USDA
    merged = merged.merge(usda, on='fips', how='outer', suffixes=('', '_usda'))
    
    # Consolidate county name — check all possible column names
    name_cols = [c for c in merged.columns if 'countyname' in c.lower() or 
                 ('county_name' in c.lower() and 'state' not in c.lower())]
    if name_cols:
        merged['county_name'] = merged[name_cols[0]]
        for nc in name_cols[1:]:
            merged['county_name'] = merged['county_name'].fillna(merged[nc])
    elif 'county_name' not in merged.columns:
        merged['county_name'] = ''
    
    # Consolidate state abbr
    abbr_cols = [c for c in merged.columns if c.startswith('stateabbr') or c.startswith('state_abbr')]
    if abbr_cols:
        merged['state_abbr'] = merged[abbr_cols[0]]
        for ac in abbr_cols[1:]:
            merged['state_abbr'] = merged['state_abbr'].fillna(merged[ac])
    elif 'state_abbr' not in merged.columns:
        merged['state_abbr'] = ''
    
    # Consolidate state name
    sname_cols = [c for c in merged.columns if c.startswith('statedesc') or 
                  (c.startswith('state_name') and c != 'state_abbr')]
    if sname_cols:
        merged['state_name'] = merged[sname_cols[0]]
        for sc in sname_cols[1:]:
            merged['state_name'] = merged['state_name'].fillna(merged[sc])
    elif 'state_name' not in merged.columns:
        merged['state_name'] = ''
    
    # Consolidate population
    pop_cols = [c for c in merged.columns if c in ['totalpopulation', 'total_population'] or 
                c.endswith('_population')]
    if pop_cols:
        merged['population'] = merged[pop_cols[0]]
        for pc in pop_cols[1:]:
            merged['population'] = merged['population'].fillna(merged[pc])
    else:
        merged['population'] = 0
    
    merged['population'] = merged['population'].fillna(0)
    merged['state_fips'] = merged['fips'].apply(get_state_fips)
    
    # Fill empty county names with FIPS as fallback
    merged['county_name'] = merged['county_name'].fillna('')
    merged.loc[merged['county_name'] == '', 'county_name'] = 'County ' + merged.loc[merged['county_name'] == '', 'fips']
    
    # Drop redundant/duplicate columns
    drop_cols = [c for c in merged.columns if any(c.endswith(s) for s in ['_cdc', '_acs', '_usda']) or
                 c in ['countyname', 'statedesc', 'stateabbr', 'totalpopulation', 'total_population',
                        'county_name_usda', 'state_name_usda', 'state_abbr_usda', 'total_population_usda']]
    merged = merged.drop(columns=[c for c in drop_cols if c in merged.columns], errors='ignore')
    
    # Track data completeness
    cdc_measures = [c for c in merged.columns if c.isupper() and len(c) <= 12]
    merged['has_cdc'] = merged[cdc_measures].notna().any(axis=1) if cdc_measures else False
    merged['has_census'] = merged.get('median_household_income', pd.Series(dtype=float)).notna()
    merged['has_usda'] = merged.get('low_access_pct', pd.Series(dtype=float)).notna()
    merged['source_count'] = merged[['has_cdc', 'has_census', 'has_usda']].sum(axis=1)
    
    print(f"  Merged: {len(merged)} counties")
    print(f"  3-source coverage: {(merged['source_count'] == 3).sum()} counties")
    print(f"  2-source coverage: {(merged['source_count'] == 2).sum()} counties")
    print(f"  1-source only:     {(merged['source_count'] == 1).sum()} counties")
    print(f"  Columns available: {sorted([c for c in merged.columns if c not in ['fips']])[:20]}...")
    
    return merged


def percentile_rank(series):
    """Convert a series to percentile ranks (0-100). Handles NaN."""
    return series.rank(pct=True, na_option='keep') * 100


def calculate_health_equity_index(df):
    """
    Calculate composite Health Equity Index (0-100, higher = better equity).
    
    Sub-indices:
    - Health Outcomes (25%): Lower disease prevalence = higher score
    - Healthcare Access (25%): Better access/utilization = higher score  
    - Social Determinants (25%): Higher income, education = higher score
    - Food Environment (25%): Better food access = higher score
    
    Uses percentile-rank normalization (robust to outliers).
    """
    print("Calculating Health Equity Index...")
    
    # --- Health Outcomes Sub-Index (invert: lower prevalence = higher score) ---
    outcome_cols = ['DIABETES', 'OBESITY', 'MHLTH', 'PHLTH', 'BPHIGH', 'CHD', 'STROKE', 
                    'COPD', 'DEPRESSION', 'CSMOKING']
    available_outcomes = [c for c in outcome_cols if c in df.columns]
    
    for col in available_outcomes:
        df[f'{col}_pctrank'] = 100 - percentile_rank(df[col])  # invert: low prevalence = high rank
    
    outcome_rank_cols = [f'{c}_pctrank' for c in available_outcomes]
    df['health_outcomes_subindex'] = df[outcome_rank_cols].mean(axis=1)
    
    # --- Healthcare Access Sub-Index ---
    # ACCESS2 (uninsured) - invert: lower = better
    # CHECKUP, DENTAL - higher = better (no invert)
    access_components = {}
    if 'ACCESS2' in df.columns:
        access_components['access2_pctrank'] = 100 - percentile_rank(df['ACCESS2'])
    if 'CHECKUP' in df.columns:
        access_components['checkup_pctrank'] = percentile_rank(df['CHECKUP'])
    if 'DENTAL' in df.columns:
        access_components['dental_pctrank'] = percentile_rank(df['DENTAL'])
    if 'uninsured_rate' in df.columns:
        access_components['uninsured_pctrank'] = 100 - percentile_rank(df['uninsured_rate'])
    
    for k, v in access_components.items():
        df[k] = v
    
    if access_components:
        df['healthcare_access_subindex'] = df[list(access_components.keys())].mean(axis=1)
    else:
        df['healthcare_access_subindex'] = np.nan
    
    # --- Social Determinants Sub-Index ---
    social_components = {}
    if 'median_household_income' in df.columns:
        social_components['income_pctrank'] = percentile_rank(df['median_household_income'])
    if 'poverty_rate' in df.columns:
        social_components['poverty_pctrank'] = 100 - percentile_rank(df['poverty_rate'])
    if 'bachelors_or_higher_pct' in df.columns:
        social_components['education_pctrank'] = percentile_rank(df['bachelors_or_higher_pct'])
    if 'unemployment_rate' in df.columns:
        social_components['unemployment_pctrank'] = 100 - percentile_rank(df['unemployment_rate'])
    
    for k, v in social_components.items():
        df[k] = v
    
    if social_components:
        df['social_determinants_subindex'] = df[list(social_components.keys())].mean(axis=1)
    else:
        df['social_determinants_subindex'] = np.nan
    
    # --- Food Environment Sub-Index ---
    food_components = {}
    if 'low_access_pct' in df.columns:
        food_components['food_access_pctrank'] = 100 - percentile_rank(df['low_access_pct'])
    if 'lila_pct' in df.columns:
        food_components['lila_pctrank'] = 100 - percentile_rank(df['lila_pct'])
    if 'snap_participation_pct' in df.columns:
        # Higher SNAP participation can indicate need, so invert
        food_components['snap_pctrank'] = 100 - percentile_rank(df['snap_participation_pct'])
    
    for k, v in food_components.items():
        df[k] = v
    
    if food_components:
        df['food_environment_subindex'] = df[list(food_components.keys())].mean(axis=1)
    else:
        df['food_environment_subindex'] = np.nan
    
    # --- Composite Index (equal weights) ---
    subindex_cols = ['health_outcomes_subindex', 'healthcare_access_subindex',
                     'social_determinants_subindex', 'food_environment_subindex']
    
    df['health_equity_index'] = df[subindex_cols].mean(axis=1)
    df['health_equity_index'] = df['health_equity_index'].round(1)
    
    # National percentile of the composite score
    df['hei_national_percentile'] = percentile_rank(df['health_equity_index']).round(0)
    
    # Tier labels
    df['hei_tier'] = pd.cut(
        df['health_equity_index'],
        bins=[0, 25, 40, 60, 75, 100],
        labels=['Critical', 'Low', 'Moderate', 'Good', 'High'],
        include_lowest=True
    )
    
    for col in subindex_cols:
        df[col] = df[col].round(1)
    
    print(f"  Index range: {df['health_equity_index'].min():.1f} - {df['health_equity_index'].max():.1f}")
    print(f"  Mean: {df['health_equity_index'].mean():.1f}")
    print(f"  Tier distribution:\n{df['hei_tier'].value_counts().to_string()}")
    
    return df


def load_to_sqlite(df):
    """Write final dataset to SQLite."""
    print(f"Loading to SQLite at {DB_PATH}...")
    
    conn = sqlite3.connect(DB_PATH)
    
    # --- dim_state ---
    dim_state = df[['state_fips', 'state_name', 'state_abbr']].drop_duplicates().dropna(subset=['state_fips'])
    dim_state.to_sql('dim_state', conn, if_exists='replace', index=False)
    print(f"  dim_state: {len(dim_state)} states")
    
    # --- dim_county ---
    dim_county = df[['fips', 'county_name', 'state_fips', 'state_abbr', 'population']].copy()
    dim_county = dim_county.rename(columns={'fips': 'county_fips'})
    dim_county.to_sql('dim_county', conn, if_exists='replace', index=False)
    print(f"  dim_county: {len(dim_county)} counties")
    
    # --- fact_county_health (all measures + index) ---
    # Select relevant columns
    measure_cols = [c for c in df.columns if c.isupper() and len(c) <= 12]
    census_cols = ['median_household_income', 'poverty_rate', 'uninsured_rate', 
                   'bachelors_or_higher_pct', 'median_age', 'unemployment_rate',
                   'white_pct', 'black_pct', 'hispanic_pct']
    food_cols = ['low_access_pct', 'lila_pct', 'snap_participation_pct',
                 'num_grocery_stores', 'grocery_stores_per_1000']
    index_cols = ['health_equity_index', 'hei_national_percentile', 'hei_tier',
                  'health_outcomes_subindex', 'healthcare_access_subindex',
                  'social_determinants_subindex', 'food_environment_subindex']
    coverage_cols = ['has_cdc', 'has_census', 'has_usda', 'source_count']
    
    keep = ['fips'] + measure_cols + [c for c in census_cols + food_cols + index_cols + coverage_cols if c in df.columns]
    fact = df[keep].copy()
    fact = fact.rename(columns={'fips': 'county_fips'})
    fact.to_sql('fact_county_health', conn, if_exists='replace', index=False)
    print(f"  fact_county_health: {len(fact)} rows, {len(fact.columns)} columns")
    
    # --- State-level aggregates for benchmarking ---
    state_agg_cols = measure_cols + [c for c in census_cols + food_cols + index_cols if c in df.columns and c != 'hei_tier']
    state_agg_cols = [c for c in state_agg_cols if c in df.columns]
    
    state_agg = df.groupby('state_fips')[state_agg_cols].mean().round(2).reset_index()
    state_agg = state_agg.merge(dim_state, on='state_fips', how='left')
    state_agg.to_sql('agg_state_health', conn, if_exists='replace', index=False)
    print(f"  agg_state_health: {len(state_agg)} states")
    
    # --- National averages ---
    nat_avg = {col: round(df[col].mean(), 2) for col in state_agg_cols if col in df.columns}
    nat_df = pd.DataFrame([nat_avg])
    nat_df.to_sql('agg_national_health', conn, if_exists='replace', index=False)
    print(f"  agg_national_health: 1 row, {len(nat_df.columns)} columns")
    
    # Create indices
    conn.execute("CREATE INDEX IF NOT EXISTS idx_fact_fips ON fact_county_health(county_fips)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_county_fips ON dim_county(county_fips)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_county_state ON dim_county(state_fips)")
    
    conn.commit()
    conn.close()
    
    db_size = os.path.getsize(DB_PATH) / 1024
    print(f"  Database size: {db_size:.0f} KB")


def run_pipeline():
    """Run the full transform pipeline."""
    print("=" * 60)
    print("LifeLens ETL Pipeline")
    print("=" * 60)
    
    cdc = load_cdc_places()
    census = load_census_acs()
    usda = load_usda_food()
    
    merged = join_sources(cdc, census, usda)
    indexed = calculate_health_equity_index(merged)
    load_to_sqlite(indexed)
    
    print("=" * 60)
    print("Pipeline complete.")
    print("=" * 60)


if __name__ == "__main__":
    run_pipeline()
