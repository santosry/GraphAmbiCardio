# 10 — Phase execution log

All work was executed on **2026-10-31** (America/Sao_Paulo). Each phase records what was done, what was obtained, criteria, results, open problems and whether it was apt to advance. Commands are reproducible; logs are in `logs/`.

---

## Phase A — Scientific and bibliographic viability

**Done.** Five pre-registered domains searched on PubMed (A1–A5) and Europe PMC; 196 exposure × phenotype pairs queried; automated triage of retrieved abstracts; manual reading of anchor studies; feasibility matrix built; explicit decision on what enters the first graph.

**Obtained.**
- PubMed hits: A1 1,512; A2 8,520; A3 6,736; A4 7,681; A5 992.
- Europe PMC hits: 1,599 / 171 / 39 / 593 / 2,387.
- 196 pairs: 73 with no direct literature, 66 sparse, 36 limited, 19 moderate, 2 high.
- 29 anchor studies; 46 curated edges.

**Criteria.** Directness of evidence, species, design, exposure window, phenotype specificity, structured-data availability, integration feasibility.

**Problems.** Automated triage over-counts relevance; Portuguese databases inaccessible; bibliometric volume ≠ quality.

**Decision.** Proceed with a restricted observed core and explicit gap layer; do not use local data for aetiological inference. **Apt to advance: yes.**

---

## Phase B — Selection and audit of databases

**Done.** Probed every database listed in the protocol. Recorded identifier, coverage, access route, licence and limitations in `docs/03_DATABASE_CATALOG.md`.

**Obtained.** HPO (2,803 annotations / 814 genes), ClinVar (945 pathogenic/likely pathogenic variants after CNV exclusion), NCBI Gene (170), Reactome (1,956 gene–pathway results; 649 after developmental filter), Enrichr GO BP (1,631 terms).

**Blocked.** CTD (captcha), DisGeNET (API key), OMIM (licence), SciELO/BVS (HTTP 403), INMET (unreachable), local PM2.5 (no series), GEO (no dataset met criteria).

**Decision.** Restrict the structured layer to accessible, licensed resources; document every exclusion. **Apt to advance: yes.**

---

## Phase C — Scoping review and evidence extraction

**Done.** All searches stored with exact query, translation, date, counts and records. Deduplication by PMID → DOI → normalised title. Automated triage; manual reading of 29 anchors; verbatim quotes stored.

**Obtained.** 1,450 retrieved records → 355 duplicates → 1,095 unique → 1,003 with abstract → 29 anchors → 46 edges. PRISMA-ScR flow in `reports/prisma_flow.csv`.

**Problems.** No dual screening; no full text; no formal risk-of-bias tool. The audit sheet is ready but not completed.

**Decision.** Label the review as rapid scoping with targeted manual curation; do not claim systematic-review status. **Apt to advance: yes, with limitation.**

---

## Phase D — Ontology

**Done.** Defined 14 node types, 12 relation types, 5 evidence layers, the evidence-row schema, entity-resolution rules and inference rules (`docs/04_ONTOLOGY.md`).

**Decision.** Keep the ontology small and enforce constraints in code. Chemical/ClimateVariable/Study nodes are declared but not instantiated; this is documented. **Apt to advance: yes.**

---

## Phase E — Local epidemiological and environmental data

**Done.** SINASC 2010–2022 + 2025; SIH 2010–2025 (192 monthly files); ERA5-Land 2010–2025; gestational-window linkage; descriptive indicators; exploratory models; leave-one-year-out sensitivity.

**Obtained.**
- 98,598 births; 59 CHD cases (5.98/10,000); 2023–2024 missing; 2025 preliminary.
- 549 CHD admissions; 33 deaths; 55% outside municipality; 18 hospitals.
- 5,844 climate days; heat-wave threshold 34.2 °C; 73 heat waves.
- 90,008 births with a complete organogenesis window.
- Logistic OR 1.30/SD (1.00–1.69); season-adjusted 1.65 (1.13–2.42); monthly RR 1.22 (0.94–1.60); LOO 1.47–1.66.

**Problems.** Under-ascertainment; missing years; ecological exposure; 56–59 events.

**Decision.** Report local results as exploratory/ecological; do not create a local heat→CHD edge. **Apt to advance: yes, as context only.**

---

## Phase F — Molecular integration

**Done.** HPO, ClinVar, NCBI Gene, Reactome and Enrichr retrieval; NCBI IDs; pathway over-representation per gene; gene universe (panel + HPO top-150).

**Obtained.** 46 curated molecular/clinical edges, 4,040 structured relations (2,314 gene–phenotype after collapsing, 649 gene–pathway, 945 variant–gene, 150 variant–phenotype).

**Problems.** 814 HPO genes lack NCBI metadata (only top-150 enriched); single-gene Reactome over-representation is statistically weak; no expression data.

**Decision.** Keep structured edges in their own layer; never let them inflate observed evidence. **Apt to advance: yes.**

---

## Phase G — Graph construction

**Done.** Evidence-first build with quote verification; aggregation with pre-registered confidence; GraphML/JSON/CSV export.

**Obtained.** 2,234 nodes; 4,100 relations; 4,596 evidence rows. Layers: observed 46, structured 4,040, inferred 4, hypothesis 7, ecological 3.

**Problems.** Graph is gene-heavy; pathways are coarse; inferred map is small.

**Decision.** Analyses exclude variants from centrality and exclude hypothesis/ecological layers from paths. **Apt to advance: yes.**

---

## Phase H — Analyses and validation

**Done.** Centrality, communities, exposure→phenotype paths, gene convergence/overlap, gap analysis, threshold sensitivity, validation checks and tests.

**Obtained.** 23 paths (13 direct + 10 mechanistic); 20 gaps; 8 communities; validation passed (0 integrity issues); pytest passing.

**Problems.** Manual two-reviewer audit pending; centrality dominated by HPO annotation density; threshold sensitivity substantial.

**Decision.** Report high-confidence core separately; keep hypothesis layer out of paths. **Apt to advance: conditionally (manual audit pending).**

---

## Phase I — Scientific interpretation

**Done.** Interpreted results without extrapolation: direct human evidence is concentrated in a few exposures/phenotypes; mechanistic chains are experimental; local data cannot test aetiology; gaps are the main output.

**Problems.** The local heat signal is fragile; publication bias; exposure misclassification.

**Decision.** Present the heat finding as hypothesis-generating only; do not claim causality or individual risk. **Apt to advance: yes, with conservative language.**

---

## Phase J — Publication and reproducibility

**Done.** Documentation (protocol, feasibility, search strategy, database catalogue, ontology, data dictionary, grading, methods, validation, limitations, phase log, manuscript draft), README, tests, exports, audit sheet.

**Problems.** No DOI/archival release yet; SciELO/BVS gap; two-reviewer audit not completed; exact database release hashes not pinned.

**Decision.** Release v0.1.0 as a reproducible study scaffold with a complete computational pipeline and a manuscript draft. **Apt to advance: yes, to internal review.**

---

## Deviations and blockers (summary)

| Item | Status | Consequence |
|---|---|---|
| R not installed | Python 3.12 used | documented; R-compatible CSVs exported |
| CTD captcha | blocked | no chemical–gene curated edges from CTD |
| DisGeNET key | blocked | gene–disease layer from HPO/ClinVar only |
| OMIM licence | blocked | no OMIM edge-level provenance |
| SciELO/BVS 403 | blocked | Portuguese literature gap |
| CAPES no API | not automated | institutional search needed |
| INMET unreachable | blocked | ERA5-Land used |
| PM2.5 no series | not fabricated | air-pollution local analysis impossible |
| SINASC 2023–2024 | absent | time series gap; no imputation |
| Full dual review | not performed | rapid scoping label |

Every deviation is reflected in the manuscript’s limitations section.
