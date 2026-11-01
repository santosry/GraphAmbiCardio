# 10: Phase execution log

All work was executed on **2026-10-31** (America/Sao_Paulo), with the CAPES triage and thesis integration added on **2026-11-01**. Each phase records what was done, what was obtained, criteria, results, open problems and whether it was apt to advance. Commands are reproducible; logs are in `logs/`.

> **Nota sobre contagens:** as fases A–G registram os valores da época (33 âncoras / 54 arestas). Após as Fases M, N e O, os valores correntes são **59 âncoras / 84 linhas de evidência curada / 76 relações únicas / 4.639 linhas de evidência totais**.

---

## Phase A: Scientific and bibliographic viability

**Done.** Five pre-registered domains searched on PubMed (A1–A5) and Europe PMC; 196 exposure × phenotype pairs queried; automated triage of retrieved abstracts; manual reading of anchor studies; feasibility matrix built; explicit decision on what enters the first graph.

**Obtained.**
- PubMed hits: A1 1,512; A2 8,520; A3 6,736; A4 7,681; A5 992.
- Europe PMC hits: 1,599 / 171 / 39 / 593 / 2,387.
- 196 pairs: 73 with no direct literature, 66 sparse, 36 limited, 19 moderate, 2 high.
- 33 anchor studies; 54 curated edges.

**Criteria.** Directness of evidence, species, design, exposure window, phenotype specificity, structured-data availability, integration feasibility.

**Problems.** Automated triage over-counts relevance; Portuguese databases inaccessible; bibliometric volume ≠ quality.

**Decision.** Proceed with a restricted observed core and explicit gap layer; do not use local data for aetiological inference. **Apt to advance: yes.**

---

## Phase B: Selection and audit of databases

**Done.** Probed every database listed in the protocol. Recorded identifier, coverage, access route, licence and limitations in `docs/03_DATABASE_CATALOG.md`.

**Obtained.** HPO (2,803 annotations / 814 genes), ClinVar (945 pathogenic/likely pathogenic variants after CNV exclusion), NCBI Gene (170), Reactome (1,956 gene–pathway results; 649 after developmental filter), Enrichr GO BP (1,631 terms).

**Blocked.** CTD (captcha), DisGeNET (API key), OMIM (licence), SciELO search interface (HTTP 403; Crossref used), INMET (later obtained via BrazilMet), GEO (no dataset met criteria).

**Decision.** Restrict the structured layer to accessible, licensed resources; document every exclusion. **Apt to advance: yes.**

---

## Phase C: Scoping review and evidence extraction

**Done.** All searches stored with exact query, translation, date, counts and records. Deduplication by PMID → DOI → normalised title. Automated triage; manual reading of 33 anchors; verbatim quotes stored.

**Obtained.** 1,978 raw records → 529 duplicates → 1,449 unique → 1,003 with abstract (PubMed/Europe PMC subset) → 33 anchors → 54 edges. PRISMA-ScR flow in `reports/prisma_flow.csv`.

**Problems.** No dual screening; no full text; no formal risk-of-bias tool.

**Decision.** Label the review as a structured, non-systematic search with targeted manual curation; do not claim systematic-review status. **Apt to advance: yes, with limitation.**

---

## Phase D: Ontology

**Done.** Defined 14 node types, 12 relation types, 5 evidence layers, the evidence-row schema, entity-resolution rules and inference rules (`docs/04_ONTOLOGY.md`).

**Decision.** Keep the ontology small and enforce constraints in code. Chemical/ClimateVariable/Study nodes are declared but not instantiated; this is documented. **Apt to advance: yes.**

---

## Phase E: Local epidemiological and environmental data

**Done.** SINASC 2010–2022 + 2025; SIH 2010–2025 (192 monthly files); ERA5-Land 2010–2025; gestational-window linkage; descriptive indicators; exploratory models; leave-one-year-out sensitivity.

**Obtained.**
- 98,598 births; 52 core CHD cases (Q20–Q26; 5.27/10,000) and 8 Q27–Q28; 2023 and 2024 aggregate-only via TabNet (5 broad Q20–Q28 cases each); 2025 preliminary.
- PM2.5 municipal 2010–2025 from VIGIAR via `vigiar` (annual 6.50–9.04 µg/m³; monthly 3.83–13.84 µg/m³).
- 474 primary core-CHD admissions (Q20–Q26), 75 primary Q27–Q28, 12 secondary-only; 30 deaths; 51.9% outside municipality; 16 hospitals.
- 5,844 climate days with model fixed to `era5_land`; heat-wave threshold 33.3 °C; 68 heat waves.
- Gestational window corrected: conception = birth date − (gestational age × 7 − 14 days); ±7-day sensitivity.
- SINASC: 52 core CHD (Q20–Q26) and 8 Q27–Q28 among 98,598 births.
- 90,258 births with a complete main organogenesis window; ±7-day sensitivity windows stored.
- Logistic OR 1.30/SD (1.00–1.69); season-adjusted 1.65 (1.13–2.42); monthly RR 1.22 (0.94–1.60); LOO 1.47–1.66.

**Problems.** Under-ascertainment; missing years; ecological exposure; 47 events; sensitivity to gestational dating.

**Decision.** Report local results as exploratory/ecological; do not create a local heat→CHD edge. **Apt to advance: yes, as context only.**

---

## Phase F: Molecular integration

**Done.** HPO, ClinVar, NCBI Gene, Reactome and Enrichr retrieval; NCBI IDs; pathway over-representation per gene; gene universe (panel + HPO top-150).

**Obtained.** 54 curated molecular/clinical edges, 4,040 structured relations (2,314 gene–phenotype, 649 gene–pathway, 945 variant–gene, 150 variant–phenotype).

**Problems.** 814 HPO genes lack NCBI metadata (only top-150 enriched); single-gene Reactome over-representation is statistically weak; no expression data.

**Decision.** Keep structured edges in their own layer; never let them inflate observed evidence. **Apt to advance: yes.**

---

## Phase G: Graph construction

**Done.** Evidence-first build with quote verification; aggregation with pre-registered confidence; GraphML/JSON/CSV export.

**Obtained.** 2,238 nodes; 4,117 relations; 4,613 evidence rows. Layers: observed 54, structured 4,040, inferred 4, hypothesis 14, ecological 5.

**Problems.** Graph is gene-heavy; pathways are coarse; inferred map is small.

**Decision.** Analyses exclude variants from centrality and exclude hypothesis/ecological layers from paths. **Apt to advance: yes.**

---

## Phase H: Analyses and validation

**Done.** Centrality, communities, exposure→phenotype paths, gene convergence/overlap, gap analysis, threshold sensitivity, validation checks and tests.

**Obtained.** 27 paths (17 direct + 10 mechanistic); 20 gaps; 5 gene-overlap hypotheses; 7 candidate paths; 8 communities; validation passed; 10 tests passing.

**Problems.** Centrality dominated by HPO annotation density; threshold sensitivity substantial.

**Decision.** Report high-confidence core separately; keep hypothesis layer out of paths. **Apt to advance: yes.**

---

## Phase I: Scientific interpretation

**Done.** Interpreted results without extrapolation: direct human evidence is concentrated in a few exposures/phenotypes; mechanistic chains are experimental; local data cannot test aetiology; gaps are the main output.

**Problems.** The local heat signal is fragile; publication bias; exposure misclassification.

**Decision.** Present the heat finding as hypothesis-generating only; do not claim causality or individual risk. **Apt to advance: yes, with conservative language.**

---

## Phase J: Publication and reproducibility

**Done.** Documentation (protocol, feasibility, search strategy, database catalogue, ontology, data dictionary, grading, methods, validation, limitations, phase log, manuscript draft, FAIR, AI declaration, app guide), README, tests, exports, **Shiny app (GraphAmbiCardio)**, FAIR metadata, R collectors for SciELO (Crossref), CAPES and VIGIAR PM2.5, Docker files, benchmark and compliance reports.

**Problems.** SciELO/CAPES coverage is partial; exact database release hashes are not pinned.

**Decision.** Release v0.2.0 as a reproducible study scaffold with a complete computational pipeline, an interactive platform (GraphAmbiCardio) and a manuscript draft. **Apt to advance: yes, to internal review.**

---

## Phase K: Privacy, FDR and reproducibility hardening (v0.3.0)

**Done.** Individual-level SINASC/SIH records removed from Git and from history; compliance now blocks their versioning. Benjamini–Hochberg FDR applied to all models and gene-overlap hypotheses. Firth, cluster-robust and socio-economic sensitivity models; exposure correlation/VIF diagnostics. CI (GitHub Actions), `uv.lock`, `renv.lock`, schema validation, extra tests, CodeMeta, changelog and release checklist. App accessibility improvements (lang, skip link, focus styles, graph alternative text).

**Problems.** No model survives FDR; CHD under-ascertainment remains the dominant limitation.

**Decision.** Release v0.3.0 as a privacy-hardened, reproducible and statistically more conservative version. **Apt to advance: yes, to internal review with explicit limitations.**

---

## Deviations and blockers (summary)

| Item | Status | Consequence |
|---|---|---|
| R not installed | Python 3.12 used | documented; R-compatible CSVs exported |
| CTD captcha | blocked | no chemical–gene curated edges from CTD |
| DisGeNET key | blocked | gene–disease layer from HPO/ClinVar only |
| OMIM licence | blocked | no OMIM edge-level provenance |
| SciELO search interface 403 | Crossref used | Portuguese coverage partial |
| Portal de Periódicos CAPES | no open API; institutional authentication | not used; public thesis catalogue used for triage (560 retrieved; 552 unique; 1 included) |
| INMET | BrazilMet 0.5.0, station A607 | used for ERA5-Land validation; not personal exposure |
| PM2.5 local | VIGIAR via `vigiar` | annual/monthly 2010–2025, area-level |
| SINASC 2023–2024 | absent | time series gap; no imputation |
| Full dual review | not performed | structured, non-systematic label |

Every deviation is reflected in the manuscript’s limitations section.

---

## Phase L: Methodological correction and v0.4.0

**Done.** Corrected the obstetric conception estimate (LMP-to-conception lag of 14 days; 40 weeks = 266 days before birth) and added ±7-day gestational-window sensitivity. Split the local case definition into core CHD Q20–Q26 and separate Q27–Q28. Fixed the Open-Meteo request to `models=era5_land` and recorded model, resolution, returned grid cell, elevation, units and retrieval timestamp. Rebuilt the gene-overlap hypothesis family before selection, applied BH-FDR across all 89 tests, added a size-matched permutation sensitivity and documented mechanism gene-set provenance. Corrected the sex recoding so unknown codes are missing rather than female.

**Obtained.** SINASC: 52 core CHD and 8 Q27–Q28 among 98,598 births. SIH: 474 primary core-CHD admissions and 75 Q27–Q28. Climate: P90 33.3 °C; 68 heat waves. Models: Tmax OR 1.155 (0.87–1.54; p=0.318); no result survives FDR. Hypotheses: 89 tests, 5 with overlap ≥2, none significant after BH-FDR; permutation also non-significant. INMET comparison against the fixed ERA5-Land series: Tmax r=0.937; RH r=0.787.

**Decision.** Release v0.4.0 as a methodologically corrected, more conservative version. **Apt to advance: yes, to review; not to causal claims.**

---

## Phase M: CAPES triage and thesis integration (2026-11-01)

**Done.** Revisited the CAPES records that had entered the PRISMA flow but had not been manually promoted. The collector was extended to paginate all pages, retrieving **560 records** (552 unique IDs) instead of the first 20 per query. All 552 unique records were title-screened; one systematic-review thesis on maternal pesticide exposure and congenital malformations was read at abstract level, archived locally (`literature/curated/capes_abstracts/7850222.json`) and included as an **indirect** evidence row for `EXP:PEST → CHD:ALL`. The other 551 were excluded with an explicit reason in `literature/screening/capes_triage.csv`. Extended the build verifier and validation to accept the non-PMID source and re-check its quote against the archived abstract.

**Obtained.** 34 anchor studies (33 PMIDs + 1 CAPES thesis); 55 curated evidence rows (54 unique relations, because `EXP:PEST → CHD:ALL` now has two sources); 4,614 total evidence rows. The CAPES edge remains grade D / “Não demonstrada”; reviews are not counted as independent replication in the confidence aggregation.

**Problems.** Most retrieved theses were clinical/surgical/descriptive, not environmental-exposure studies; only one thesis was eligible. The included thesis is a review, not a primary study.

**Decision.** Treat CAPES as a complementary search source with explicit screening, not as a source of many new edges. **Apt to advance: yes, with the limitation documented.**

---

## Phase N: Recuperação exaustiva e camada de estudos triados (2026-11-01)

**Done.** Aplicada recuperação exaustiva às consultas pré-registradas de PubMed (domínios e pares), Europe PMC e SciELO via Crossref, além da CAPES já paginada. Os registros brutos foram gravados em JSONL gzip em `data_raw/literature/full/`; uma triagem automática gerou 3.963 candidatos únicos e um grafo separado de estudos triados.

**Obtained.** PubMed domínios 25.406/25.442; PubMed pares 663/666; Europe PMC 4.789; SciELO 83.157; CAPES 560. Candidatos únicos: 3.963; com fenótipo CHD detectado: 638; relações Study→conceito: 13.723.

**Problems.** O volume recuperado é muito maior do que o conjunto manualmente curável. A camada de estudos triados é automática e não pode ser tratada como evidência. A cobertura de metadados do SciELO/Crossref é limitada e gerou apenas 2 candidatos.

**Decision.** Manter duas camadas separadas: (i) evidência manual, com 34 estudos-âncora e 54 relações únicas; (ii) estudos triados, não evidenciais, para auditoria e priorização. **Apt to advance: yes, as a transparent screening layer; manual curation remains the bottleneck.**

---

## Phase O: Promoção em lote com camada de revisão (2026-11-01)

**Done.** Implementada a promoção em lote dos 635 candidatos com fenótipo CHD e PMID. A extração automática passou a ser determinística e testável (`src/graphambicardio/curation/batch_extract.py`), com regras estritas de cláusula única. Nenhum candidato entra no grafo diretamente: a revisão fica registrada em `literature/curated/batch_chd_review.csv` (`src/graphambicardio/curation/batch_review.py`), e a construção do grafo rejeita linhas verificadas sem citação verbatim no PubMed. Foi criado também um pacote de leitura humana (`reports/batch_chd_review_packet.md`) e testes unitários para as regras e para a camada de revisão.

**Obtained.** 635 candidatos com PMID; 23 candidatos automáticos revisados; **29 arestas verificadas**; 5 recusados; 605 registros ainda sem decisão. Os recusados foram uma publicação duplicada (PMID 2091934, mesmo dado de PMID 1397217), um efeito de exposição combinada PM10 + CO (PMID 37610216), duas redescobertas de arestas já curadas manualmente (PMID 32278917 e PMID 35916623) e uma estimativa de solvente para CoA/VSD (PMID 11745829), que não é VSD isolado. Dois achados condicionais foram aceitos com ressalva explícita (PMID 28520847 e PMID 32091506). O grafo passou a 2.238 nós, 4.135 relações e 4.639 linhas de evidência; 49 caminhos exposição a fenótipo (39 diretos, 10 mecanísticos).

**Problems.** A revisão foi assistida por IA e feita por um único revisor. A segunda passagem recuperou 11 propostas adicionais e a triagem heurística mostrou que 97 dos registros restantes são estudos humanos com tamanho de efeito, 172 são humanos sem confirmação da exposição ou do fenótipo candidato, 165 são animais ou celulares, 60 são cirúrgicos ou diagnósticos, 17 são revisões, 93 não têm sinal suficiente e 1 não tem resumo. A promoção em lote não substitui leitura humana independente.

**Decision.** Manter a curadoria em lote como camada separada, auditável e conservadora, sempre marcada em `source_database` e nas notas da evidência, com segunda passagem por proposta e triagem explícita da fila restante. **Apt to advance: yes, as reviewed auxiliary curation; human confirmation remains the final gate.**
