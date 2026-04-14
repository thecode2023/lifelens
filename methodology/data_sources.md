# Data Sources

## 1. CDC PLACES

- **URL:** https://data.cdc.gov/500-Cities-Places/PLACES-Local-Data-for-Better-Health-County-Data-202/swc5-untb
- **Provider:** Centers for Disease Control and Prevention
- **Granularity:** County
- **Records:** ~3,000 counties × ~30 health measures
- **Update Frequency:** Annual
- **Access Method:** SODA API (CSV export, no authentication required)
- **Key Variables Used:** Diabetes, obesity, mental health, depression, blood pressure, heart disease, stroke, COPD, smoking, physical inactivity, uninsured rate, checkup rate, dental visit rate

## 2. US Census American Community Survey (ACS) 5-Year Estimates

- **URL:** https://data.census.gov / https://api.census.gov
- **Provider:** US Census Bureau
- **Granularity:** County
- **Records:** ~3,143 counties
- **Update Frequency:** Annual (5-year rolling estimates)
- **Access Method:** Census API (free key required) or bulk CSV download
- **Key Variables Used:** Median household income, poverty rate, uninsured rate, educational attainment, unemployment rate, demographic composition, median age

## 3. USDA Food Access Research Atlas

- **URL:** https://www.ers.usda.gov/data-products/food-access-research-atlas/
- **Provider:** USDA Economic Research Service
- **Granularity:** Census tract (aggregated to county in pipeline)
- **Records:** ~72,000 tracts → ~3,143 counties
- **Update Frequency:** Periodic (last major update: 2019 data)
- **Access Method:** Excel file download (no authentication required)
- **Key Variables Used:** Low food access population, low income + low access population, SNAP participation

## Join Strategy

All three datasets are joined on **FIPS county code** — a 5-digit identifier assigned by the Census Bureau to every US county. The pipeline standardizes FIPS codes to zero-padded 5-digit strings before joining to handle format inconsistencies across sources.

## Coverage Rates

Each county record includes a `source_count` field (1–3) indicating how many sources contributed data. Counties with fewer than 3 sources still appear in the dataset but receive composite index scores based only on available dimensions.
