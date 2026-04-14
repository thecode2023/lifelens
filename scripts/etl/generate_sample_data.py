"""
Generate realistic sample data for LifeLens development.
Mirrors the schema of CDC PLACES, Census ACS, and USDA Food Access.
Run this ONLY for development — real data comes from the extract scripts.
"""
import pandas as pd
import numpy as np
import os
import json

np.random.seed(42)
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# --- Real FIPS codes and county names for ~200 sample counties ---
# Spread across states to make choropleth look realistic
SAMPLE_COUNTIES = [
    # Format: (FIPS, County, State, StateAbbr, StateFIPS, Pop)
    ("01001", "Autauga County", "Alabama", "AL", "01", 58805),
    ("01003", "Baldwin County", "Alabama", "AL", "01", 231767),
    ("01015", "Calhoun County", "Alabama", "AL", "01", 116441),
    ("01073", "Jefferson County", "Alabama", "AL", "01", 674721),
    ("01089", "Madison County", "Alabama", "AL", "01", 388190),
    ("04013", "Maricopa County", "Arizona", "AZ", "04", 4485414),
    ("04019", "Pima County", "Arizona", "AZ", "04", 1043433),
    ("06001", "Alameda County", "California", "CA", "06", 1682353),
    ("06013", "Contra Costa County", "California", "CA", "06", 1165927),
    ("06037", "Los Angeles County", "California", "CA", "06", 10014009),
    ("06059", "Orange County", "California", "CA", "06", 3186989),
    ("06065", "Riverside County", "California", "CA", "06", 2470546),
    ("06067", "Sacramento County", "California", "CA", "06", 1585055),
    ("06073", "San Diego County", "California", "CA", "06", 3338330),
    ("06075", "San Francisco County", "California", "CA", "06", 873965),
    ("06085", "Santa Clara County", "California", "CA", "06", 1936259),
    ("08001", "Adams County", "Colorado", "CO", "08", 519572),
    ("08005", "Arapahoe County", "Colorado", "CO", "08", 655070),
    ("08031", "Denver County", "Colorado", "CO", "08", 715522),
    ("08041", "El Paso County", "Colorado", "CO", "08", 730395),
    ("09001", "Fairfield County", "Connecticut", "CT", "09", 943332),
    ("09003", "Hartford County", "Connecticut", "CT", "09", 899498),
    ("09009", "New Haven County", "Connecticut", "CT", "09", 864835),
    ("10003", "New Castle County", "Delaware", "DE", "10", 570719),
    ("12011", "Broward County", "Florida", "FL", "12", 1944375),
    ("12031", "Duval County", "Florida", "FL", "12", 995567),
    ("12057", "Hillsborough County", "Florida", "FL", "12", 1459762),
    ("12086", "Miami-Dade County", "Florida", "FL", "12", 2716940),
    ("12095", "Orange County", "Florida", "FL", "12", 1429908),
    ("12099", "Palm Beach County", "Florida", "FL", "12", 1492191),
    ("13089", "DeKalb County", "Georgia", "GA", "13", 764382),
    ("13121", "Fulton County", "Georgia", "GA", "13", 1066710),
    ("13135", "Gwinnett County", "Georgia", "GA", "13", 957062),
    ("17031", "Cook County", "Illinois", "IL", "17", 5275541),
    ("17043", "DuPage County", "Illinois", "IL", "17", 932877),
    ("17089", "Kane County", "Illinois", "IL", "17", 516522),
    ("17097", "Lake County", "Illinois", "IL", "17", 696535),
    ("17197", "Will County", "Illinois", "IL", "17", 696355),
    ("18097", "Marion County", "Indiana", "IN", "18", 977203),
    ("21111", "Jefferson County", "Kentucky", "KY", "21", 782969),
    ("22071", "Orleans Parish", "Louisiana", "LA", "22", 383997),
    ("24003", "Anne Arundel County", "Maryland", "MD", "24", 588261),
    ("24005", "Baltimore County", "Maryland", "MD", "24", 854535),
    ("24031", "Montgomery County", "Maryland", "MD", "24", 1062061),
    ("24033", "Prince George's County", "Maryland", "MD", "24", 967201),
    ("25005", "Bristol County", "Massachusetts", "MA", "25", 579200),
    ("25009", "Essex County", "Massachusetts", "MA", "25", 809829),
    ("25013", "Hampden County", "Massachusetts", "MA", "25", 465925),
    ("25017", "Middlesex County", "Massachusetts", "MA", "25", 1632002),
    ("25021", "Norfolk County", "Massachusetts", "MA", "25", 725981),
    ("25023", "Plymouth County", "Massachusetts", "MA", "25", 530819),
    ("25025", "Suffolk County", "Massachusetts", "MA", "25", 797936),
    ("25027", "Worcester County", "Massachusetts", "MA", "25", 862111),
    ("26081", "Kent County", "Michigan", "MI", "26", 657974),
    ("26099", "Macomb County", "Michigan", "MI", "26", 881217),
    ("26125", "Oakland County", "Michigan", "MI", "26", 1274395),
    ("26163", "Wayne County", "Michigan", "MI", "26", 1793561),
    ("27003", "Anoka County", "Minnesota", "MN", "27", 363887),
    ("27053", "Hennepin County", "Minnesota", "MN", "27", 1281565),
    ("27123", "Ramsey County", "Minnesota", "MN", "27", 552352),
    ("29095", "Jackson County", "Missouri", "MO", "29", 717204),
    ("29189", "St. Louis County", "Missouri", "MO", "29", 1004125),
    ("31055", "Douglas County", "Nebraska", "NE", "31", 584526),
    ("32003", "Clark County", "Nevada", "NV", "32", 2265461),
    ("34003", "Bergen County", "New Jersey", "NJ", "34", 955732),
    ("34013", "Essex County", "New Jersey", "NJ", "34", 863728),
    ("34017", "Hudson County", "New Jersey", "NJ", "34", 724854),
    ("34023", "Middlesex County", "New Jersey", "NJ", "34", 863162),
    ("34025", "Monmouth County", "New Jersey", "NJ", "34", 643615),
    ("34029", "Ocean County", "New Jersey", "NJ", "34", 637229),
    ("34039", "Union County", "New Jersey", "NJ", "34", 575345),
    ("36005", "Bronx County", "New York", "NY", "36", 1472654),
    ("36029", "Erie County", "New York", "NY", "36", 954236),
    ("36047", "Kings County", "New York", "NY", "36", 2736074),
    ("36055", "Monroe County", "New York", "NY", "36", 759443),
    ("36059", "Nassau County", "New York", "NY", "36", 1395774),
    ("36061", "New York County", "New York", "NY", "36", 1694251),
    ("36081", "Queens County", "New York", "NY", "36", 2405464),
    ("36087", "Rockland County", "New York", "NY", "36", 338329),
    ("36103", "Suffolk County", "New York", "NY", "36", 1525920),
    ("36119", "Westchester County", "New York", "NY", "36", 1004457),
    ("37063", "Durham County", "North Carolina", "NC", "37", 324833),
    ("37067", "Forsyth County", "North Carolina", "NC", "37", 382295),
    ("37081", "Guilford County", "North Carolina", "NC", "37", 541299),
    ("37119", "Mecklenburg County", "North Carolina", "NC", "37", 1115482),
    ("37183", "Wake County", "North Carolina", "NC", "37", 1129410),
    ("39035", "Cuyahoga County", "Ohio", "OH", "39", 1264817),
    ("39049", "Franklin County", "Ohio", "OH", "39", 1323807),
    ("39061", "Hamilton County", "Ohio", "OH", "39", 830639),
    ("39095", "Lucas County", "Ohio", "OH", "39", 431279),
    ("39113", "Montgomery County", "Ohio", "OH", "39", 537309),
    ("39153", "Summit County", "Ohio", "OH", "39", 540428),
    ("40109", "Oklahoma County", "Oklahoma", "OK", "40", 797434),
    ("40143", "Tulsa County", "Oklahoma", "OK", "40", 669279),
    ("41005", "Clackamas County", "Oregon", "OR", "41", 421401),
    ("41051", "Multnomah County", "Oregon", "OR", "41", 815428),
    ("41067", "Washington County", "Oregon", "OR", "41", 600372),
    ("42003", "Allegheny County", "Pennsylvania", "PA", "42", 1250578),
    ("42017", "Bucks County", "Pennsylvania", "PA", "42", 628341),
    ("42029", "Chester County", "Pennsylvania", "PA", "42", 534413),
    ("42045", "Delaware County", "Pennsylvania", "PA", "42", 576830),
    ("42091", "Montgomery County", "Pennsylvania", "PA", "42", 856553),
    ("42101", "Philadelphia County", "Pennsylvania", "PA", "42", 1603797),
    ("44007", "Providence County", "Rhode Island", "RI", "44", 660741),
    ("47037", "Davidson County", "Tennessee", "TN", "47", 715884),
    ("47093", "Knox County", "Tennessee", "TN", "47", 478971),
    ("47157", "Shelby County", "Tennessee", "TN", "47", 929744),
    ("48029", "Bexar County", "Texas", "TX", "48", 2009324),
    ("48085", "Collin County", "Texas", "TX", "48", 1064465),
    ("48113", "Dallas County", "Texas", "TX", "48", 2613539),
    ("48121", "Denton County", "Texas", "TX", "48", 906402),
    ("48141", "El Paso County", "Texas", "TX", "48", 865657),
    ("48157", "Fort Bend County", "Texas", "TX", "48", 822779),
    ("48201", "Harris County", "Texas", "TX", "48", 4731145),
    ("48215", "Hidalgo County", "Texas", "TX", "48", 870781),
    ("48439", "Tarrant County", "Texas", "TX", "48", 2110640),
    ("48453", "Travis County", "Texas", "TX", "48", 1290188),
    ("49035", "Salt Lake County", "Utah", "UT", "49", 1185238),
    ("51059", "Fairfax County", "Virginia", "VA", "51", 1150309),
    ("51087", "Henrico County", "Virginia", "VA", "51", 334389),
    ("51107", "Loudoun County", "Virginia", "VA", "51", 420959),
    ("51760", "Richmond city", "Virginia", "VA", "51", 226610),
    ("53033", "King County", "Washington", "WA", "53", 2269675),
    ("53053", "Pierce County", "Washington", "WA", "53", 921130),
    ("53061", "Snohomish County", "Washington", "WA", "53", 827957),
    ("55025", "Dane County", "Wisconsin", "WI", "55", 561504),
    ("55079", "Milwaukee County", "Wisconsin", "WI", "55", 945726),
    # Add some rural/low-equity counties for contrast
    ("01023", "Choctaw County", "Alabama", "AL", "01", 12589),
    ("01063", "Greene County", "Alabama", "AL", "01", 8111),
    ("01091", "Marengo County", "Alabama", "AL", "01", 18863),
    ("05035", "Crittenden County", "Arkansas", "AR", "05", 47955),
    ("13007", "Baker County", "Georgia", "GA", "13", 3038),
    ("13251", "Screven County", "Georgia", "GA", "13", 13966),
    ("21013", "Bell County", "Kentucky", "KY", "21", 26032),
    ("21051", "Clay County", "Kentucky", "KY", "21", 19901),
    ("21095", "Harlan County", "Kentucky", "KY", "21", 26010),
    ("21131", "Leslie County", "Kentucky", "KY", "21", 9877),
    ("21189", "Owsley County", "Kentucky", "KY", "21", 4415),
    ("21195", "Pike County", "Kentucky", "KY", "21", 57876),
    ("22035", "East Carroll Parish", "Louisiana", "LA", "22", 6861),
    ("22073", "Ouachita Parish", "Louisiana", "LA", "22", 160268),
    ("28011", "Bolivar County", "Mississippi", "MS", "28", 30600),
    ("28049", "Hinds County", "Mississippi", "MS", "28", 231840),
    ("28063", "Jefferson County", "Mississippi", "MS", "28", 6990),
    ("28075", "Lauderdale County", "Mississippi", "MS", "28", 74125),
    ("28133", "Sunflower County", "Mississippi", "MS", "28", 23569),
    ("28151", "Washington County", "Mississippi", "MS", "28", 43909),
    ("35006", "Cibola County", "New Mexico", "NM", "35", 26675),
    ("35031", "McKinley County", "New Mexico", "NM", "35", 71367),
    ("40001", "Adair County", "Oklahoma", "OK", "40", 22194),
    ("46007", "Bennett County", "South Dakota", "SD", "46", 3404),
    ("46047", "Fall River County", "South Dakota", "SD", "46", 6713),
    ("46065", "Hughes County", "South Dakota", "SD", "46", 17703),
    ("46095", "Oglala Lakota County", "South Dakota", "SD", "46", 14177),
    ("46102", "Oglala Lakota County", "South Dakota", "SD", "46", 14177),
    ("48127", "Dimmit County", "Texas", "TX", "48", 10124),
    ("48243", "Jeff Davis County", "Texas", "TX", "48", 2274),
    ("48427", "Starr County", "Texas", "TX", "48", 64633),
    ("48489", "Willacy County", "Texas", "TX", "48", 21358),
    ("51595", "Emporia city", "Virginia", "VA", "51", 5346),
    ("51678", "Lexington city", "Virginia", "VA", "51", 7446),
    ("54005", "Boone County", "West Virginia", "WV", "54", 21457),
    ("54045", "Logan County", "West Virginia", "WV", "54", 32019),
    ("54047", "McDowell County", "West Virginia", "WV", "54", 18161),
    ("54055", "Mercer County", "West Virginia", "WV", "54", 57746),
    ("54059", "Mingo County", "West Virginia", "WV", "54", 23424),
]


def _correlated_value(base, noise_scale=0.1, low=0, high=100):
    """Generate a value correlated to base with some noise."""
    val = base + np.random.normal(0, noise_scale * 100)
    return np.clip(val, low, high)


def generate_cdc_places():
    """Generate CDC PLACES-style county health data."""
    print("Generating CDC PLACES sample data...")
    
    measures = {
        # measureid: (display_name, category, mean, std, higher_is_worse)
        'DIABETES': ('Diabetes among adults', 'Health Outcomes', 12.0, 4.0, True),
        'OBESITY': ('Obesity among adults', 'Health Outcomes', 32.0, 7.0, True),
        'MHLTH': ('Mental health not good for >=14 days', 'Health Outcomes', 15.0, 4.0, True),
        'PHLTH': ('Physical health not good for >=14 days', 'Health Outcomes', 13.0, 4.0, True),
        'BPHIGH': ('High blood pressure', 'Health Outcomes', 33.0, 6.0, True),
        'HIGHCHOL': ('High cholesterol', 'Health Outcomes', 33.0, 4.0, True),
        'STROKE': ('Stroke among adults', 'Health Outcomes', 3.5, 1.2, True),
        'CHD': ('Coronary heart disease', 'Health Outcomes', 6.5, 2.0, True),
        'CANCER': ('Cancer (excl. skin)', 'Health Outcomes', 6.5, 1.0, True),
        'CASTHMA': ('Current asthma', 'Health Outcomes', 9.5, 1.5, True),
        'COPD': ('COPD among adults', 'Health Outcomes', 7.0, 2.5, True),
        'KIDNEY': ('Chronic kidney disease', 'Health Outcomes', 3.0, 0.8, True),
        'DEPRESSION': ('Depression among adults', 'Health Outcomes', 20.0, 4.0, True),
        'ACCESS2': ('No health insurance (18-64)', 'Prevention', 12.0, 6.0, True),
        'CHECKUP': ('Annual checkup among adults', 'Prevention', 73.0, 6.0, False),
        'DENTAL': ('Dental visit among adults', 'Prevention', 63.0, 8.0, False),
        'CSMOKING': ('Current smoking', 'Health Outcomes', 16.0, 5.0, True),
        'BINGE': ('Binge drinking', 'Health Outcomes', 17.0, 3.0, True),
        'LPA': ('No leisure-time physical activity', 'Health Outcomes', 27.0, 6.0, True),
        'SLEEP': ('Short sleep duration', 'Health Outcomes', 35.0, 4.0, True),
        'TEETHLOST': ('All teeth lost (65+)', 'Health Outcomes', 15.0, 6.0, True),
    }
    
    rows = []
    for fips, county, state, state_abbr, state_fips, pop in SAMPLE_COUNTIES:
        # Create a "deprivation factor" per county for realistic correlation
        # Rural/poor counties cluster toward worse outcomes
        deprivation = np.random.beta(2, 5) if pop > 100000 else np.random.beta(5, 2)
        deprivation = deprivation * 100  # 0-100, higher = more deprived
        
        for mid, (mname, cat, mean, std, worse_is_high) in measures.items():
            if worse_is_high:
                val = mean + (deprivation / 100) * std * 2 + np.random.normal(0, std * 0.3)
            else:
                val = mean - (deprivation / 100) * std * 2 + np.random.normal(0, std * 0.3)
            
            val = max(0.1, min(99.9, val))
            
            rows.append({
                'stateabbr': state_abbr,
                'statedesc': state,
                'countyname': county,
                'countyfips': fips,
                'measureid': mid,
                'measure': mname,
                'category': cat,
                'data_value': round(val, 1),
                'data_value_unit': '%',
                'totalpopulation': pop,
                'year': 2023,
            })
    
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(DATA_DIR, 'cdc_places_raw.csv'), index=False)
    print(f"  Generated {len(df)} rows for {df['countyfips'].nunique()} counties")
    return df


def generate_census_acs():
    """Generate Census ACS-style demographic/economic data."""
    print("Generating Census ACS sample data...")
    
    rows = []
    for fips, county, state, state_abbr, state_fips, pop in SAMPLE_COUNTIES:
        is_urban = pop > 100000
        
        # Income correlates with population density
        base_income = 65000 if is_urban else 38000
        median_income = int(base_income + np.random.normal(0, 15000))
        median_income = max(20000, min(150000, median_income))
        
        # Poverty inversely correlates with income
        poverty_rate = max(3, min(45, 30 - (median_income / 5000) + np.random.normal(0, 4)))
        
        # Uninsured rate
        uninsured = max(3, min(30, 12 + np.random.normal(0, 5) + (1 if not is_urban else -1) * 3))
        
        # Education: % with bachelor's or higher
        bachelors_pct = max(8, min(70, 30 + (median_income - 50000) / 2000 + np.random.normal(0, 5)))
        
        # Demographics
        white_pct = max(10, min(95, np.random.normal(65, 20)))
        black_pct = max(1, min(80, np.random.normal(15, 12)))
        hispanic_pct = max(1, min(80, np.random.normal(18, 15)))
        # Normalize
        total = white_pct + black_pct + hispanic_pct
        white_pct = white_pct / total * 95  # leave 5% for other
        black_pct = black_pct / total * 95
        hispanic_pct = hispanic_pct / total * 95
        
        rows.append({
            'fips': fips,
            'county_name': county,
            'state_name': state,
            'state_abbr': state_abbr,
            'state_fips': state_fips,
            'total_population': pop,
            'median_household_income': median_income,
            'poverty_rate': round(poverty_rate, 1),
            'uninsured_rate': round(uninsured, 1),
            'bachelors_or_higher_pct': round(bachelors_pct, 1),
            'median_age': round(max(25, min(55, 38 + np.random.normal(0, 5))), 1),
            'white_pct': round(white_pct, 1),
            'black_pct': round(black_pct, 1),
            'hispanic_pct': round(hispanic_pct, 1),
            'unemployment_rate': round(max(2, min(15, 5.5 + np.random.normal(0, 2))), 1),
        })
    
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(DATA_DIR, 'census_acs_raw.csv'), index=False)
    print(f"  Generated {len(df)} county records")
    return df


def generate_usda_food():
    """Generate USDA Food Access-style data (pre-aggregated to county)."""
    print("Generating USDA Food Access sample data...")
    
    rows = []
    for fips, county, state, state_abbr, state_fips, pop in SAMPLE_COUNTIES:
        is_urban = pop > 100000
        
        # Low access = % of population >1 mile (urban) or >10 miles (rural) from supermarket
        low_access_pct = max(2, min(60, 
            (15 if is_urban else 35) + np.random.normal(0, 10)))
        
        low_access_pop = int(pop * low_access_pct / 100)
        
        # Low income + low access
        lila_pct = max(1, min(40, low_access_pct * 0.5 + np.random.normal(0, 5)))
        
        # SNAP participation rate
        snap_pct = max(5, min(50, 15 + np.random.normal(0, 8) + (5 if not is_urban else 0)))
        
        rows.append({
            'fips': fips,
            'county_name': county,
            'state_name': state,
            'state_abbr': state_abbr,
            'total_population': pop,
            'low_access_pop': low_access_pop,
            'low_access_pct': round(low_access_pct, 1),
            'lila_pop': int(pop * lila_pct / 100),
            'lila_pct': round(lila_pct, 1),
            'snap_participation_pct': round(snap_pct, 1),
            'num_grocery_stores': max(1, int(pop / 8000 + np.random.normal(0, 3))),
            'grocery_stores_per_1000': round(max(0.05, 1000 / (pop / max(1, int(pop / 8000)))), 2),
        })
    
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(DATA_DIR, 'usda_food_access_raw.csv'), index=False)
    print(f"  Generated {len(df)} county records")
    return df


if __name__ == "__main__":
    generate_cdc_places()
    generate_census_acs()
    generate_usda_food()
    print("\nSample data generation complete.")
