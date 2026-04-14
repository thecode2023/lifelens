# 🔬 LifeLens

**Health Equity Data Intelligence Platform**

LifeLens integrates three federal public health datasets into a composite Health Equity Index that scores US counties across health outcomes, healthcare access, social determinants, and food environment — surfacing disparities through interactive mapping, correlation analysis, and AI-generated community health profiles.

🔗 **[Live Demo](https://lifelens.streamlit.app)** · 📄 **[Methodology](methodology/health_equity_index.md)** · 📊 **[Data Sources](methodology/data_sources.md)**

---

## Dashboard

| Page | Description |
|------|-------------|
| **National Overview** | Choropleth map of Health Equity Index scores across US counties with tier distribution and rankings |
| **County Deep Dive** | Sub-index gauge charts, health measure comparisons vs national benchmarks, socioeconomic context |
| **Social Determinants Explorer** | Interactive scatter plots with trendlines and R² values showing correlations between socioeconomic factors and health outcomes |
| **Community Health Profile** | AI-generated narrative profiles for any county with PDF export |

## Health Equity Index

A composite score (0–100) calculated from four equally-weighted sub-indices using percentile-rank normalization:

- **Health Outcomes** (25%) — Disease prevalence, mental health, health behaviors
- **Healthcare Access** (25%) — Insurance coverage, preventive care utilization
- **Social Determinants** (25%) — Income, poverty, education, employment
- **Food Environment** (25%) — Food desert indicators, SNAP participation

Full methodology: [`methodology/health_equity_index.md`](methodology/health_equity_index.md)

## Data Pipeline

```
CDC PLACES + Census ACS + USDA Food Access
            │
            ▼
  Python/Pandas ETL Pipeline
  - FIPS code standardization
  - Multi-source join
  - Percentile-rank normalization
  - Composite index calculation
            │
            ▼
    SQLite Database (baked)
            │
            ▼
    Streamlit Dashboard + Gemini AI
```

## Tech Stack

- **ETL:** Python, Pandas, NumPy
- **Database:** SQLite
- **Dashboard:** Streamlit, Plotly
- **AI:** Google Gemini 2.0 Flash
- **PDF Export:** fpdf2
- **Deployment:** Streamlit Cloud

## Setup

```bash
# Clone
git clone https://github.com/thecode2023/lifelens.git
cd lifelens

# Install
pip install -r requirements.txt

# Run with sample data
python scripts/etl/generate_sample_data.py
python scripts/etl/transform.py
streamlit run app/Home.py
```

### With Real Data

1. **CDC PLACES:** `python scripts/etl/extract_cdc_places.py`
2. **Census ACS:** `python scripts/etl/extract_census_acs.py --key YOUR_CENSUS_API_KEY`
3. **USDA:** Download [Food Access Research Atlas](https://www.ers.usda.gov/data-products/food-access-research-atlas/download-the-data/) Excel file to `data/FoodAccessResearchAtlasData.xlsx`, then run `python scripts/etl/extract_usda_food.py`
4. **Transform:** `python scripts/etl/transform.py`
5. **Run:** `streamlit run app/Home.py`

### Environment Variables

```
GEMINI_API_KEY=your_gemini_api_key    # For AI community health profiles
CENSUS_API_KEY=your_census_api_key    # For Census ACS extraction
```

## Author

**Yusuf Masood** — [GitHub](https://github.com/thecode2023)

---

*Data sources: CDC PLACES, US Census ACS, USDA Food Access Research Atlas. All data is aggregate/population-level. Correlations do not imply causation.*
