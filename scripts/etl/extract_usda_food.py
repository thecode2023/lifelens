"""
Extract USDA Food Access Research Atlas data.
Download the Excel file from:
https://www.ers.usda.gov/data-products/food-access-research-atlas/download-the-data/

Save as data/FoodAccessResearchAtlasData.xlsx before running.
The data is at census-tract level — this script aggregates to county.
"""
import pandas as pd
import numpy as np
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from fips_crosswalk import standardize_fips

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data')


def extract(file_path=None):
    """Load and aggregate USDA Food Access data to county level."""
    path = file_path or os.path.join(DATA_DIR, 'FoodAccessResearchAtlasData.xlsx')

    if not os.path.exists(path):
        print(f"ERROR: Download the Food Access Research Atlas Excel file to: {path}")
        print("URL: https://www.ers.usda.gov/data-products/food-access-research-atlas/download-the-data/")
        return None

    print("Loading USDA Food Access Research Atlas...")
    # The main data sheet is typically "Food Access Research Atlas"
    try:
        df = pd.read_excel(path, sheet_name='Food Access Research Atlas')
    except Exception:
        # Try first sheet
        df = pd.read_excel(path, sheet_name=0)

    print(f"  Raw tracts: {len(df)}")
    print(f"  Columns: {list(df.columns[:20])}...")

    # Build county FIPS from tract FIPS (first 5 digits of 11-digit tract FIPS)
    fips_col = None
    for candidate in ['CensusTract', 'FIPS', 'TractFIPS', 'Census Tract']:
        if candidate in df.columns:
            fips_col = candidate
            break

    if fips_col is None:
        print(f"  ERROR: Cannot find tract FIPS column. Available: {list(df.columns)}")
        return None

    df['county_fips'] = df[fips_col].astype(str).str[:5].apply(standardize_fips)

    # Identify key columns (names vary by data release)
    col_map = {}
    for col in df.columns:
        cl = col.lower()
        if 'pop' in cl and '2010' not in cl and 'group' not in cl:
            if 'lapop1' in cl or 'la1' in cl:
                col_map['low_access_pop'] = col
            elif 'lalowi1' in cl or 'lali' in cl:
                col_map['lila_pop'] = col
            elif 'tractsnap' in cl or 'snap' in cl:
                col_map['snap_tracts'] = col
        if 'pop2010' in cl or 'ohu2010' in cl:
            if 'pop' in cl:
                col_map.setdefault('tract_pop', col)

    # Aggregate to county
    agg_dict = {}
    if 'tract_pop' in col_map:
        agg_dict[col_map['tract_pop']] = 'sum'
    if 'low_access_pop' in col_map:
        agg_dict[col_map['low_access_pop']] = 'sum'
    if 'lila_pop' in col_map:
        agg_dict[col_map['lila_pop']] = 'sum'

    if not agg_dict:
        # Fallback: just count tracts
        print("  WARNING: Could not identify standard columns. Using tract counts.")
        county = df.groupby('county_fips').size().reset_index(name='tract_count')
    else:
        county = df.groupby('county_fips').agg(agg_dict).reset_index()

        # Rename
        reverse_map = {v: k for k, v in col_map.items()}
        county = county.rename(columns=reverse_map)

        # Calculate rates
        if 'tract_pop' in county.columns and 'low_access_pop' in county.columns:
            county['low_access_pct'] = (county['low_access_pop'] / county['tract_pop'] * 100).round(1)
        if 'tract_pop' in county.columns and 'lila_pop' in county.columns:
            county['lila_pct'] = (county['lila_pop'] / county['tract_pop'] * 100).round(1)

    county = county.rename(columns={'county_fips': 'fips'})
    out_path = os.path.join(DATA_DIR, 'usda_food_access_raw.csv')
    county.to_csv(out_path, index=False)
    print(f"  Aggregated to {len(county)} counties → {out_path}")
    return county


if __name__ == "__main__":
    extract()
