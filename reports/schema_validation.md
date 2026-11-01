# Schema validation

Generated: 2026-11-01T02:32:03Z

**Result: PASSED**

- OK — `columns:outputs/graph/nodes.csv` — 2238 rows
- OK — `columns:outputs/graph/relations.csv` — 4117 rows
- OK — `columns:outputs/graph/evidence.csv` — 4613 rows
- OK — `columns:outputs/tables/exploratory_models.csv` — 13 rows
- OK — `columns:outputs/tables/hypothesis_candidates.csv` — 5 rows
- OK — `columns:data_processed/pm25_campos_anual.csv` — 16 rows
- OK — `columns:data_processed/pm25_campos_mensal.csv` — 192 rows
- OK — `columns:app/data/models.csv` — 13 rows
- OK — `columns:outputs/tables/sensitivity_leave_one_year_out.csv` — 14 rows
- OK — `columns:outputs/tables/exposure_correlation.csv` — 5 rows
- OK — `columns:outputs/tables/exposure_vif.csv` — 5 rows
- OK — `columns:data_processed/inmet_campos_daily.csv` — 5754 rows
- OK — `columns:outputs/tables/inmet_era5_comparison.csv` — 4 rows
- OK — `columns:app/data/inmet_daily.csv` — 5754 rows
- OK — `columns:app/data/inmet_comparison.csv` — 4 rows
- OK — `fdr:outputs/tables/exploratory_models.csv` — ok
- OK — `fdr:outputs/tables/hypothesis_candidates.csv` — ok
- OK — `inmet:rows` — 5754 days
- OK — `inmet:unique_dates` — ok
- OK — `inmet:station` — {'A607'}
- OK — `inmet:tmax_range` — -10 to 55 C
- OK — `inmet:rh_range` — 0-100 %
- OK — `pm25:monthly_rows` — 192 rows
- OK — `pm25:monthly_unique` — ok
- OK — `pm25:monthly_range` — 0-500 µg/m3
- OK — `pm25:monthly_complete` — 0 missing
- OK — `pm25:annual_years` — 16 rows
- OK — `app:no_individual_data` — ok
- OK — `metadata:version_consistent` — {'fair/metadata.json': '0.3.0', 'fair/datapackage.json': '0.3.0', 'app/data/metadata.json': '0.3.0', 'codemeta.json': '0.3.0'}
- OK — `lockfiles:present` — uv.lock + renv.lock
- OK — `release:changelog` — CHANGELOG has 0.3.0
