# Health Equity Index — Methodology

**Version:** 1.0
**Author:** Yusuf Masood
**Platform:** LifeLens Health Equity Data Intelligence Platform
**Last Updated:** 2025

---

## 1. Purpose

The Health Equity Index (HEI) is a composite score that quantifies the relative health equity standing of US counties across four dimensions: health outcomes, healthcare access, social determinants, and food environment. It is designed to surface disparities, enable geographic comparison, and identify communities where targeted interventions may have the greatest impact.

The HEI is **not** a clinical tool or causal model. It is an analytical framework for population-level comparison using publicly available aggregate data.

---

## 2. Data Sources

| Source | Provider | Granularity | Key Variables | Update Frequency |
|--------|----------|-------------|---------------|-----------------|
| PLACES | CDC | County | Disease prevalence, preventive care, health behaviors | Annual |
| American Community Survey (5-Year) | US Census Bureau | County | Income, poverty, education, insurance, demographics | Annual |
| Food Access Research Atlas | USDA ERS | Census tract → County | Food desert indicators, SNAP participation | Periodic |

All datasets are publicly available, require no API authentication, and are joined on **FIPS county codes** (5-digit, zero-padded).

### Coverage

The pipeline targets all ~3,143 US counties. Coverage depends on data availability across all three sources. Counties missing data from any source are flagged but not excluded from the dataset — they receive sub-index scores only for dimensions with available data, and the composite index is calculated as the mean of available sub-indices.

---

## 3. Index Construction

### 3.1 Normalization Method

All input measures are converted to **percentile ranks** (0–100) within the dataset rather than min-max scaled. This decision was made for two reasons:

1. **Robustness to outliers.** Min-max scaling compresses the majority of values when extreme outliers exist (e.g., a single county with 50% diabetes prevalence would compress the scale for all other counties). Percentile ranking distributes counties uniformly across the 0–100 range regardless of outlier magnitude.

2. **Interpretability.** A percentile rank of 75 means "this county scores better than 75% of counties on this measure," which is more intuitive for non-technical stakeholders than a min-max value of 0.42.

### 3.2 Polarity Alignment

Health measures have different polarities — for some, higher values indicate worse outcomes (e.g., diabetes prevalence), while for others, higher values indicate better outcomes (e.g., annual checkup rate). All measures are aligned so that **higher percentile rank = better equity**:

- **Inverted measures** (higher raw value = worse): Diabetes, obesity, poor mental health days, poor physical health days, high blood pressure, coronary heart disease, stroke, COPD, depression, smoking, physical inactivity, uninsured rate, poverty rate, unemployment rate, low food access, SNAP participation rate
- **Direct measures** (higher raw value = better): Annual checkup rate, dental visit rate, median household income, bachelor's degree attainment

### 3.3 Sub-Index Composition

The HEI consists of four equally weighted sub-indices:

#### Health Outcomes Sub-Index (25%)

Measures the burden of disease and health-risk behaviors.

| Measure | Source | Polarity |
|---------|--------|----------|
| Diabetes prevalence | CDC PLACES | Inverted |
| Obesity rate | CDC PLACES | Inverted |
| Poor mental health days (≥14/month) | CDC PLACES | Inverted |
| Poor physical health days (≥14/month) | CDC PLACES | Inverted |
| High blood pressure | CDC PLACES | Inverted |
| Coronary heart disease | CDC PLACES | Inverted |
| Stroke prevalence | CDC PLACES | Inverted |
| COPD prevalence | CDC PLACES | Inverted |
| Depression | CDC PLACES | Inverted |
| Smoking rate | CDC PLACES | Inverted |

Sub-index = mean of percentile ranks across available measures.

#### Healthcare Access Sub-Index (25%)

Measures the ability of residents to obtain and utilize healthcare services.

| Measure | Source | Polarity |
|---------|--------|----------|
| Uninsured rate (18–64) | CDC PLACES | Inverted |
| Annual checkup rate | CDC PLACES | Direct |
| Dental visit rate | CDC PLACES | Direct |
| Uninsured rate (all ages) | Census ACS | Inverted |

Sub-index = mean of percentile ranks across available measures.

#### Social Determinants Sub-Index (25%)

Measures socioeconomic conditions that influence health.

| Measure | Source | Polarity |
|---------|--------|----------|
| Median household income | Census ACS | Direct |
| Poverty rate | Census ACS | Inverted |
| Bachelor's degree or higher (%) | Census ACS | Direct |
| Unemployment rate | Census ACS | Inverted |

Sub-index = mean of percentile ranks across available measures.

#### Food Environment Sub-Index (25%)

Measures access to healthy food options.

| Measure | Source | Polarity |
|---------|--------|----------|
| Low food access population (%) | USDA | Inverted |
| Low income + low access (%) | USDA | Inverted |
| SNAP participation rate | USDA | Inverted |

SNAP participation is inverted because higher participation rates are associated with higher community need, not better food access. This is a debatable choice — an alternative interpretation is that high SNAP uptake reflects effective program delivery. The current treatment prioritizes consistency with the other food access measures.

Sub-index = mean of percentile ranks across available measures.

### 3.4 Composite Score

The composite Health Equity Index is the **unweighted arithmetic mean** of the four sub-indices:

```
HEI = (Health Outcomes + Healthcare Access + Social Determinants + Food Environment) / 4
```

Equal weighting was chosen because there is no empirical or consensus basis for assigning differential weights across these dimensions. The methodology document and codebase are structured to allow weight adjustment for sensitivity analysis.

### 3.5 Tier Classification

Counties are classified into tiers based on their composite HEI score:

| Tier | Score Range | Interpretation |
|------|------------|----------------|
| Critical | 0–25 | Severe disparities across multiple dimensions |
| Low | 25–40 | Significant gaps in health equity |
| Moderate | 40–60 | Mixed performance, some areas of concern |
| Good | 60–75 | Above-average equity with room for improvement |
| High | 75–100 | Strong performance across most dimensions |

---

## 4. Limitations

### 4.1 Ecological Fallacy

All data is aggregate at the county level. Patterns observed across counties do not necessarily apply to individuals within those counties. A county with a high HEI score may still contain pockets of severe health inequity, and vice versa.

### 4.2 Data Recency

CDC PLACES, Census ACS, and USDA data are released on different schedules and reflect different reference periods. The HEI represents a composite snapshot, not a single point-in-time measurement.

### 4.3 Equal Weighting

The four sub-indices are weighted equally (25% each). Alternative weighting schemes could produce meaningfully different rankings. Users should consider sensitivity analysis — adjusting weights to test whether conclusions are robust to different assumptions about the relative importance of each dimension.

### 4.4 Missing Data

Counties with incomplete data across sources receive sub-index scores only for available dimensions. The composite score is the mean of available sub-indices, which means a county with data from only one source will have a composite score based solely on that dimension. These counties are flagged in the dataset with a `source_count` field.

### 4.5 Measure Selection

The measures included in each sub-index represent a curated subset of available variables. Alternative measure selections — particularly the inclusion of environmental quality data (e.g., EPA EJScreen), hospital quality metrics (e.g., CMS), or broadband access data — could alter index values and rankings.

### 4.6 SNAP Participation Polarity

The treatment of SNAP participation as an inverted measure (higher participation = lower score) is debatable. High SNAP participation could indicate effective social safety net delivery rather than community need. This choice is documented and can be toggled in the codebase.

---

## 5. Reproducibility

The complete ETL pipeline, index calculation logic, and dashboard source code are available in the project repository. The pipeline is deterministic given the same input data — running the same extraction scripts against the same data releases will produce identical index values.

Key files:
- `scripts/etl/transform.py` — Data joining and index calculation
- `scripts/fips_crosswalk.py` — FIPS code standardization
- `scripts/etl/extract_*.py` — Data extraction scripts for each source

---

## 6. References

- CDC PLACES: https://www.cdc.gov/places/
- US Census American Community Survey: https://www.census.gov/programs-surveys/acs
- USDA Food Access Research Atlas: https://www.ers.usda.gov/data-products/food-access-research-atlas/
- County Health Rankings methodology (inspiration): https://www.countyhealthrankings.org/explore-health-rankings/measures-data-sources/methodology
