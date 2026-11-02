# 07: Local epidemiological and environmental methods and results

Period: **2010-01-01 to 2025-12-31**; municipality: Campos dos Goytacazes, RJ (IBGE 330100). Extraction date: **2026-10-31**; case-definition correction to the full **Q20–Q28** group: **2026-11-02**.

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

> 2023–2024 microdata were not available on the FTP. TabNet counts the group “malformações congênitas do aparelho circulatório” (Q20–Q28), which is the same ICD group as the study outcome. TabNet values are still kept in dedicated columns and are **not** imputed into the birth-level series because the extraction route differs (TabNet aggregate vs. birth-level `CODANOMAL` parser). 2025 is labelled preliminary. No values were imputed.

### 1.2 Case definition and `CODANOMAL` parsing

`CODANOMAL` can contain several 4-character ICD-10 codes concatenated (e.g. `Q339Q652`, `Q179Q189Q740Q749`). The parser removes separators and splits the content into blocks of four. The primary case group is the **full Q20–Q28 chapter** of congenital malformations of the circulatory system:

- **Q20–Q26:** cardiac chambers and connections, septa, valves and great vessels;
- **Q27–Q28:** peripheral vascular malformations and other circulatory malformations. These are **inside** the primary outcome and are also reported as a descriptive subgroup.

Results:

- 697 records had at least one ICD code;
- 8 records had **more than one** Q20–Q28 code;
- **59 records** met the Q20–Q28 case definition;
- 51 records had Q20–Q26 codes without a Q27–Q28 code; **8 records** had a Q27–Q28 code, and 1 of these also had a Q20–Q26 code;
- **0** Q20–Q28 records had `IDANOMAL ≠ 1`; 3 records had `IDANOMAL = 1` with no code (kept out of the case count but flagged).

`IDANOMAL` is therefore **not** used as the inclusion criterion; the concern about losing records through concatenated/missing codes is addressed by parsing all codes.

### 1.3 Annual indicators

| Year | Live births | Q20–Q28 | per 1,000 | of which Q27–Q28 | Q27–Q28/1,000 | TabNet Q20–Q28 | Status |
|---|---:|---:|---:|---:|---:|---:|---|
| 2010 | 6,882 | 6 | 0.87 | 1 | 0.15 |  | consolidated |
| 2011 | 6,021 | 0 | 0.00 | 0 | 0.00 |  | consolidated |
| 2012 | 6,612 | 2 | 0.30 | 0 | 0.00 |  | consolidated |
| 2013 | 7,424 | 1 | 0.13 | 0 | 0.00 |  | consolidated |
| 2014 | 7,891 | 1 | 0.13 | 0 | 0.00 |  | consolidated |
| 2015 | 8,229 | 4 | 0.49 | 1 | 0.12 |  | consolidated |
| 2016 | 7,516 | 4 | 0.53 | 0 | 0.00 |  | consolidated |
| 2017 | 7,498 | 8 | 1.07 | 0 | 0.00 |  | consolidated |
| 2018 | 7,449 | 2 | 0.27 | 0 | 0.00 |  | consolidated |
| 2019 | 7,166 | 7 | 0.98 | 1 | 0.14 |  | consolidated |
| 2020 | 6,849 | 5 | 0.73 | 0 | 0.00 |  | consolidated |
| 2021 | 6,776 | 4 | 0.59 | 0 | 0.00 |  | consolidated |
| 2022 | 6,361 | 6 | 0.94 | 1 | 0.16 | 5 | consolidated |
| 2023* | 6,252 |  |  |  |  | 5 | aggregate only (Q20–Q28) |
| 2024* | 5,870 |  |  |  |  | 5 | aggregate only (Q20–Q28) |
| 2025 | 5,924 | 9 | 1.52 | 4 | 0.68 | 9 | **preliminary** |

\* TabNet aggregate for the same Q20–Q28 group; the birth-level series is left missing for 2023–2024 because microdata were unavailable. 2025 TabNet (9 aggregate cases) and the birth-level series (9 Q20–Q28 records, 4 with a Q27–Q28 code) are shown separately.

Overall Q20–Q28 microdata: **0.60 per 1,000 live births** (59/98,598), roughly **one order of magnitude below** the birth prevalence usually reported for congenital heart defects (6–9 per 1,000). The most defensible interpretation is **severe under-ascertainment in SINASC**, not a low burden of congenital circulatory malformations: the absolute number of anomaly records in Campos is only ~25–80 per year across *all* congenital anomalies.

### 1.4 Phenotype distribution (all codes, all years)

**Q20–Q28 group (all study codes):**

| Code | n | Typical meaning |
|---|---:|---|
| Q249 | 20 | Congenital malformation of heart, unspecified |
| Q248 | 12 | Other specified congenital malformations of heart |
| Q270 | 7 | Congenital malformation of peripheral vascular system, unspecified |
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
| Q279 | 1 | Other congenital malformation of circulatory system, unspecified |

**Q27–Q28 subgroup:** Q270 (7; peripheral vascular system) and Q279 (1; other circulatory malformation). The Q279 record also carried Q251 and therefore contributes to both Q20–Q26 and Q27–Q28.

The dominance of **unspecified** codes (Q249, Q248, Q219) further limits phenotype-specific analyses.

### 1.5 Maternal and neonatal characteristics

| Group | n | Maternal age (mean) | Birth weight (g) | Preterm % | Male % | Caesarean % | Multiple % |
|---|---:|---:|---:|---:|---:|---:|---:|
| Q20–Q28 (primary outcome) | 59 | 28.5 | 2,844 | 19.2 | 52.5 | 84.8 | 5.1 |
| Q20–Q26 only (without Q27–Q28) | 51 | 27.9 | 2,794 | 22.2 | 51.0 | 86.3 | 3.9 |
| Q27–Q28 subgroup | 8 | 32.0 | 3,166 | 0.0 | 62.5 | 75.0 | 12.5 |
| Non-circulatory | 98,539 | 26.3 | 3,165 | 12.1 | 46.9 | 63.4 | 2.2 |

These are descriptive only. With 59 Q20–Q28 cases, differences are imprecise and potentially confounded (e.g. caesarean indication, diagnosis at birth). One record had both a Q20–Q26 and a Q27–Q28 code and appears in both components.

---

## 2. SIH/SUS (hospital admissions)

### 2.1 Extraction

192 monthly files (`RDRJ1001.dbc` … `RDRJ2512.dbc`), converted with `pyreaddbc`, parsed in parallel, filtered to `MUNIC_RES = 330100` and primary diagnosis in Q20–Q28. Q20–Q28 is the main outcome; Q27–Q28 are summarised as a descriptive subgroup. Large DBF files were deleted after filtering.

- **549 admissions** with primary diagnosis in Q20–Q28;
- **75 admissions** with primary Q27–Q28, included in the 549 and also reported as a subgroup;
- **12 additional admissions** had Q20–Q28 only as a secondary/associated diagnosis; they were evaluated separately and are not included in the 549 primary-diagnosis admissions;
- **18 hospitals**;
- **33 in-hospital deaths (6.01%)**;
- mean length of stay **12.0 days**;
- total reimbursement **BRL 4,155,684** (nominal);
- **55.0%** of admissions occurred outside Campos dos Goytacazes.

### 2.2 Age distribution (primary Q20–Q28)

| Age group | Admissions |
|---|---:|
| <1 year | 193 |
| 1–4 years | 121 |
| 5–9 years | 57 |
| 10–14 years | 31 |
| 15–17 years | 9 |
| ≥18 years | 138 |

The presence of 138 adult admissions reflects adults with congenital circulatory malformations (including Q20–Q28 codes), not incident cases in childhood. The Q27–Q28 subgroup is adult-heavy and helps explain the increase in adult admissions relative to the Q20–Q26 component alone.

### 2.3 Referral flow

| Municipality of admission | Admissions |
|---|---:|
| Rio de Janeiro (330455) | 245 |
| Campos dos Goytacazes (330100) | 247 |
| Macaé (330220) | 50 |
| other | 7 |

**Interpretation:** just over half of the admissions occur outside Campos, mainly in Rio de Janeiro, showing a referral pattern to the state capital. Any incidence or access analysis that ignores `MUNIC_MOV` would be biased.

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
| Source | Open-Meteo Historical Weather API: **ERA5-Land** |
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
|---|---:|---:|---:|---:|---:|---:|---:|
| All | 98,598 | 28.57 | 2.28 | 20.62 | 75.9 | 3.7% | 7.73 |
| Q20–Q28 | 59 | 28.90 | 2.45 | 20.80 | 75.3 | 5.5% | 7.73 |
| Non-circulatory | 98,539 | 28.57 | 2.28 | 20.62 | 75.9 | 3.7% | 7.73 |

---

## 4. Exploratory models

All inferential p-values reported below and in the app are adjusted for multiple testing with the Benjamini–Hochberg procedure (BH-FDR). The adjustment family comprises the birth-level models (five exposures), the season-adjusted and mutual-adjustment models, and the monthly count model. **No association survives FDR control at q < 0.05.**

### 4.1 Birth-level logistic regression

Outcome: **Q20–Q28** (0/1). Exposure: area-level mean Tmax during the organogenesis window (z-score). Adjustment: year (linear), maternal age (linear), infant sex. n = 83,040; events = 53.

| Exposure | OR per SD | 95% CI | p | q (FDR) | OR per IQR |
|---|---:|---|---:|---:|---:|
| Tmax window mean | **1.149** | 0.876–1.507 | 0.315 | 0.501 | 1.220 |
| Tmin window mean | 1.063 | 0.805–1.403 | 0.666 | 0.710 | 1.113 |
| Heat-day proportion | **1.199** | 0.988–1.454 | 0.066 | 0.501 | 1.131 |
| Relative humidity | 0.890 | 0.675–1.173 | 0.407 | 0.501 | 0.841 |
| PM2.5 (VIGIAR) | 0.857 | 0.650–1.129 | 0.272 | 0.501 | 0.821 |

**Small-sample sensitivity.** Firth penalised logistic regression gave Tmax **OR 1.153 (0.876–1.505), p = 0.301, q = 0.501** and PM2.5 **OR 0.859 (0.648–1.127), p = 0.269, q = 0.501**.

**Clustering.** Cluster-robust standard errors by month of conception (163 clusters) gave Tmax **OR 1.149 (0.849–1.555), p = 0.368, q = 0.501**: the confidence interval includes 1.

**Socio-economic sensitivity.** Firth model additionally adjusted for education (≥8 years), race (white vs non-white), number of prenatal visits and multiple gestation: Tmax **OR 1.179 (0.896–1.542), p = 0.231, q = 0.501**, n = 79,919 and 52 events.

Season-adjusted sensitivity (quarter of conception fixed effects): **OR 1.389 per SD (0.954–2.023), p = 0.087, q = 0.501**.

Mutual-adjustment model (PM2.5 + Tmax, year, age, sex): PM2.5 **OR 0.886 per SD (0.666–1.179), p = 0.407, q = 0.501**; Tmax **OR 1.104 (0.832–1.466), p = 0.492, q = 0.562**. The PM2.5 association is null in this municipality.

**Gestational-age sensitivity (±7 days).** Main window **OR 1.149 (0.876–1.507)**; early window **1.219 (0.931–1.595), p = 0.150**; late window **1.038 (0.787–1.368), p = 0.793**. The direction is not stable across plausible shifts, reinforcing the exploratory interpretation.

Leave-one-year-out: OR per SD ranged **1.188–1.598**; p ranged 0.019–0.397 and q (within the LOO family) 0.153–0.397; no single year changed the direction.

**Colinearity.** Correlations and VIF are in `outputs/tables/exposure_correlation.csv` and `exposure_vif.csv`; exposures are modelled separately and the only mutual-adjustment model is PM2.5 + Tmax.

### 4.2 Monthly count model

Q20–Q28 counts by month of conception (165 months with ≥30 births; 56 cases), Poisson with log(live births) offset, adjusted for year. Dispersion 1.219 (Poisson selected). **RR 1.187 per SD (0.909–1.549), p = 0.208, q = 0.501**; RR 1.292 per IQR. The monthly model does not support a heat effect.

### 4.3 Julia measurement-error simulation

The gestational-window uncertainty was also propagated with a well-delimited Julia module (`julia/gestational_window_simulation.jl`). For each birth, the module samples a window shift from a normal distribution (`SD = 3.5` days when `SEMAGESTAC` is available; `7` days for the categorical midpoint), interpolates Tmax between the main, −7-day and +7-day windows, and refits the same birth-level logistic model. This is a **Monte Carlo measurement-error sensitivity analysis**, not a full Bayesian hierarchical model.

| Scenario | OR per SD | 95% CI |
|---|---:|---:|
| Fixed −7 days | 1.222 | 0.930–1.604 |
| Fixed −3.5 days | 1.189 | 0.904–1.562 |
| Main window | 1.152 | 0.876–1.516 |
| Fixed +3.5 days | 1.097 | 0.832–1.447 |
| Fixed +7 days | 1.041 | 0.787–1.377 |
| Monte Carlo, 500 replicates (median) | 1.144 | simulation interval 1.106–1.185 |

None of the fixed scenarios excluded 1, and none of the 500 Monte Carlo replicates produced a 95% CI excluding 1. Individual measurement error tends to average out; the systematic window shift is the dominant source of sensitivity. The module writes `outputs/tables/julia_gestational_window_simulation.csv` and `reports/julia_gestational_window_simulation.json`; individual-level input remains local.

### 4.4 Interpretation (enforced)

- The birth-level Tmax association is **null** (OR 1.149; p = 0.315), and the monthly model is also null (RR 1.187; p = 0.208).
- The heat-day proportion has a nominal p = 0.066; it does **not** survive FDR correction (q = 0.501) and is sensitive to the ±7-day gestational window.
- No model survives FDR control at q < 0.05.
- The exposure is **ecological**: every birth in the same window receives the same value.
- Gestational age is measured at birth and may be misclassified; conception dates are estimates.
- Q20–Q28 ascertainment in SINASC is severely incomplete and may be differential by year/season (e.g. diagnosis at birth vs later).
- The season-adjusted model controls only for quarter, not for calendar time trends beyond a linear year term.
- Therefore the result is **hypothesis-generating** and is not used to assert that heat causes congenital circulatory malformations in Campos. The graph does not contain a heat→CHD edge based on this local model; the heat→ASD edge comes from the published cohort (PMID 27494594).

---

## 5. What the local data can and cannot support

**Can support:** descriptive burden of reported anomalies; hospital utilisation, cost, mortality and referral flow; ecological co-variation of area-level climate with reported Q20–Q28 timing; data-quality research.

**Cannot support:** CHD incidence or prevalence; individual exposure; causal inference; gene–environment interaction; “number of affected children” (SIH); mechanism.

**Minimum improvements before aetiological analysis:** linkage to live-birth cohorts or notification systems with postnatal diagnosis; local air-quality monitoring; individual-level exposure (residence geocoding + land-use regression); congenital anomaly registry with active surveillance.
