# Schema validation

Generated: 2026-11-01T21:08:05Z

**Result: PASSED**

- OK | `columns:outputs/graph/nodes.csv` | 2238 rows
- OK | `columns:outputs/graph/relations.csv` | 4146 rows
- OK | `columns:outputs/graph/evidence.csv` | 4659 rows
- OK | `columns:outputs/tables/exploratory_models.csv` | 16 rows
- OK | `columns:outputs/tables/hypothesis_candidates.csv` | 1 rows
- OK | `columns:data_processed/pm25_campos_anual.csv` | 16 rows
- OK | `columns:data_processed/pm25_campos_mensal.csv` | 192 rows
- OK | `columns:app/data/models.csv` | 16 rows
- OK | `columns:outputs/tables/sensitivity_leave_one_year_out.csv` | 14 rows
- OK | `columns:outputs/tables/gestational_window_sensitivity.csv` | 3 rows
- OK | `columns:outputs/tables/julia_gestational_window_simulation.csv` | 505 rows
- OK | `columns:app/data/julia_ga_simulation.csv` | 505 rows
- OK | `columns:outputs/tables/sinasc_annual_complete.csv` | 16 rows
- OK | `columns:outputs/tables/sinasc_other_circulatory_by_code.csv` | 2 rows
- OK | `columns:outputs/tables/sih_other_circulatory_annual.csv` | 15 rows
- OK | `columns:outputs/tables/hypothesis_family.csv` | 66 rows
- OK | `columns:outputs/tables/mechanism_gene_sets.csv` | 103 rows
- OK | `columns:app/data/ga_sensitivity.csv` | 3 rows
- OK | `columns:app/data/sinasc_other_by_code.csv` | 2 rows
- OK | `columns:app/data/sih_other_annual.csv` | 15 rows
- OK | `columns:outputs/tables/exposure_correlation.csv` | 5 rows
- OK | `columns:outputs/tables/exposure_vif.csv` | 5 rows
- OK | `columns:data_processed/inmet_campos_daily.csv` | 5754 rows
- OK | `columns:outputs/tables/inmet_era5_comparison.csv` | 4 rows
- OK | `columns:app/data/inmet_daily.csv` | 5754 rows
- OK | `columns:app/data/inmet_comparison.csv` | 4 rows
- OK | `fdr:outputs/tables/exploratory_models.csv` | ok
- OK | `fdr:outputs/tables/hypothesis_candidates.csv` | ok
- OK | `fdr:outputs/tables/hypothesis_family.csv` | ok
- OK | `inmet:rows` | 5754 days
- OK | `inmet:unique_dates` | ok
- OK | `inmet:station` | {'A607'}
- OK | `inmet:tmax_range` | -10 to 55 C
- OK | `inmet:rh_range` | 0-100 %
- OK | `pm25:monthly_rows` | 192 rows
- OK | `pm25:monthly_unique` | ok
- OK | `pm25:monthly_range` | 0-500 µg/m3
- OK | `pm25:monthly_complete` | 0 missing
- OK | `pm25:annual_years` | 16 rows
- OK | `case_definition:no_q27_q28_in_chd` | ok
- OK | `case_definition:2023_2024_core_missing` | core CHD not imputed from TabNet
- OK | `case_definition:tabnet_separate` | TabNet kept in its own columns
- OK | `climate:model_fixed` | era5_land
- OK | `climate:returned_cell` | -21.799995,-41.300003
- OK | `julia:fixed_scenarios` | 5 fixed rows
- OK | `julia:monte_carlo` | 500 MC rows
- OK | `julia:report_language` | Julia
- OK | `app:no_individual_data` | ok
- OK | `metadata:version_consistent` | {'fair/metadata.json': '0.4.0', 'fair/datapackage.json': '0.4.0', 'app/data/metadata.json': '0.4.0', 'codemeta.json': '0.4.0'}
- OK | `lockfiles:present` | uv.lock + renv.lock
- OK | `release:changelog` | CHANGELOG has 0.4.0
