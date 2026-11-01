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

> 2023–2024 microdata were not available on the FTP. TabNet counts the broad group “malformações congênitas do aparelho circulatório” (Q20–Q28), which is **not** the core CHD definition (Q20–Q26). TabNet values are therefore kept in dedicated columns and are **not** imputed into the core CHD series. 2025 is labelled preliminary. No values were imputed.

### 1.2 Case definition and `CODANOMAL` parsing

`CODANOMAL` can contain several 4-character ICD-10 codes concatenated (e.g. `Q339Q652`, `Q179Q189Q740Q749`). The parser removes separators, splits into blocks of four and separates two groups:

- **CHD core:** Q20–Q26;
- **Other circulatory malformations:** Q27–Q28 (not CHD).

Results:

- 697 records had at least one ICD code;
- 7 core CHD records had **more than one** core CHD code;
- **52 records** met the core CHD case definition;
- **8 records** had a Q27–Q28 code; 1 of them also had a Q20–Q26 code;
- **0** core CHD records had `IDANOMAL ≠ 1`; 3 records had `IDANOMAL = 1` with no code (kept out of the case count but flagged).

`IDANOMAL` is therefore **not** used as the inclusion criterion — the prompt’s concern about losing records through concatenated/missing codes is addressed by parsing all codes.

### 1.3 Annual indicators

| Year | Live births | CHD Q20–Q26 | per 10,000 | Q27–Q28 | per 10,000 | TabNet Q20–Q28 | Status |
|---|---:|---:|---:|---:|---:|---:|---|
| 2010 | 6,882 | 5 | 7.27 | 1 | 1.45 |  | consolidated |
| 2011 | 6,021 | 0 | 0.00 | 0 | 0.00 |  | consolidated |
| 2012 | 6,612 | 2 | 3.02 | 0 | 0.00 |  | consolidated |
| 2013 | 7,424 | 1 | 1.35 | 0 | 0.00 |  | consolidated |
| 2014 | 7,891 | 1 | 1.27 | 0 | 0.00 |  | consolidated |
| 2015 | 8,229 | 3 | 3.65 | 1 | 1.22 |  | consolidated |
| 2016 | 7,516 | 4 | 5.32 | 0 | 0.00 |  | consolidated |
| 2017 | 7,498 | 8 | 10.67 | 0 | 0.00 |  | consolidated |
| 2018 | 7,449 | 2 | 2.68 | 0 | 0.00 |  | consolidated |
| 2019 | 7,166 | 6 | 8.37 | 1 | 1.40 |  | consolidated |
| 2020 | 6,849 | 5 | 7.30 | 0 | 0.00 |  | consolidated |
| 2021 | 6,776 | 4 | 5.90 | 0 | 0.00 |  | consolidated |
| 2022 | 6,361 | 5 | 7.86 | 1 | 1.57 | 5 | consolidated |
| 2023* | 6,252 |  |  |  |  | 5 | aggregate only (broad Q20–Q28) |
| 2024* | 5,870 |  |  |  |  | 5 | aggregate only (broad Q20–Q28) |
| 2025 | 5,924 | 6 | 10.13 | 4 | 6.75 | 9 | **preliminary** |

\* TabNet broad Q20–Q28 group; not directly comparable to the core microdata definition. For 2023–2024 the core CHD cell is left missing. 2025 TabNet (9 broad-group cases) and core microdata (6 Q20–Q26; 4 Q27–Q28) are shown separately.

Overall core microdata: **5.27 per 10,000 live births** (52/98,598), i.e. **0.53 per 1,000** — roughly **one order of magnitude below** the birth prevalence usually reported for CHD (6–9 per 1,000). The most defensible interpretation is **severe under-ascertainment in SINASC**, not a low CHD burden: the absolute number of anomaly records in Campos is only ~25–80 per year across *all* congenital anomalies.

### 1.4 Phenotype distribution (all codes, all years)

**Core CHD (Q20–Q26):**

| Code | n | Typical meaning |
|---|---:|---|
| Q249 | 20 | Congenital malformation of heart, unspecified |
| Q248 | 12 | Other specified congenital malformations of heart |
| Q213 | 5 | Tetralogy of Fallot |
| Q251 | 4 | Coarctation of the aorta |
| Q224 | 3 | Congenital tricuspid stenosis |
| Q208 | 3 | Other congenital malformations of cardiac chambers |
| Q206 | 2 | Congenital stenosis of vena cava |
| Q219 | 2 | Septal defect, unspecified |
| Q212 | 2 | Atrioventricular septal defect |
| Q203 | 1 | Discordant ventriculoarterial connection |
| Q204 | 1 | Double outlet right ventricle |
| Q209 | 1 | Other congenital malformation of cardiac chambers |
| Q221 | 1 | Congenital pulmonary valve stenosis |
| Q245 | 1 | Congenital cardiomyopathy |
| Q233 | 1 | Congenital mitral valve insufficiency |
| Q250 | 1 | Patent ductus arteriosus |
| Q253 | 1 | Congenital stenosis of aortic valve |
| Q268 | 1 | Other congenital malformations of great veins |

**Q27–Q28 (not CHD):** Q270 (7; peripheral vascular system) and Q279 (1; other circulatory malformation).

The dominance of **unspecified** codes (Q249, Q248, Q219) further limits phenotype-specific analyses.

### 1.5 Maternal and neonatal characteristics

| Group | n | Maternal age (mean) | Birth weight (g) | Preterm % | Male % | Caesarean % | Multiple % |
|---|---:|---:|---:|---:|---:|---:|---:|
| CHD core Q20–Q26 | 52 | 28.1 | 2,798 | 21.7 | 51.9 | 86.5 | 3.9 |
| Q27–Q28 (not CHD) | 8 | 32.0 | 3,166 | 0.0 | 62.5 | 75.0 | 12.5 |
| Non-circulatory | 98,539 | 26.3 | 3,165 | 12.1 | 46.9 | 63.4 | 2.2 |

These are descriptive only. With 52 core cases, differences are imprecise and potentially confounded (e.g. caesarean indication, diagnosis at birth). One record had both a core CHD and a Q27–Q28 code and appears in both groups.

---

## 2. SIH/SUS (hospital admissions)

### 2.1 Extraction

192 monthly files (`RDRJ1001.dbc` … `RDRJ2512.dbc`), converted with `pyreaddbc`, parsed in parallel, filtered to `MUNIC_RES = 330100` and primary diagnosis in Q20–Q28. Q20–Q26 (core CHD) and Q27–Q28 (other circulatory) are summarised separately. Large DBF files were deleted after filtering.

- **474 admissions** with primary core CHD diagnosis (Q20–Q26);
- **75 admissions** with primary Q27–Q28 (not CHD), reported separately;
- **12 additional admissions** had core CHD only as a secondary/associated diagnosis; they were evaluated separately and are not included in the 474 primary-diagnosis admissions;
- **16 hospitals**;
- **30 in-hospital deaths (6.33%)**;
- mean length of stay **12.7 days** (median 8);
- total reimbursement **BRL 3,546,864** (nominal);
- **51.9%** of admissions occurred outside Campos dos Goytacazes.

### 2.2 Age distribution (primary CHD)

| Age group | Admissions |
|---|---:|
| <1 year | 178 |
| 1–4 years | 117 |
| 5–9 years | 56 |
| 10–14 years | 28 |
| 15–17 years | 7 |
| ≥18 years | 88 |

The presence of 88 adult admissions reflects adults with congenital heart disease (and the Q20–Q26 codes), not incident cases in childhood.

### 2.3 Referral flow

| Municipality of admission | Admissions |
|---|---:|
| Rio de Janeiro (330455) | 242 |
| Campos dos Goytacazes (330100) | 228 |
| Macaé (330220) | 2 |
| other | 2 |

**Interpretation:** just over half of the admissions occur outside Campos, mainly in Rio de Janeiro, showing a referral pattern to the state capital. Any incidence or access analysis that ignores `MUNIC_MOV` would be biased.

### 2.4 Annual admissions

| Year | Admissions | Deaths | Mortality % | Mean LOS (days) | Mean cost (BRL) |
|---|---:|---:|---:|---:|---:|
| 2010 | 46 | 5 | 10.9 | 12.6 | 5,264 |
| 2011 | 45 | 1 | 2.2 | 12.5 | 5,158 |
| 2012 | 15 | 1 | 6.7 | 14.1 | 6,258 |
| 2013 | 34 | 3 | 8.8 | 16.9 | 9,100 |
| 2014 | 19 | 3 | 15.8 | 16.2 | 10,247 |
| 2015 | 32 | 1 | 3.1 | 7.0 | 5,217 |
| 2016 | 14 | 0 | 0.0 | 10.4 | 5,247 |
| 2017 | 35 | 3 | 8.6 | 11.8 | 6,037 |
| 2018 | 20 | 2 | 10.0 | 16.6 | 7,556 |
| 2019 | 24 | 1 | 4.2 | 9.8 | 5,875 |
| 2020 | 17 | 0 | 0.0 | 17.1 | 6,940 |
| 2021 | 30 | 0 | 0.0 | 10.1 | 5,776 |
| 2022 | 43 | 4 | 9.3 | 11.3 | 8,168 |
| 2023 | 22 | 1 | 4.5 | 11.4 | 6,700 |
| 2024 | 39 | 2 | 5.1 | 18.7 | 13,536 |
| 2025 | 39 | 3 | 7.7 | 9.3 | 10,589 |

Costs are nominal (no deflation); 2025 is a complete year of processing files at the extraction date but may still be revised.

**What SIH does not provide:** unique individuals or readmissions. `N_AIH` identifies an admission authorisation, not a patient. No linkage was attempted.

---

## 3. Environmental data

### 3.1 Source and quality

| Property | Value |
|---|---|
| Source | Open-Meteo Historical Weather API — **ERA5-Land** |
| Model requested | **`era5_land`** (not the API default best-match) |
| Resolution | ~9 km |
| Grid cell returned | −21.800, −41.300; 12 m elevation |
| Period | 2010-01-01 … 2025-12-31 |
| Days | 5,844 |
| Missing Tmax | 0 |
| Heat-wave threshold (Tmax P90) | **33.3 °C** |
| Heat waves (≥3 consecutive days > P90) | **68** |
| Heat-wave days | **353** |

INMET: **station A607** (Campos dos Goytacazes; latitude −21,7167; longitude −41,3500; altitude 25 m; 2010–2025) was downloaded with `BrazilMet` 0.5.0 and used only to validate the ERA5-Land series. It is a station series, not individual exposure. Daily comparison against the fixed `era5_land` series: Tmax r=0.937 (bias +1.20 °C; RMSE 1.78), Tmin r=0.942 (−0.77 °C; 1.20), Tmean r=0.972 (−0.23 °C; 0.67), RH r=0.787 (+1.61 pp; 4.77). The app shows the scatter plots and the comparison table.

PM2.5: **municipal series from VIGIAR** (Ministry of Health), obtained with the R package `vigiar` 0.7.2 (annual 2010–2025 and monthly 2010–2025). The series is area-level: annual values ranged 6.50–9.04 µg/m³ (mean 7.72) and monthly values 3.83–13.84 µg/m³. It is not a local monitoring station and cannot represent personal exposure.

### 3.2 Exposure window

Cardiac organogenesis was defined as **days 21–56 after conception** (weeks 3–8), based on human embryology (heart tube at the end of week 4, looping week 5, chambers week 6, septation weeks 7–8; PMID 38884703).

Conception date was estimated as birth date minus **gestational age minus 14 days** (the approximate interval from LMP to conception). For a 40-week gestation this gives **266 days before birth**, not 280. `SEMAGESTAC` was used when valid; otherwise the category midpoint was used. A main window and early/late windows shifted by **±7 days** were stored for sensitivity analysis. A complete main window was available for **90,258/98,598 births (91.5%)**; where a window existed, climate coverage was **100%**.

| Group | n | Mean Tmax in window | SD | Mean Tmin | RH | Heat days ≥35 °C (proportion) | PM2.5 window mean |
|---|---:|---:|---:|---:|---:|---:|
| All | 98,598 | 28.57 | 2.28 | 20.62 | 75.9 | 3.7% | 7.73 |
| CHD core Q20–Q26 | 52 | 28.91 | 2.55 | 20.85 | 75.3 | 5.9% | 7.69 |
| Non-CHD | 98,546 | 28.57 | 2.28 | 20.62 | 75.9 | 3.7% | 7.73 |

---

## 4. Exploratory models

All inferential p-values reported below and in the app are adjusted for multiple testing with the Benjamini–Hochberg procedure (BH-FDR). The adjustment family comprises the birth-level models (five exposures), the season-adjusted and mutual-adjustment models, and the monthly count model. **No association survives FDR control at q < 0.05.**

### 4.1 Birth-level logistic regression

Outcome: **CHD core Q20–Q26** (0/1). Exposure: area-level mean Tmax during the organogenesis window (z-score). Adjustment: year (linear), maternal age (linear), infant sex. n = 83,040; events = 47.

| Exposure | OR per SD | 95% CI | p | q (FDR) | OR per IQR |
|---|---:|---|---:|---:|---:|
| Tmax window mean | **1.155** | 0.870–1.535 | 0.318 | 0.509 | 1.230 |
| Tmin window mean | 1.092 | 0.815–1.464 | 0.555 | 0.592 | 1.168 |
| Heat-day proportion | **1.221** | 1.006–1.480 | 0.043 | 0.509 | 1.145 |
| Relative humidity | 0.889 | 0.664–1.188 | 0.426 | 0.524 | 0.840 |
| PM2.5 (VIGIAR) | 0.842 | 0.625–1.134 | 0.257 | 0.509 | 0.803 |

**Small-sample sensitivity.** Firth penalised logistic regression gave Tmax **OR 1.159 (0.869–1.532), p = 0.304, q = 0.509** and PM2.5 **OR 0.844 (0.622–1.132), p = 0.255, q = 0.509**.

**Clustering.** Cluster-robust standard errors by month of conception (163 clusters) gave Tmax **OR 1.155 (0.829–1.611), p = 0.394, q = 0.524** — the confidence interval includes 1.

**Socio-economic sensitivity.** Firth model additionally adjusted for education (≥8 years), race (white vs non-white), number of prenatal visits and multiple gestation: Tmax **OR 1.187 (0.889–1.571), p = 0.236, q = 0.509**, n = 79,919 and 46 events.

Season-adjusted sensitivity (quarter of conception fixed effects): **OR 1.357 per SD (0.914–2.013), p = 0.130, q = 0.509**.

Mutual-adjustment model (PM2.5 + Tmax, year, age, sex): PM2.5 **OR 0.872 per SD (0.640–1.189), p = 0.386, q = 0.524**; Tmax **OR 1.106 (0.822–1.487), p = 0.506, q = 0.578**. The PM2.5 association is null in this municipality.

**Gestational-age sensitivity (±7 days).** Main window **OR 1.155 (0.870–1.535)**; early window **1.221 (0.922–1.618), p = 0.164**; late window **1.071 (0.803–1.428), p = 0.641**. The direction is not stable across plausible shifts, reinforcing the exploratory interpretation.

Leave-one-year-out: OR per SD ranged **1.136–1.608**; p ranged 0.024–0.546 and q (within the LOO family) 0.224–0.546; no single year changed the direction.

**Colinearity.** Correlations and VIF are in `outputs/tables/exposure_correlation.csv` and `exposure_vif.csv`; exposures are modelled separately and the only mutual-adjustment model is PM2.5 + Tmax.

### 4.2 Monthly count model

CHD core counts by month of conception (165 months with ≥30 births; 50 cases), Poisson with log(live births) offset, adjusted for year. Dispersion 1.236 (Poisson selected). **RR 1.211 per SD (0.918–1.599), p = 0.176, q = 0.509**; RR 1.333 per IQR. The monthly model does not support a heat effect.

### 4.3 Julia measurement-error simulation

The gestational-window uncertainty was also propagated with a well-delimited Julia module (`julia/gestational_window_simulation.jl`). For each birth, the module samples a window shift from a normal distribution (`SD = 3.5` days when `SEMAGESTAC` is available; `7` days for the categorical midpoint), interpolates Tmax between the main, −7-day and +7-day windows, and refits the same birth-level logistic model. This is a **Monte Carlo measurement-error sensitivity analysis**, not a full Bayesian hierarchical model.

| Scenario | OR per SD | 95% CI |
|---|---:|---:|
| Fixed −7 days | 1.224 | 0.921–1.628 |
| Fixed −3.5 days | 1.193 | 0.896–1.589 |
| Main window | 1.159 | 0.870–1.545 |
| Fixed +3.5 days | 1.118 | 0.837–1.493 |
| Fixed +7 days | 1.075 | 0.804–1.438 |
| Monte Carlo, 500 replicates (median) | 1.157 | simulation interval 1.116–1.202 |

None of the fixed scenarios excluded 1, and none of the 500 Monte Carlo replicates produced a 95% CI excluding 1. Individual measurement error tends to average out; the systematic window shift is the dominant source of sensitivity. The module writes `outputs/tables/julia_gestational_window_simulation.csv` and `reports/julia_gestational_window_simulation.json`; individual-level input remains local.

### 4.4 Interpretation (enforced)

- After correcting the conception window, the birth-level Tmax association is **null** (OR 1.155; p = 0.318), and the monthly model is also null (RR 1.211; p = 0.176).
- The heat-day proportion has a nominal p = 0.043, but it does **not** survive FDR correction (q = 0.509) and is sensitive to the ±7-day gestational window.
- No model survives FDR control at q < 0.05.
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
