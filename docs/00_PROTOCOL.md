# 00 — Research protocol (pre-registered plan)

**Study:** GraphAmbiCardio — knowledge graph of environmental exposures, molecular mechanisms, cardiogenesis and congenital heart defects (CHD) in Campos dos Goytacazes, RJ, 2010–2025.
**Version:** 0.1.0 (protocol frozen before graph construction; deviations logged in `10_PHASE_LOG.md`).
**Date of protocol:** 2026-10-31.

---

## 1. Background and rationale

CHD are the most common major congenital anomalies (birth prevalence commonly reported around 6–9 per 1,000 live births, with substantial regional variation). Their aetiology is multifactorial: Mendelian and chromosomal causes explain a minority of cases; environmental, behavioural and developmental factors contribute, but the evidence is scattered across epidemiology, toxicology, developmental biology and genetics. Mechanistic claims are often made by chaining associations that were never studied together.

This protocol therefore builds a **traceable graph of documented relations**, not a predictive model, and asks which connections are demonstrated, which are experimentally supported, which are only indirect, and which remain hypotheses.

---

## 2. Question

In the period 2010–2025, for residents of Campos dos Goytacazes (RJ, Brazil):

> Which environmental exposures have documented associations with congenital heart defects, which molecular mechanisms and developmental processes connect them, and which of these connections are supported by converging evidence across human, animal and cell studies?

Secondary question: what does the local epidemiological and environmental data add, and what are its limits?

---

## 3. Objectives

1. Identify environmental exposures investigated in association with CHD.
2. Identify molecular mechanisms related to the selected exposures.
3. Map genes, proteins, variants and pathways involved in cardiogenesis.
4. Identify relations between molecular mechanisms and specific CHD phenotypes.
5. Build a provenance-rich relation network with evidence-quality classification.
6. Integrate local epidemiological and environmental data (2010–2025) as ecological context.
7. Identify biologically plausible relations, converging evidence and knowledge gaps.
8. Evaluate graph consistency and robustness.

---

## 4. Scope and definitions

### 4.1 Population

Live births and hospital admissions of residents of Campos dos Goytacazes (IBGE 330100), 2010-01-01 to 2025-12-31. Literature: human studies of any population, plus experimental animal/cell studies relevant to human cardiogenesis.

### 4.2 Phenotypes

CID-10 Q20–Q28. Fourteen sentinel phenotypes are represented with HPO cross-references: VSD (Q21.0), ASD (Q21.1), AVSD (Q21.2), TOF (Q21.3), DORV (Q20.1), TGA (Q20.3), HLHS (Q23.4), coarctation (Q25.1), PDA (Q25.0), pulmonary stenosis (Q25.6), aortic stenosis (Q23.0), TAPVC (Q26.2), truncus arteriosus (Q20.0), Ebstein anomaly (Q22.5). An aggregate node `CHD:ALL` is used when a study reports overall CHD.

### 4.3 Exposures

Seventeen exposures pre-specified for environmental/occupational/therapeutic relevance and local plausibility: PM2.5, PM10, NO2/traffic, O3, SO2, CO, heat, cold, relative humidity (contextual), pesticides, organic solvents, heavy metals, tobacco smoke, alcohol, valproic acid, retinoic acid derivatives, dioxins/PCBs. The hierarchy is explicit: PM2.5 as primary axis, temperature as secondary, humidity as contextual only.

> Pre-specification does **not** imply that evidence exists. Exposures without retained evidence remain in the graph as explicit gaps.

### 4.4 Biological layer

- Mechanisms: oxidative stress, inflammation, epigenetic alteration, mitochondrial dysfunction, altered signalling, altered gene expression, apoptosis, proliferation, heat-shock response, AHR, retinoic acid, Wnt/β-catenin, HDAC, hypoxia, neural crest, endothelial/vascular perturbation.
- Processes: heart tube, looping, chamber development, septation, AV cushion/valve, outflow tract, great vessels, cardiac neural crest migration, cardiomyocyte differentiation, coronary/vascular development, conduction system.
- Genes: pre-specified panel (NKX2-5, GATA4, TBX5, NOTCH1, TBX1, JAG1, etc.) plus genes emerging from HPO/ClinVar.

### 4.5 Inclusion criteria

- Human epidemiological studies of prenatal/periconceptional exposure and CHD.
- Experimental studies (human cells, animal models) of the mechanism or developmental process.
- Human genetics studies with variant-level evidence.
- Structured database annotations with stable identifiers.
- Reviews only as **indirect** evidence for synthesised developmental relations.
- Foundational papers before 2010 are eligible for genetics, embryology and mechanisms; the 2010–2025 window applies **only** to local epidemiological data, not to biological literature.

### 4.6 Exclusion criteria

- Adult cardiac disease without congenital/developmental context.
- Case reports of anaesthetic or surgical management (e.g. malignant hyperthermia during TOF repair).
- Studies without exposure or outcome definition.
- Non-peer-reviewed sources, conference abstracts, preprints, predatory outlets.
- Relations supported only by co-occurrence or text-mining without a verifiable source.

---

## 5. Evidence sources

### Literature
PubMed/MEDLINE (E-utilities), Europe PMC (REST), SciELO (metadata via Crossref, DOI prefix 10.1590) and CAPES (Catálogo de Teses e Dissertações). The SciELO search interface blocked automated access, so Crossref was used; this is documented in `02_SEARCH_STRATEGY.md`.

### Structured biology
HPO (ontology + gene-to-phenotype annotations), ClinVar, NCBI Gene, Reactome Analysis Service, Enrichr (GO Biological Process). OMIM, DisGeNET and CTD were not programmatically accessible (licence/credential/captcha); their absence is documented.

### Local epidemiology
SINASC (live births) and SIH/SUS (hospital admissions), DATASUS FTP, extracted via DBC → DBF → records.

### Environment
ERA5-Land daily series via Open-Meteo for the municipality grid cell, and annual/monthly municipal PM2.5 from VIGIAR (Ministry of Health) via the `vigiar` R package, 2010–2025. Both are area-level series, not personal exposure.

---

## 6. Search strategy (summary)

Five pre-registered evidence domains:

| ID | Domain |
|---|---|
| A1 | environmental exposure ↔ CHD |
| A2 | environmental exposure ↔ molecular mechanism (cardiac/developmental context) |
| A3 | molecular mechanism ↔ cardiogenesis |
| A4 | cardiogenesis ↔ CHD phenotype |
| A5 | gene/protein ↔ CHD phenotype |

Plus a 14 × 14 **exposure × phenotype** matrix (196 queries) with a prenatal/developmental context block, used only as a bibliometric feasibility screen.

Full strings, translations, dates and counts: `docs/02_SEARCH_STRATEGY.md` and `literature/searches/*.json`.

---

## 7. Screening and data extraction

- Deduplication by PMID, DOI and normalised title.
- Automated triage of titles/abstracts for species, design, exposure window, mechanism and phenotype vocabulary.
- **Manual curation** of anchor studies: the reviewer read the abstract and extracted (i) the exact claim, (ii) a verbatim quote, (iii) species/design/population/window/direction.
- A build-time verifier checks that every quote exists in the PubMed abstract; failure aborts the build.

This is a **structured, non-systematic search with targeted manual extraction**, not a full dual-reviewer systematic review. The PRISMA-ScR flow reflects exactly what was done.

---

## 8. Ontology and provenance

Node types: Exposure, Chemical, ClimateVariable, Mechanism, Gene, Pathway, Process, Phenotype, Variant, Indicator, Population, Period, Study, DataSource.
Relation types: `EXPOSURE_ASSOCIATED_WITH_PHENOTYPE`, `EXPOSURE_MODULATES_MECHANISM`, `MECHANISM_INTERFERES_WITH_PROCESS`, `GENE_ASSOCIATED_WITH_PHENOTYPE`, `GENE_PARTICIPATES_IN_PATHWAY`, `PATHWAY_REGULATES_PROCESS`, `VARIANT_IN_GENE`, `ALTERATION_ASSOCIATED_WITH_PHENOTYPE`, `INDICATOR_DESCRIBES_PHENOTYPE`, `ECOLOGICAL_CONTEXT_FOR`, `HYPOTHESIS_LINK`.

Evidence layers: **observed**, **structured**, **inferred**, **hypothesis**, **ecological**. Layers are never merged in analysis.

Full specification: `docs/04_ONTOLOGY.md`.

---

## 9. Evidence grading

Each evidence row records evidence type (direct human, human experimental, animal, cell, structured database, indirect, hypothesis), study design, species, population/model, exposure window, effect direction, context and reference.

Edge confidence is computed with a pre-registered formula:

```
base      = min(0.9, max(0.7·type_weight + 0.3·design_weight))
conf      = base + replication_bonus + species_concordance_bonus
            − single_study_penalty − non_significance_penalty − contradiction_penalty
conf      = clip(conf, 0, 0.95)
```

Grades: A ≥ 0.85, B ≥ 0.70, C ≥ 0.55, D ≥ 0.40, E < 0.40.
Full weights and rationale: `docs/06_EVIDENCE_GRADING.md`.

**Centrality is never interpreted as causal importance.**

---

## 10. Local epidemiological methods

- Case = any CID-10 code Q20–Q28 in `CODANOMAL`, parsed as blocks of four characters (multiple codes per record are preserved).
- Denominator = live births to resident mothers (SINASC).
- Indicators: annual counts, proportion per 1,000, rate per 10,000, phenotype distribution, maternal/neonatal characteristics, completeness indicators.
- SIH: AIH counts, never individuals; residence (MUNIC_RES) and admission municipality (MUNIC_MOV) kept separate; primary and secondary diagnoses kept separate.
- 2025 flagged preliminary; 2023–2024 SINASC absent and not imputed.
- Gestational window: conception estimated as birth date − gestational age; cardiac organogenesis window = days 21–56 after conception (weeks 3–8). Area-level daily climate averaged over this window.
- Models: birth-level logistic regression (CHD ~ exposure z-score + year + maternal age + sex) and a season-adjusted sensitivity model; monthly Poisson/negative-binomial counts by conception month with log(births) offset. Leave-one-year-out sensitivity.

Full methods and results: `docs/07_EPI_ENV_METHODS.md`.

---

## 11. Analysis plan

- Descriptive evidence matrices (feasibility, evidence density).
- Graph centrality (degree, betweenness) and Louvain communities.
- All simple exposure→phenotype paths (cut-off 5 nodes), with minimum edge confidence along each path.
- Gene convergence per phenotype and gene-set overlap between phenotypes.
- Explicit gap analysis (entities without retained edges).
- Sensitivity to confidence thresholds (0.40, 0.50, 0.55, 0.70, 0.85).
- Hypothesis and inferred layers analysed separately and never presented as observed.

---

## 12. Validation plan

1. Bibliographic: quote verification against PubMed (100% of curated edges; 25% re-checked at validation).
2. Biological: manual review of every curated edge for developmental/molecular coherence.
3. Data: municipality, period, missingness, range and completeness checks.
4. Computational: node/edge integrity, unique IDs, no self-loops, valid relation vocabulary, tests.
5. Robustness: confidence-threshold sensitivity and leave-one-year-out models.

---

## 13. Ethics and data protection

Secondary, aggregate, publicly available data; no names, addresses, CPF or dates of birth are exported. Small-area / small-count tables are reported at municipality level only. The study does not attempt re-identification.

---

## 14. Deviations from the original plan

| Planned | Executed | Reason |
|---|---|---|
| R as primary language | Python (with R unavailable in the runtime) | R was not installed; Python 3.12 + pysus was the only reproducible route to DATASUS DBC files |
| CTD, DisGeNET, OMIM | Not used | Captcha / API key / licence restrictions |
| SciELO search interface | Crossref metadata used instead | HTTP 403 to automated requests |
| INMET station series | ERA5-Land via Open-Meteo | INMET portal not reachable programmatically |
| Local PM2.5 | Not used | No local monitoring series; no proxy fabricated |
| Full dual-reviewer systematic review | Rapid scoping + targeted manual curation | Feasibility and traceability prioritised; audit sample provided |

---

## 15. Expected products

Protocol; feasibility matrix; search strategies and PRISMA flow; database catalogue; ontology; data dictionary; evidence matrix; graph (GraphML/JSON/CSV); computational pipeline; local epidemiological and environmental analyses; figures; validation report; limitations/gaps report; manuscript draft; reproducible repository.
