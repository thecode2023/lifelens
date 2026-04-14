# LifeLens

**Health Equity Data Intelligence Platform**

LifeLens surfaces health disparities across 3,100+ US counties by integrating three federal public health datasets into a composite Health Equity Index — a 0–100 score measuring outcomes, access, social determinants, and food environment. The platform combines geographic visualization, statistical correlation analysis, and AI-generated community health profiles into a single analytical tool.

🔗 **[Live Demo](https://lifelens.streamlit.app)** · 📄 **[Index Methodology](methodology/health_equity_index.md)** · 📊 **[Data Sources](methodology/data_sources.md)**

---

## Health Equity Index

A composite score (0–100, higher = better equity) calculated from four equally-weighted sub-indices using percentile-rank normalization across all US counties:

| Sub-Index | Weight | Source | Measures |
|-----------|--------|--------|----------|
| Health Outcomes | 25% | CDC PLACES | Diabetes, obesity, depression, heart disease, COPD, smoking, physical inactivity |
| Healthcare Access | 25% | CDC PLACES + Census ACS | Uninsured rate, annual checkup rate, dental visit rate |
| Social Determinants | 25% | Census ACS | Median income, poverty rate, educational attainment, unemployment |
| Food Environment | 25% | USDA Food Access | Low food access population, food desert indicators |

Percentile-rank normalization was chosen over min-max scaling for robustness to outliers. Full methodology, limitations, and reproducibility notes: [`methodology/health_equity_index.md`](methodology/health_equity_index.md)

## Dashboard

**National Overview** — Choropleth map colored by Health Equity Index with sub-index toggle, tier distribution, and county rankings.

**County Deep Dive** — Sub-index gauge charts, health measure comparison vs. national benchmarks, socioeconomic and food environment metrics for any selected county.

**Social Determinants Explorer** — Interactive scatter plots with trendlines and R² values showing correlations between socioeconomic factors (income, poverty, education, food access) and health outcomes (diabetes, obesity, depression, smoking). Key finding: poverty and diabetes show a strong positive correlation (r ≈ 0.67).

**Community Health Profile** — AI-generated narrative assessments for any county with structured data context passed to Gemini 2.0 Flash (or template fallback), exportable as PDF.

## Data Pipeline

```
CDC PLACES (3,144 counties × 40 measures)
Census ACS 5-Year (3,222 counties × 15 variables)
USDA Food Access Atlas (72,531 tracts → 3,183 counties)
                    │
                    ▼
     Python/Pandas ETL Pipeline
     ├── FIPS code standardization
     ├── Multi-source outer join
     ├── Negative value cleaning (Census sentinel codes)
     ├── Percentile-rank normalization
     └── Composite index calculation
                    │
                    ▼
          SQLite (baked, 1.6 MB)
                    │
                    ▼
     Streamlit Dashboard (4 pages)
     └── Gemini 2.0 Flash → PDF Export
```

ETL scripts are re-runnable against updated source data. The baked SQLite database is committed to the repo for zero-dependency deployment.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| ETL | Python, Pandas, NumPy |
| Database | SQLite |
| Dashboard | Streamlit, Plotly |
| AI Profiles | Google Gemini 2.0 Flash |
| PDF Export | fpdf2 |
| Deployment | Streamlit Cloud |

## Run Locally

```bash
git clone https://github.com/thecode2023/lifelens.git
cd lifelens
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app/Home.py
```

The app runs immediately using the baked SQLite database. To rebuild from raw sources:

```bash
# CDC PLACES (no auth required)
python scripts/etl/extract_cdc_places.py

# Census ACS (free API key: api.census.gov/data/key_signup.html)
python scripts/etl/extract_census_acs.py --key YOUR_KEY

# USDA (manual download from ers.usda.gov, save to data/)
python scripts/etl/extract_usda_food.py

# Rebuild database
python scripts/etl/transform.py
```

## Project Structure

```
lifelens/
├── app/
│   ├── Home.py                          # Landing page
│   ├── pages/
│   │   ├── 1_National_Overview.py       # Choropleth map
│   │   ├── 2_County_Deep_Dive.py        # County profile
│   │   ├── 3_Social_Determinants.py     # Correlation analysis
│   │   └── 4_Community_Health_Profile.py # AI profiles + PDF
│   └── utils/
│       ├── db.py                        # SQLite queries + caching
│       ├── charts.py                    # Plotly chart builders
│       ├── ai_profile.py               # Gemini integration
│       ├── pdf_export.py               # fpdf2 markdown→PDF
│       └── theme.py                    # CSS + design system
├── scripts/
│   ├── etl/
│   │   ├── extract_cdc_places.py
│   │   ├── extract_census_acs.py
│   │   ├── extract_usda_food.py
│   │   ├── transform.py                # Join + index calculation
│   │   └── generate_sample_data.py     # Dev sample data
│   └── fips_crosswalk.py               # FIPS standardization
├── methodology/
│   ├── health_equity_index.md           # Full methodology doc
│   └── data_sources.md                  # Source documentation
├── data/
│   └── lifelens.db                      # Baked SQLite database
└── requirements.txt
```

## Author

**Yusuf Masood** · [GitHub](https://github.com/thecode2023)

---

*Data: CDC PLACES, US Census American Community Survey, USDA Food Access Research Atlas. All data is aggregate/population-level. Correlations do not imply causation. See [methodology](methodology/health_equity_index.md) for limitations.*
