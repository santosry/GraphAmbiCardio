# 05 — Data dictionary

The machine-readable dictionary is `data_dictionary/data_dictionary.csv` (102 variables across four processed datasets). This document summarises the datasets, their provenance and the graph tables.

---

## 1. Processed datasets

### 1.1 `data_processed/sinasc_campos_births.csv`
One row per live birth to a resident mother (municipality 330100), 2010–2022 and 2025.
- **Rows:** 98,598 (59 with a Q20–Q28 code).
- **Source:** DATASUS SINASC `DNRJ{year}.dbc` (state file), converted with `pyreaddbc`.
- **Key fields:** `codmunres`, `dtnasc`, `is_chd`, `chd_codes`, `codanomal`, `idanomal`, `semagestac`, `peso`, `idademae`, `sexo`, `parto`, `tipo_gravidez`.
- **Derived:** `n_icd_codes`, `conception_date_est`, `organogenesis_start_est`, `organogenesis_end_est`.
- **Case definition:** `is_chd = TRUE` when at least one parsed code in `CODANOMAL` is in Q20–Q28. `CODANOMAL` is parsed in blocks of four characters (e.g. `Q339Q211` → `Q339`, `Q211`).
- **Missing years:** 2023, 2024 (not available at DATASUS on the extraction date).

### 1.2 `data_processed/sih_campos_chd_admissions.csv`
One row per AIH of a resident with a primary diagnosis in Q20–Q28 (secondary-only records are retained in the raw extraction but not used in the main tables).
- **Rows:** 549.
- **Source:** 192 monthly `RDRJ{yy}{mm}.dbc` files (2010–2025).
- **Key fields:** `N_AIH`, `MUNIC_RES`, `MUNIC_MOV`, `DIAG_PRINC`, `DIAG_SECUN`, `DIAS_PERM`, `MORTE`, `VAL_TOT`, `CAR_INT`, `IDADE`, `COD_IDADE`, `age_years`, `age_group`.
- **Warning:** AIH ≠ person; no stable patient identifier exists, so readmissions and unique individuals cannot be derived.

### 1.3 `data_processed/climate_daily_campos.csv`
Daily ERA5-Land series, 2010-01-01 to 2025-12-31 (5,844 rows, no missing Tmax).
- **Source:** Open-Meteo Historical Weather API (ERA5/ERA5-Land), grid cell −21.757 / −41.354.
- **Fields:** Tmean, Tmax, Tmin, relative humidity, precipitation, wind; derived heat-wave id (`heatwave_id`), heat days ≥35 °C, cold days ≤15 °C, diurnal range.
- **Heat wave definition:** ≥3 consecutive days with Tmax above the 2010–2025 90th percentile (34.2 °C).

### 1.3b `data_processed/sinasc_tabnet_aggregates.csv`
Agregados do TabNet para 2022–2025 (nascidos vivos e casos do grupo “malformações congênitas do aparelho circulatório”).
- **Fonte:** DATASUS TabNet (`nvrj22.dbf` … `nvrj25.dbf`).
- **Uso:** preencher 2023–2024, cujos microdados não estavam disponíveis; 2025 serve como validação (9 casos e 5.924 nascidos, idêntico aos microdados).
- **Aviso:** definição de caso distinta do parser de qualquer código Q20–Q28; não misturar as séries.

### 1.4 `data_processed/sinasc_campos_with_exposure.csv`
The birth-level file plus gestational-window area-level exposure:
`win_temperature_2m_max_mean`, `win_temperature_2m_min_mean`, `win_relative_humidity_2m_mean_mean`, `win_heat_days_35_pct`, `win_covariate_completeness`.
- Exposure assigned to days 21–56 after estimated conception.
- 90,008 of 98,598 births (91.3%) have a complete window; window coverage is 100% where dates exist.

---

## 2. Biological datasets

| File | Rows | Meaning |
|---|---:|---|
| `hpo_gene_phenotype_edges.csv` | 2,803 | HPO gene→HPO annotations for the 14 sentinel terms (814 genes) |
| `hpo_phenotype_metadata.json` | 14 | HPO term metadata verified via the HPO API |
| `clinvar_variants.csv` | 945 | Pathogenic/likely pathogenic ClinVar variants (47-gene panel; CNVs excluded) |
| `clinvar_gene_counts.csv` | 47 | Per-gene ClinVar counts |
| `reactome_gene_pathway_edges.csv` | 1,956 | Per-gene Reactome over-representation (FDR < 0.05) |
| `reactome_gene_summary.csv` | 170 | Per-gene pathway counts |
| `ncbi_gene_metadata.csv` | 170 | NCBI Gene IDs and descriptions |
| `enrichr_GO_Biological_Process_2023.csv` | 1,631 | GO BP over-representation for the gene universe |
| `inferred_pathway_process_map.csv` | 4 | Explicit keyword map from Reactome pathways to developmental processes |
| `hypothesis_candidates.csv` | 5 | Gene-overlap hypotheses (exposure → phenotype), with supporting genes and missing link |
| `candidate_paths_missing_link.csv` | 7 | Documented chains reaching a process without a curated process → phenotype edge |

---

## 3. Evidence and graph tables

### `outputs/graph/nodes.csv`
`node_id, label, type, subtype, identifiers, description, source`.

### `outputs/graph/relations.csv`
`edge_id, edge_key, source_id, source_type, target_id, target_type, relation, layer, n_evidence, n_references, evidence_types, species, study_designs, confidence, grade, evidence_tier, evidence_tier_label, confidence_detail, references, source_database, retrieved_at`.

`evidence_tier` ∈ {`estabelecida`, `plausivel_experimental`, `nao_demonstrada`, `contextual`, `inferida`}.

### `outputs/graph/evidence.csv`
One row per evidence item (see `docs/04_ONTOLOGY.md` §4 for the full schema). Key fields: `evidence_id, edge_key, layer, evidence_type, study_design, species, population_or_model, exposure_window, effect_direction, quote, reference, reference_type, source_database, retrieved_at, notes`.

### `outputs/graph/graph.graphml` / `graph.json`
Interoperable exports of the aggregated graph; edge attributes include `relation`, `layer`, `confidence`, `grade`, `n_evidence`, `references`.

### `outputs/graph/hypotheses.csv`
Hipóteses (`HYPOTHESIS_LINK` e `HYPOTHESIS_CANDIDATE`) no mesmo esquema de evidência, com `layer = hypothesis` e `evidence_type = hypothesis`. Nunca usadas em caminhos ou centralidade.

### `app/data/`
Bundle autocontido do aplicativo Shiny (30 arquivos, ~4 MB), gerado por `scripts/app/01_prepare_data.py`.

### `reports/feasibility_pair_matrix.csv`
196 rows: exposure × phenotype, PubMed count, volume class, triage counts, mechanistic terms, provisional class and the exact query.

---

## 4. Coding conventions and missing data

- Missing values are empty strings/NA; **no imputation**.
- `COD_IDADE`: 4 = years, 3 = months, 2 = days; other codes are treated as unknown age.
- `IDANOMAL`: kept verbatim; **not** used as the case definition.
- `GESTACAO` categories: 1 <22 wk, 2 22–27, 3 28–31, 4 32–36, 5 37–41, 6 ≥42; midpoints used only when `SEMAGESTAC` is missing.
- Costs are nominal BRL (no deflation).
- Dates are ISO 8601 in processed files; DATASUS `DDMMYYYY` in raw fields.
