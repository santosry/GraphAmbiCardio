# GraphAmbiCardio

**Knowledge graph of environmental exposures, molecular mechanisms, cardiogenesis and congenital heart defects — Campos dos Goytacazes, RJ, 2010–2025.**

[![status](https://img.shields.io/badge/status-v0.1.0%20(phases%20A--G%20complete)-blue)]()
[![Python](https://img.shields.io/badge/python-3.12-blue)]()

GraphAmbiCardio is a reproducible computational study that integrates:

1. **structured literature searches** (PubMed/MEDLINE, Europe PMC) for five pre-registered evidence domains and for 196 exposure × phenotype pairs;
2. **curated biological databases** (HPO, ClinVar, NCBI Gene, Reactome, Enrichr);
3. **local epidemiological data** (SINASC and SIH/SUS, 2010–2025, residents of Campos dos Goytacazes);
4. **area-level climate exposure** (ERA5-Land via Open-Meteo);
5. a **provenance-first knowledge graph** in which every relation carries its evidence type, species, study design, context, reference, confidence and limitations.

The project intentionally separates what is **demonstrated**, what is **plausible**, and what remains **unknown**. It does not treat association as causation, admissions as incidence, or area-level exposure as personal exposure.

---

## 1. What is in this repository

| Path | Content |
|---|---|
| `src/graphambicardio/` | Python package (collection, cleaning, integration, graph, analysis, validation) |
| `scripts/` | Executable pipeline steps (collection → integration → analysis → validation) |
| `docs/` | Protocol, feasibility report, search strategy, database catalogue, ontology, data dictionary, evidence grading, methods, validation, limitations, phase log, manuscript draft |
| `reports/` | Feasibility matrices, PRISMA flow, validation results, audit sample, analysis summary |
| `literature/` | Raw search records (JSON), screening tables, curated anchor studies |
| `data_processed/` | Harmonised local and biological datasets |
| `outputs/graph/` | `nodes.csv`, `relations.csv`, `evidence.csv`, `graph.graphml`, `graph.json` |
| `outputs/tables/`, `outputs/figures/` | Analysis tables and figures |
| `tests/` | Unit and integrity tests (pytest) |

---

## 2. Headline results (v0.1.0)

### Evidence base

- **5 pre-registered literature domains** searched on **2026-10-31**:
  PubMed counts — exposure→CHD **1,512**; exposure→mechanism **8,520**; mechanism→cardiogenesis **6,736**; cardiogenesis→phenotype **7,681**; gene→phenotype **992**.
  Europe PMC counts — **1,599 / 171 / 39 / 593 / 2,387**.
- **196 exposure × phenotype pairs** queried; **73 pairs (37%) had no direct literature** under the pre-specified context filter; only **2 pairs** reached the “high volume” stratum.
- **1,450 retrieved records → 355 duplicates removed → 1,095 unique records screened** (1,003 with abstract). **29 anchor studies** were manually read and **46 curated edges** were encoded with verbatim quotes that are machine-verified against PubMed.

### Knowledge graph

- **2,234 nodes** and **4,100 relations**, backed by **4,596 evidence rows**.
- Layers: **observed** 46 relations, **structured** 4,040, **inferred** 4, **hypothesis** 7, **ecological** 3.
- **23 exposure→phenotype paths** in the conceptual core (13 direct, 10 through mechanism/process chains).
- **20 explicit gaps** (exposures, mechanisms or processes with no retained edge).
- Graph exports: `outputs/graph/graph.graphml`, `graph.json`, `nodes.csv`, `relations.csv`, `evidence.csv`.

### Local data (Campos dos Goytacazes)

- SINASC: **98,598 live births** (2010–2022 consolidated; 2023–2024 not available; 2025 preliminary) and **59 reported CHD cases** — **6.0 per 10,000 live births**, i.e. roughly one order of magnitude below expected birth prevalence, indicating severe under-ascertainment rather than low risk.
- SIH/SUS: **549 hospital admissions** with a primary diagnosis in Q20–Q28 (2010–2025), **33 in-hospital deaths**, **55% of admissions outside the municipality of residence**, 18 hospitals.
- Climate: **5,844 days** of ERA5-Land data; heat-wave threshold (Tmax P90) **34.2 °C**; **73 heat waves / 363 heat-wave days**.
- Exploratory ecological-exposure model (56–59 events): birth-level logistic regression of CHD on gestational-window mean Tmax, adjusted for year, maternal age and sex — **OR 1.30 per SD (95% CI 1.00–1.69)**; after adding quarter-of-conception fixed effects, **OR 1.65 per SD (1.13–2.42)**, stable under leave-one-year-out (1.47–1.66). The monthly count model was null (RR 1.22, 0.94–1.60). These results are **exploratory and fragile** and are not a causal claim.

> The most important local finding is methodological: **SINASC alone cannot support CHD prevalence or aetiology analyses in this municipality**. The local integration is therefore presented as ecological context, not as aetiological evidence.

---

## 3. Reproducing the study

### Requirements

- Python **3.12** (the DATASUS DBC decoder `pyreaddbc` has wheels for 3.12; the system Python 3.14 could not build it).
- Internet access to NCBI E-utilities, Europe PMC, JAX HPO, Reactome, Enrichr, Open-Meteo and the DATASUS FTP.

```bash
# create the environment (uv recommended; this is how the study was run)
uv venv .venv --python 3.12
uv pip install --python .venv -e ".[dev,datasus]"

# full pipeline
.venv/Scripts/python.exe scripts/collection/01_literature.py
.venv/Scripts/python.exe scripts/collection/02_databases.py
.venv/Scripts/python.exe scripts/collection/03_clinvar_enrichr.py
.venv/Scripts/python.exe scripts/epi/01_sinasc.py
.venv/Scripts/python.exe scripts/epi/02_sih.py
.venv/Scripts/python.exe scripts/env/01_climate.py
.venv/Scripts/python.exe scripts/epi/03_exposure_models.py
.venv/Scripts/python.exe scripts/integration/01_build_graph.py
.venv/Scripts/python.exe scripts/analysis/01_network.py
.venv/Scripts/python.exe scripts/analysis/02_figures.py
.venv/Scripts/python.exe scripts/validation/01_validate.py
.venv/Scripts/python.exe -m pytest -q
```

Raw downloads are cached under `data_raw/` (git-ignored); every HTTP response used in the graph is cached and the retrieval date is stored in the output tables.

### Optional credentials

- `NCBI_API_KEY` and `NCBI_EMAIL` environment variables raise the E-utilities rate limit.
- DisGeNET, OMIM, CDS/ERA5 and CTD require credentials or interactive access and were **not** used (see `docs/03_DATABASE_CATALOG.md`).

---

## 4. Key methodological safeguards

- **No fabricated references or data.** Every curated quote is a verbatim abstract fragment and the build fails if it is not found in PubMed.
- **Provenance per evidence row**, not per aggregated edge; the same relation may have several independent evidence rows.
- **Layered evidence**: observed / structured / inferred / hypothesis / ecological. Hypothesis edges are excluded from all path analyses.
- **Confidence is not centrality.** Network centrality is reported as a structural property and explicitly not as biological or causal importance.
- **Ecological design is labelled as such.** Area-level ERA5-Land exposure is assigned to individual gestational windows, but it is not personal exposure.
- **Under-ascertainment is quantified**, not hidden; missing years are not imputed.

---

## 5. Data and licensing

- Literature metadata: PubMed/Europe PMC (public; respect NLM and Europe PMC terms).
- HPO, ClinVar, NCBI Gene, Reactome, Enrichr: public resources; original licences apply to redistributed annotations. This repository redistributes identifiers and short quoted abstract fragments for verification, not full texts.
- SINASC and SIH/SUS: public secondary data from DATASUS, no personal identifiers in the extracted tables.
- Climate: ERA5-Land reanalysis via Open-Meteo (CC-BY-4.0 for the API outputs; Copernicus licence for ERA5).
- Code: MIT (see `LICENSE`).

---

## 6. How to cite

See `CITATION.cff`. Until a manuscript is published, cite the repository and the study version.

---

## 7. Status and limitations

v0.1.0 completes **Phases A–G** and the computational part of **Phase H**, with the validation report, limitations report and manuscript draft in `docs/`. Phase I (scientific interpretation) and Phase J (publication) are partially complete. The main limitations are:

- rapid scoping rather than a full systematic review (no dual independent screening of all 1,095 records);
- 2023–2024 SINASC microdata unavailable and 2025 preliminary;
- no local PM2.5 monitoring; no personal exposure; low event counts;
- many molecular edges depend on animal/cell models;
- CTD, DisGeNET and OMIM not programmatically accessible in this environment;
- SciELO/BVS/CAPES interfaces blocked automated access (HTTP 403), so Portuguese-language databases were not systematically searched.

See `docs/09_LIMITATIONS_AND_GAPS.md` for the full account.
