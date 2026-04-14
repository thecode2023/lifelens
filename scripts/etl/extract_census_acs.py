"""
Extract Census ACS 5-Year county-level socioeconomic data.
Uses the Census API. Get a free key at: https://api.census.gov/data/key_signup.html

If API rate limits are an issue, download bulk CSVs from data.census.gov instead.
"""
import requests
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from fips_crosswalk import standardize_fips

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# ACS 5-Year variables
# Docs: https://api.census.gov/data/2022/acs/acs5/variables.html
VARIABLES = {
    'B01003_001E': 'total_population',
    'B19013_001E': 'median_household_income',
    'B17001_002E': 'poverty_count',
    'B27010_001E': 'health_insurance_universe',
    'B27010_017E': 'uninsured_under19',
    'B27010_033E': 'uninsured_19to34',
    'B27010_050E': 'uninsured_35to64',
    'B27010_066E': 'uninsured_65plus',
    'B15003_022E': 'bachelors_count',
    'B15003_023E': 'masters_count',
    'B15003_024E': 'professional_count',
    'B15003_025E': 'doctorate_count',
    'B15003_001E': 'education_universe',
    'B01002_001E': 'median_age',
    'B02001_002E': 'white_alone',
    'B02001_003E': 'black_alone',
    'B03003_003E': 'hispanic',
    'B23025_005E': 'unemployed',
    'B23025_002E': 'labor_force',
}


def extract(api_key=None, year=2022):
    """Download ACS 5-Year data for all US counties."""
    key = api_key or os.environ.get('CENSUS_API_KEY')
    if not key:
        print("WARNING: No Census API key. Set CENSUS_API_KEY env var or pass api_key param.")
        print("Get a free key at: https://api.census.gov/data/key_signup.html")
        return None

    var_list = ','.join(VARIABLES.keys())
    url = f"https://api.census.gov/data/{year}/acs/acs5"
    params = {
        'get': f'NAME,{var_list}',
        'for': 'county:*',
        'key': key,
    }

    print(f"Fetching ACS {year} 5-Year data...")
    resp = requests.get(url, params=params, timeout=120)
    resp.raise_for_status()
    data = resp.json()

    # First row is headers
    headers = data[0]
    rows = data[1:]
    df = pd.DataFrame(rows, columns=headers)

    # Build FIPS from state + county
    df['fips'] = (df['state'] + df['county']).apply(standardize_fips)

    # Rename and convert
    rename = {k: v for k, v in VARIABLES.items()}
    rename['NAME'] = 'county_name_raw'
    df = df.rename(columns=rename)

    # Convert numeric columns
    for col in VARIABLES.values():
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Calculate derived fields
    df['county_name'] = df['county_name_raw'].str.split(',').str[0].str.strip()
    df['state_name'] = df['county_name_raw'].str.split(',').str[1].str.strip()
    df['state_fips'] = df['fips'].str[:2]

    # Rates
    df['uninsured_count'] = df[['uninsured_under19', 'uninsured_19to34',
                                 'uninsured_35to64', 'uninsured_65plus']].sum(axis=1)
    df['uninsured_rate'] = (df['uninsured_count'] / df['health_insurance_universe'] * 100).round(1)

    df['bachelors_plus'] = df[['bachelors_count', 'masters_count',
                                'professional_count', 'doctorate_count']].sum(axis=1)
    df['bachelors_or_higher_pct'] = (df['bachelors_plus'] / df['education_universe'] * 100).round(1)

    df['poverty_rate'] = (df['poverty_count'] / df['total_population'] * 100).round(1)
    df['unemployment_rate'] = (df['unemployed'] / df['labor_force'] * 100).round(1)

    df['white_pct'] = (df['white_alone'] / df['total_population'] * 100).round(1)
    df['black_pct'] = (df['black_alone'] / df['total_population'] * 100).round(1)
    df['hispanic_pct'] = (df['hispanic'] / df['total_population'] * 100).round(1)

    # Select final columns
    keep = ['fips', 'county_name', 'state_name', 'state_fips',
            'total_population', 'median_household_income', 'poverty_rate',
            'uninsured_rate', 'bachelors_or_higher_pct', 'median_age',
            'white_pct', 'black_pct', 'hispanic_pct', 'unemployment_rate']

    # Map state FIPS to abbreviations
    from _state_abbr import STATE_FIPS_TO_ABBR
    df['state_abbr'] = df['state_fips'].map(STATE_FIPS_TO_ABBR)
    keep.append('state_abbr')

    out = df[keep].copy()
    out_path = os.path.join(DATA_DIR, 'census_acs_raw.csv')
    out.to_csv(out_path, index=False)
    print(f"Saved {len(out)} counties to {out_path}")
    return out


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--key', help='Census API key')
    args = parser.parse_args()
    extract(api_key=args.key)
