# 07 — Local epidemiological and environmental methods and results

Period: **2010-01-01 to 2025-12-31**; municipality: Campos dos Goytacazes, RJ (IBGE 330100). Extraction date: **2026-10-31**.

---

## 1. SINASC (live births)

### 1.1 Files and coverage

| Year | File | Status | Births (Campos) |
|---|---|---|---:|
| 2010–2022 | `DNRJ{year}.dbc` (NOV/DNRES) | consolidated | 6,882–8,229/year |
| 2023 | `nvrj23.dbf` (TabNet only) | **aggregate only** | 6,252 |
| 2024 | `nvrj24.dbf` (TabNet only) | **aggregate only** | 5,870 |
| 2025 | `DNRJ2025.dbc` (PRELIM/DNRES) | **preliminary** | 5,924 |

Total: **98,598 live births** to resident mothers.

> 2023–2024 microdata were not available on the FTP; aggregate counts were obtained from TabNet and are kept in a separate series, because TabNet counts only the “malformações congênitas do aparelho circulatório” group while the microdata parser counts any Q20–Q28 code. 2025 is labelled preliminary. No values were imputed.

### 1.2 Case definition and `CODANOMAL` parsing

`CODANOMAL` can contain several 4-character ICD-10 codes concatenated (e.g. `Q339Q652`, `Q179Q189Q740Q749`). The parser removes separators, splits into blocks of four and keeps every code in Q20–Q28:

- 697 records had at least one ICD code;
- 8 CHD records had **more than one** CHD code;
- **59 records** met the CHD case definition;
- **0** CHD records had `IDANOMAL ≠ 1`; 3 records had `IDANOMAL = 1` with no code (kept out of the case count but flagged).

`IDANOMAL` is therefore **not** used as the inclusion criterion — the prompt’s concern about losing records through concatenated/missing codes is addressed by parsing all codes.

### 1.3 Annual indicators

| Year | Live births | CHD cases | per 10,000 LB | per 1,000 LB | Status |
|---|---:|---:|---:|---:|---|
| 2010 | 6,882 | 6 | 8.72 | 0.87 | consolidated |
| 2011 | 6,021 | 0 | 0.00 | 0.00 | consolidated |
| 2012 | 6,612 | 2 | 3.02 | 0.30 | consolidated |
| 2013 | 7,424 | 1 | 1.35 | 0.13 | consolidated |
| 2014 | 7,891 | 1 | 1.27 | 0.13 | consolidated |
| 2015 | 8,229 | 4 | 4.86 | 0.49 | consolidated |
| 2016 | 7,516 | 4 | 5.32 | 0.53 | consolidated |
| 2017 | 7,498 | 8 | 10.67 | 1.07 | consolidated |
| 2018 | 7,449 | 2 | 2.68 | 0.27 | consolidated |
| 2019 | 7,166 | 7 | 9.77 | 0.98 | consolidated |
| 2020 | 6,849 | 5 | 7.30 | 0.73 | consolidated |
| 2021 | 6,776 | 4 | 5.90 | 0.59 | consolidated |
| 2022 | 6,361 | 6 | 9.43 | 0.94 | consolidated |
| 2023* | 6,252 | 5 | 8.00 | 0.80 | aggregate (TabNet) |
| 2024* | 5,870 | 5 | 8.52 | 0.85 | aggregate (TabNet) |
| 2025 | 5,924 | 9 | 15.19 | 1.52 | **preliminary** |

\* TabNet group definition; not directly comparable to the microdata any-code definition. 2025 TabNet (9 cases, 5,924 births) matches the microdata exactly, supporting internal consistency.

Overall microdata: **5.98 per 10,000 live births** (59/98,598), i.e. **0.6 per 1,000** — roughly **one order of magnitude below** the birth prevalence usually reported for CHD (6–9 per 1,000). The most defensible interpretation is **severe under-ascertainment in SINASC**, not a low CHD burden: the absolute number of anomaly records in Campos is only ~25–80 per year across *all* congenital anomalies.

### 1.4 Phenotype distribution (all codes, all years)

| Code | n | Typical meaning |
|---|---:|---|
| Q249 | 20 | Congenital malformation of heart, unspecified |
| Q248 | 12 | Other specified congenital malformations of heart |
| Q270 | 7 | Congenital malformation of peripheral vascular system |
| Q213 | 5 | Tetralogy of Fallot |
| Q251 | 4 | Coarctation of the aorta |
| Q224 | 3 | Congenital tricuspid stenosis |
| Q208 | 3 | Other congenital malformations of cardiac chambers |
| Q206 | 2 | Congenital stenosis of vena cava |
| Q219 | 2 | Septal defect, unspecified |
| Q212 | 2 | Atrioventricular septal defect |
| Q203 | 1 | Discordant ventriculoarterial connection |
| Q204 | 1 | Double outlet right ventricle |

The dominance of **unspecified** codes (Q249, Q248, Q219) further limits phenotype-specific analyses.

### 1.5 Maternal and neonatal characteristics

| Group | n | Maternal age (mean) | Birth weight (g) | Preterm % | Male % | Caesarean % | Multiple % |
|---|---:|---:|---:|---:|---:|---:|---:|
| CHD | 59 | 28.5 | 2,844 | 19.2 | 52.5 | 84.7 | 5.1 |
| Non-CHD | 98,539 | 26.3 | 3,165 | 12.1 | 46.9 | 63.4 | 2.2 |

These are descriptive only. With 59 cases, differences are imprecise and potentially confounded (e.g. caesarean indication, diagnosis at birth).

---

## 2. SIH/SUS (hospital admissions)

### 2.1 Extraction

192 monthly files (`RDRJ1001.dbc` … `RDRJ2512.dbc`), converted with `pyreaddbc`, parsed in parallel, filtered to `MUNIC_RES = 330100` and `DIAG_PRINC` in Q20–Q28. Large DBF files were deleted after filtering.

- **549 admissions** with primary CHD diagnosis;
- **12 additional admissions** had CHD only as a secondary/associated diagnosis; they were evaluated separately and are not included in the 549 primary-diagnosis admissions used in the main tables;
- **18 hospitals**;
- **33 in-hospital deaths (6.0%)**;
- mean length of stay **12.0 days** (median 7);
- total reimbursement **BRL 4,155,684** (nominal);
- **55.0%** of admissions occurred outside Campos dos Goytacazes.

### 2.2 Age distribution (primary CHD)

| Age group | Admissions |
|---|---:|
| <1 year | 193 |
| 1–4 years | 121 |
| 5–9 years | 57 |
| 10–14 years | 31 |
| 15–17 years | 9 |
| ≥18 years | 138 |

The presence of 138 adult admissions reflects adults with congenital heart disease (and the Q20–Q28 codes), not incident cases in childhood.

### 2.3 Referral flow

| Municipality of admission | Admissions |
|---|---:|
| Campos dos Goytacazes (330100) | 247 |
| Rio de Janeiro (330455) | 245 |
| Macaé (330220) | 50 |
| Itaperuna (330390) | 5 |
| other | 1 |

**Interpretation:** nearly half of the admissions occur in Rio de Janeiro, showing a referral pattern to the state capital. Any incidence or access analysis that ignores `MUNIC_MOV` would be biased.

### 2.4 Annual admissions

| Year | Admissions | Deaths | Mortality % | Mean LOS (days) | Mean cost (BRL) |
|---|---:|---:|---:|---:|---:|
| 2010 | 48 | 5 | 10.4 | 12.2 | 6,352 |
| 2011 | 49 | 1 | 2.0 | 12.5 | 5,370 |
| 2012 | 15 | 1 | 6.7 | 14.1 | 6,258 |
| 2013 | 38 | 3 | 7.9 | 15.8 | 8,658 |
| 2014 | 21 | 3 | 14.3 | 16.1 | 9,749 |
| 2015 | 33 | 1 | 3.0 | 7.0 | 5,359 |
| 2016 | 20 | 0 | 0.0 | 11.4 | 7,199 |
| 2017 | 43 | 4 | 9.3 | 10.6 | 5,839 |
| 2018 | 26 | 2 | 7.7 | 13.8 | 6,786 |
| 2019 | 29 | 1 | 3.4 | 9.0 | 5,770 |
| 2020 | 23 | 0 | 0.0 | 15.6 | 6,784 |
| 2021 | 35 | 0 | 0.0 | 9.2 | 6,405 |
| 2022 | 48 | 4 | 8.3 | 11.4 | 8,626 |
| 2023 | 27 | 1 | 3.7 | 10.9 | 7,592 |
| 2024 | 46 | 3 | 6.5 | 16.9 | 12,383 |
| 2025 | 48 | 4 | 8.3 | 8.3 | 9,907 |

Costs are nominal (no deflation); 2025 is a complete year of processing files at the extraction date but may still be revised.

**What SIH does not provide:** unique individuals or readmissions. `N_AIH` identifies an admission authorisation, not a patient. No linkage was attempted.

---

## 3. Environmental data

### 3.1 Source and quality

| Property | Value |
|---|---|
| Source | ERA5/ERA5-Land via Open-Meteo Historical Weather API |
| Grid cell returned | −21.757, −41.354; 12 m elevation |
| Period | 2010-01-01 … 2025-12-31 |
| Days | 5,844 |
| Missing Tmax | 0 |
| Heat-wave threshold (Tmax P90) | **34.2 °C** |
| Heat waves (≥3 consecutive days > P90) | **73** |
| Heat-wave days | **363** |

PM2.5: **municipal series from VIGIAR** (Ministry of Health), obtained with the R package `vigiar` 0.7.2 (annual 2010–2025 and monthly 2010–2025). The series is area-level: annual values ranged 6.50–9.04 µg/m³ (mean 7.72) and monthly values 3.83–13.84 µg/m³. It is not a local monitoring station and cannot represent personal exposure.

### 3.2 Exposure window

Cardiac organogenesis was defined as **days 21–56 after conception** (weeks 3–8), based on human embryology (heart tube at the end of week 4, looping week 5, chambers week 6, septation weeks 7–8; PMID 38884703).

Conception date was estimated as birth date minus gestational age (`SEMAGESTAC`, weeks; categorical midpoint when missing). A complete window was available for **90,008/98,598 births (91.3%)**; where a window existed, climate coverage was **100%**.

| Group | n | Mean Tmax in window | SD | Mean Tmin | RH | Heat days ≥35 °C (proportion) | PM2.5 window mean |
|---|---:|---:|---:|---:|---:|---:|
| All | 98,598 | 29.05 | 2.43 | 20.50 | 76.0 | 6.0% | 7.73 |
| CHD | 59 | 29.91 | 2.50 | 20.88 | 75.2 | 8.5% | 7.73 |
| Non-CHD | 98,539 | 29.04 | 2.43 | 20.50 | 76.0 | 6.0% | 7.73 |

---

## 4. Exploratory models

All inferential p-values reported below and in the app are adjusted for multiple testing with the Benjamini–Hochberg procedure (BH-FDR). The adjustment family comprises the birth-level models (five exposures), the season-adjusted and mutual-adjustment models, and the monthly count model. **No association survives FDR control at q < 0.05.**

### 4.1 Birth-level logistic regression

Outcome: CHD (0/1). Exposure: area-level mean Tmax during the organogenesis window (z-score). Adjustment: year (linear), maternal age (linear), infant sex. n = 90,008; events = 56.

| Exposure | OR per SD | 95% CI | p | q (FDR) | OR per IQR |
|---|---:|---|---:|---:|---:|
| Tmax window mean | **1.30** | 1.00–1.69 | 0.048 | 0.153 | 1.50 |
| Tmin window mean | 1.19 | 0.91–1.56 | 0.20 | 0.295 | 1.35 |
| Heat-day proportion | 1.10 | 0.89–1.36 | 0.36 | 0.473 | 1.06 |
| Relative humidity | 0.82 | 0.63–1.07 | 0.13 | 0.228 | 0.75 |
| PM2.5 (VIGIAR) | 0.91 | 0.70–1.18 | 0.47 | 0.509 | 0.89 |

**Small-sample sensitivity.** Firth penalised logistic regression gave Tmax **OR 1.31 (1.00–1.69), p = 0.047, q = 0.153** and PM2.5 **OR 0.91 (0.70–1.18), p = 0.47, q = 0.509**.

**Clustering.** Cluster-robust standard errors by month of conception (170 clusters) gave Tmax **OR 1.30 (0.98–1.72), p = 0.065, q = 0.153** — the confidence interval now includes 1.

**Socio-economic sensitivity.** Firth model additionally adjusted for education (≥8 years), race (white vs non-white), number of prenatal visits and multiple gestation: Tmax **OR 1.33 (1.02–1.73), p = 0.033, q = 0.153**, n = 86,090 and 55 events.

Season-adjusted sensitivity (quarter of conception fixed effects): **OR 1.65 per SD (1.13–2.42), p = 0.009, q = 0.122**.

Mutual-adjustment model (PM2.5 + Tmax, year, age, sex): PM2.5 **OR 1.01 per SD (0.77–1.32), p = 0.97, q = 0.97**; Tmax **OR 1.30 (0.98–1.74), p = 0.071, q = 0.153**. The PM2.5 association is null in this municipality and does not explain the heat signal.

Leave-one-year-out: OR per SD ranged **1.47–1.86**; p ranged 0.002–0.057 and q (within the LOO family) 0.019–0.057; no single year changed the direction.

**Colinearity.** Tmax and Tmin are strongly correlated (r = 0.88) and heat-day proportion is correlated with Tmax (r = 0.75). In a model containing all five exposures the VIF for Tmax is 10.4, so the study does **not** fit a five-exposure model; each exposure is modelled separately and the only mutual-adjustment model is PM2.5 + Tmax, whose correlation is low (r = −0.26). Correlations and VIF are in `outputs/tables/exposure_correlation.csv` and `exposure_vif.csv`.

### 4.2 Monthly count model

CHD counts by month of conception (163 months with ≥30 births; 56 cases), Poisson with log(live births) offset, adjusted for year. Dispersion 1.11 (no overdispersion). **RR 1.22 per SD (0.94–1.60), p = 0.14, q = 0.25**; RR 1.38 per IQR.

### 4.3 Interpretation (enforced)

- The birth-level and monthly models **disagree** (positive borderline vs null). This is expected with 56–59 events and an area-level exposure.
- The nominal p-values (0.049 and 0.010) do **not** survive FDR correction across the model family (q = 0.153 and 0.122), so the heat signal remains hypothesis-generating.
- The exposure is **ecological**: every birth in the same window receives the same value.
- Gestational age is measured at birth and may be misclassified; conception dates are estimates.
- CHD ascertainment in SINASC is severely incomplete and may be differential by year/season (e.g. diagnosis at birth vs later).
- The season-adjusted model controls only for quarter, not for calendar time trends beyond a linear year term.
- Therefore the result is **hypothesis-generating** and is not used to assert that heat causes CHD in Campos. The graph does not contain a heat→CHD edge based on this local model; the heat→ASD edge comes from the published cohort (PMID 27494594).

---

## 5. What the local data can and cannot support

**Can support:** descriptive burden of reported anomalies; hospital utilisation, cost, mortality and referral flow; ecological co-variation of area-level climate with reported CHD timing; data-quality research.

**Cannot support:** CHD incidence or prevalence; individual exposure; causal inference; gene–environment interaction; “number of affected children” (SIH); mechanism.

**Minimum improvements before aetiological analysis:** linkage to live-birth cohorts or notification systems with postnatal diagnosis; local air-quality monitoring; individual-level exposure (residence geocoding + land-use regression); congenital anomaly registry with active surveillance.
