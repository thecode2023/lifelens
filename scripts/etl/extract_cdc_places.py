"""
Extract CDC PLACES county-level health data via SODA API.
Source: https://data.cdc.gov/500-Cities-Places/PLACES-Local-Data-for-Better-Health-County-Data-202/swc5-untb
"""
import requests
import pandas as pd
import os
import time

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
DATASET_ID = "swc5-untb"
BASE_URL = f"https://data.cdc.gov/resource/{DATASET_ID}.csv"

# Key health measures we care about
TARGET_MEASURES = [
    'DIABETES', 'OBESITY', 'MHLTH', 'PHLTH',  # outcomes
    'ACCESS2', 'CHECKUP', 'DENTAL',             # access/preventive
    'BINGE', 'CSMOKING', 'LPA', 'SLEEP',        # behaviors
    'BPHIGH', 'HIGHCHOL', 'STROKE', 'CHD',       # chronic conditions
    'CANCER', 'CASTHMA', 'COPD', 'KIDNEY',       # more conditions
    'DEPRESSION', 'TEETHLOST',                    # additional
]

def extract(limit=50000):
    """Download CDC PLACES county data."""
    print("Extracting CDC PLACES county data...")
    
    all_rows = []
    offset = 0
    batch_size = limit
    
    while True:
        params = {
            '$limit': batch_size,
            '$offset': offset,
            '$where': "data_value IS NOT NULL",
        }
        
        print(f"  Fetching rows {offset} to {offset + batch_size}...")
        resp = requests.get(BASE_URL, params=params, timeout=120)
        resp.raise_for_status()
        
        # Read CSV from response text
        from io import StringIO
        batch = pd.read_csv(StringIO(resp.text))
        
        if len(batch) == 0:
            break
            
        all_rows.append(batch)
        offset += batch_size
        
        if len(batch) < batch_size:
            break
        
        time.sleep(1)  # Be polite
    
    df = pd.concat(all_rows, ignore_index=True)
    print(f"  Total rows downloaded: {len(df)}")
    print(f"  Columns: {list(df.columns)}")
    print(f"  Unique measures: {df['measureid'].nunique() if 'measureid' in df.columns else 'N/A'}")
    
    os.makedirs(DATA_DIR, exist_ok=True)
    out_path = os.path.join(DATA_DIR, 'cdc_places_raw.csv')
    df.to_csv(out_path, index=False)
    print(f"  Saved to {out_path}")
    
    return df


if __name__ == "__main__":
    df = extract()
    print(f"\nShape: {df.shape}")
    if 'measureid' in df.columns:
        print(f"\nAvailable measures:\n{df['measureid'].value_counts().to_string()}")
