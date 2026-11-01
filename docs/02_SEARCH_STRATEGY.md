# 02: Search strategy, PRISMA-ScR flow and reproducibility

**Retrieval date for all searches:** 2026-10-31 (UTC).
**Study period for local epidemiology:** 2010-01-01 to 2025-12-31. This period was **not** applied to biological literature.

---

## 1. Sources and interfaces

| Source | Interface used | Status | Notes |
|---|---|---|---|
| PubMed/MEDLINE | NCBI E-utilities (`esearch`, `efetch`, XML) | Used | 3 req/s without key; 10 req/s with `NCBI_API_KEY` |
| Europe PMC | REST `/search` (JSON, `resultType=core`) | Used | independent discovery + open access |
| SciELO | `search.scielo.org` (HTML) | **HTTP 403** | direct interface blocked; fallback via Crossref (below) |
| SciELO (metadados) | Crossref `prefix:10.1590` | **Used** | official DOI metadata for SciELO articles; 100 records/query |
| CAPES (Catálogo de Teses) | `catalogodeteses.capes.gov.br` REST | **Used** | 560 hits; 560 records retrieved (552 unique); 1 thesis included |
| Portal de Periódicos CAPES | web interface | Not automated | full text requires institutional authentication |
| Google Scholar | n/a | Not used | not reproducible; no record-level export |
| Reference lists | manual | Partially used | reviews and anchor papers checked for key references |

SciELO was ultimately accessed through **Crossref metadata restricted to the SciELO DOI prefix (10.1590)**, because the direct search interface returned HTTP 403/Bunny Shield to automated clients. CAPES was accessed through the **public Catálogo de Teses e Dissertações API**. These routes and their limitations are recorded in `09_LIMITATIONS_AND_GAPS.md`.

---

## 2. Concept blocks (PubMed syntax)

```
POPULATION
("heart defects, congenital"[MeSH] OR "congenital heart defect*"[tiab]
 OR "congenital heart disease*"[tiab] OR "congenital heart anomal*"[tiab]
 OR "cardiac anomal*"[tiab])

EXPOSURE
("environmental exposure"[MeSH] OR "air pollution"[MeSH] OR "particulate matter"[MeSH]
 OR "maternal exposure"[MeSH] OR "pesticides"[MeSH] OR "metals, heavy"[MeSH]
 OR "hot temperature"[MeSH] OR "solvents"[MeSH] OR "tobacco smoke pollution"[MeSH]
 OR "alcohol drinking"[MeSH] OR "valproic acid"[MeSH])

MECHANISM
("oxidative stress"[MeSH] OR "epigenesis, genetic"[MeSH] OR "inflammation"[MeSH]
 OR "signal transduction"[MeSH] OR "gene expression regulation, developmental"[MeSH]
 OR "mitochondria"[MeSH])

DEVELOPMENT
("cardiogenesis"[tiab] OR "heart development"[tiab] OR "embryonic heart"[tiab]
 OR "neural crest"[tiab] OR "outflow tract"[tiab] OR "septation"[tiab])
```

The MeSH-only exposure block has low recall for PM2.5, ozone, solvents and specific pesticides; the 14-exposure panel therefore uses **MeSH + free-text** combinations below.

---

## 3. Five pre-registered domain queries (exact strings)

These are the strings stored in `literature/searches/A*.json` (field `query`). Retrieve with `python scripts/collection/01_literature.py`.

| ID | Query |
|---|---|
| **A1** | `EXPOSURE AND POPULATION` |
| **A2** | `EXPOSURE AND MECHANISM AND (cardiac OR heart OR embry* OR pregnancy OR placenta*)` |
| **A3** | `MECHANISM AND DEVELOPMENT` |
| **A4** | `DEVELOPMENT AND POPULATION` |
| **A5** | `(NKX2-5 OR GATA4 OR TBX5 OR NOTCH1 OR TBX1 OR JAG1) AND ("congenital heart"[tiab] OR "heart defect"[tiab] OR "cardiac malformation"[tiab])` |

`retmax = 100` per domain, sorted by relevance, no date filter (biological literature is not restricted to 2010–2025).

### Results

| ID | PubMed hits | Retrieved | Europe PMC hits | Europe PMC retrieved |
|---|---:|---:|---:|---:|
| A1 | 1,512 | 100 | 1,599 | 100 |
| A2 | 8,520 | 100 | 171 | 100 |
| A3 | 6,736 | 100 | 39 | 39 |
| A4 | 7,681 | 100 | 593 | 100 |
| A5 | 992 | 98 | 2,387 | 100 |

Europe PMC translation: `[tiab]` → `TITLE_ABS:`, `[MeSH]` → `MESH:`. The translation is stored verbatim in each `*_europepmc.json` (`query_translation`). Europe PMC does not accept the PubMed field tags; the translated query is a **recall-oriented approximation**, not an identical query.

---

## 4. Exposure × phenotype matrix (196 queries)

Template:

```
(EXPOSURE_TERMS)
AND ("congenital heart"[tiab] OR "congenital heart disease*"[tiab]
     OR "heart defects, congenital"[MeSH] OR "cardiac malformation*"[tiab])
AND (PHENOTYPE_TERMS)
AND (pregnan*[tiab] OR maternal[tiab] OR prenatal[tiab] OR teratogen*[tiab]
     OR "birth defect*"[tiab] OR embry*[tiab] OR "in utero"[tiab])
```

- 14 exposures × 14 phenotypes = **196 queries**.
- `retmax = 15` per pair (manual feasibility screening), `retmax = 0` for exposure × mechanism counts.
- Total pair hits: **546**; records retrieved: **513**.
- Full strings: `reports/feasibility_pair_matrix.csv` (column `query`).

### Exposure terms (PubMed)

| Exposure | Terms |
|---|---|
| PM2.5 | `"particulate matter"[MeSH] OR "PM2.5"[tiab] OR "PM 2.5"[tiab] OR "fine particulate matter"[tiab]` |
| NO2/traffic | `"nitrogen dioxide"[MeSH] OR "nitrogen dioxide"[tiab] OR "NO2"[tiab] OR "traffic-related air pollution"[tiab]` |
| O3 | `"ozone"[MeSH] OR "ozone"[tiab]` |
| SO2 | `"sulfur dioxide"[MeSH] OR "sulfur dioxide"[tiab] OR "sulphur dioxide"[tiab]` |
| Heat | `"hot temperature"[MeSH] OR "hyperthermia"[MeSH] OR "hyperthermia"[tiab] OR "heat wave*"[tiab] OR "high temperature"[tiab]` |
| Cold | `"cold temperature"[MeSH] OR "cold spell*"[tiab] OR "low temperature"[tiab]` |
| Pesticides | `"pesticides"[MeSH] OR "pesticide*"[tiab] OR "organophosphate*"[tiab] OR "glyphosate"[tiab] OR "insecticide*"[tiab] OR "herbicide*"[tiab]` |
| Solvents | `"solvents"[MeSH] OR "trichloroethylene"[MeSH] OR "benzene"[MeSH] OR "organic solvent*"[tiab] OR "trichloroethylene"[tiab] OR "benzene exposure"[tiab]` |
| Metals | `"arsenic"[MeSH] OR "lead"[MeSH] OR "mercury"[MeSH] OR "metals, heavy"[MeSH] OR "heavy metal*"[tiab]` |
| Tobacco | `"tobacco smoke pollution"[MeSH] OR "smoking"[MeSH] OR "tobacco smoke"[tiab] OR "cigarette smoke"[tiab]` |
| Alcohol | `"ethanol"[MeSH] OR "alcohol drinking"[MeSH] OR "alcohol"[tiab] OR "ethanol"[tiab] OR "fetal alcohol"[tiab]` |
| Valproate | `"valproic acid"[MeSH] OR "valproic acid"[tiab] OR "valproate"[tiab]` |
| Retinoic acid | `"tretinoin"[MeSH] OR "retinoic acid"[tiab] OR "isotretinoin"[tiab] OR "vitamin A"[tiab]` |
| Dioxins/PCBs | `"dioxins"[MeSH] OR "polychlorinated biphenyls"[MeSH] OR "dioxin*"[tiab] OR "TCDD"[tiab] OR "polychlorinated biphenyl*"[tiab] OR "PCB"[tiab]` |

### Phenotype terms

Each phenotype uses its label and accepted variants in `[tiab]` (e.g. VSD: `"ventricular septal defect"`, `"ventricular septal defects"`, `"VSD"`). Abbreviations are only used inside the CHD context block. Full mapping in `src/graphambicardio/config.py` (`PHENOTYPE_QUERY_TERMS`).

**Rationale for the context block:** without it, the matrix retrieved surgical/anaesthetic case reports and adult disease. With it, precision improved but 73 pairs dropped to zero, an honest reflection of the literature, not a search failure.

---

## 4.1 Buscas em R (SciELO e CAPES)

```bash
Rscript R/collection/scielo.R   # Crossref, prefixo 10.1590
Rscript R/collection/capes.R    # Catálogo de Teses e Dissertações
```

Resultados em `literature/searches/scielo_*.json` e `capes_*.json`:

| Busca | Fonte | Resultado |
|---|---|---:|
| cardiopatia congênita + exposição ambiental | SciELO/Crossref | 100 recuperados; 50 com termos de CHD |
| cardiopatia congênita + poluição do ar/PM | SciELO/Crossref | 100 recuperados; 42 com termos de CHD |
| cardiopatia congênita + agrotóxicos | SciELO/Crossref | 100 recuperados; 42 com termos de CHD |
| cardiopatia congênita + temperatura/calor | SciELO/Crossref | 100 recuperados; 60 com termos de CHD |
| cardiopatia congênita + umidade | SciELO/Crossref | 100 recuperados; 50 com termos de CHD |
| cardiopatias congênitas | CAPES Teses | 552 hits (todos recuperados) |
| poluição do ar + cardiopatia | CAPES Teses | 0 |
| agrotóxicos + cardiopatia | CAPES Teses | 1 |
| temperatura + cardiopatia congênita | CAPES Teses | 7 |

A API do Catálogo de Teses devolve no máximo 20 itens por página; o coletor agora percorre todas as páginas. Foram recuperados **560 registros** (552 IDs únicos; 8 repetidos entre consultas). Os 552 registros únicos foram triados por título; **1 tese** (revisão sistemática sobre agrotóxicos e malformações congênitas) foi lida em nível de resumo e incluída como evidência indireta para `EXP:PEST → CHD:ALL`. As outras 551 foram excluídas por não avaliarem exposição ambiental específica ou por serem estudos clínicos/cirúrgicos. Decisões em `literature/screening/capes_triage.csv`; ver `docs/16_CAPES_MCP.md`.

## 5. Deduplication and screening flow (PRISMA-ScR)

Deduplication key precedence: PMID → DOI → normalised title (alphanumeric, lower-case, first 200 characters).

| Stage | Records | Notes |
|---|---:|---|
| PubMed domain searches (5) | 498 | top 100 per domain |
| PubMed pair searches (196) | 513 | top 15 per pair |
| Europe PMC searches (5) | 439 | top 100 / all available |
| SciELO via Crossref (5) | 500 | 100 per query |
| CAPES Teses (4) | 560 | all pages retrieved; 552 unique IDs |
| **Total raw records** | **2,510** | includes repeats across pair searches |
| Duplicates removed | 540 | within-source repeats + PMID/DOI/title |
| **Unique records screened** | **1,970** | title/abstract (automated triage) |
| Unique with abstract (PubMed/Europe PMC subset) | 1,003 | 91.6% of that subset |
| Manually curated anchor studies | 34 | 55 evidence rows = 54 unique relations (33 PMIDs + 1 CAPES thesis) |
| Batch curation from the exhaustive layer | 29 | 23 first-pass candidates plus 11 second-pass proposals and one manual addition; 5 rejected (2 already curated, 1 duplicate publication, 1 combined exposure, 1 combined CoA/VSD) |

Machine-readable: `reports/prisma_flow.csv`.

### Cobertura real por base (o que foi recuperado)

A busca é **top-N** para PubMed, Europe PMC e SciELO; apenas a CAPES foi recuperada em todas as páginas. Isso é uma assimetria deliberada e declarada:

| Base | Hits totais | Registros recuperados | Estratégia |
|---|---:|---:|---|
| PubMed (domínios) | 25.441 | 498 | top 100 por domínio |
| PubMed (pares) | 546 | 513 | top 15 por par (123 pares com hits) |
| Europe PMC | 4.789 | 439 | top 100 por domínio |
| SciELO via Crossref | 83.157 | 500 | top 100 por consulta |
| CAPES Teses | 560 | 560 | todas as páginas (552 IDs únicos) |

Os números de hits do SciELO são altos porque a consulta Crossref é ampla e o filtro de prefixo 10.1590 não é um mecanismo de busca preciso. A cobertura detalhada está em `reports/retrieval_coverage.csv` e `.md`.

### Recuperação exaustiva e camada de estudos triados

Depois da revisão, foi executada uma recuperação **exaustiva** de todas as consultas pré-registradas:

| Base | Hits totais | Recuperados | Candidatos (antes de dedup) |
|---|---:|---:|---:|
| PubMed, domínios | 25.442 | 25.406 | 4.181 |
| PubMed, pares | 666 | 663 | 485 |
| Europe PMC | 4.789 | 4.789 | 477 |
| SciELO via Crossref | 83.157 | 83.157 | 2 |
| CAPES Teses | 560 | 560 | 1 (após triagem manual) |

Após deduplicação, há **3.963 estudos candidatos**; **638** têm fenótipo CHD detectado. Eles foram organizados em uma **camada separada** (`outputs/graph/screened_studies.json`), com **13.723 relações Study→conceito**. Essa camada é gerada por triagem automática, **não é evidência** e não entra em `evidence.csv`, caminhos, centralidade ou conclusões.

A triagem automática de todos os registros recuperados está em `literature/screening/all_records_triage.csv`; os candidatos estão em `literature/screening/exhaustive_candidates.csv`; os resumos com SHA-256 dos arquivos brutos estão em `reports/exhaustive_retrieval.csv`. Os registros brutos compactados ficam em `data_raw/literature/full/` (não versionado, re-downloadable).

### Screening procedure actually used

1. **Automated triage** of all retrieved records (`literature/screen.py`): species, study design, exposure-window vocabulary, mechanism vocabulary, phenotype vocabulary, review flag.
2. **Manual reading** of 34 anchor studies (33 PMIDs + 1 CAPES thesis) selected to cover: each exposure with positive human evidence, each mechanism with experimental evidence, each process→phenotype link, and the classic gene discoveries. All 552 unique CAPES records were title-screened; one thesis was read at abstract level and included. In addition, 23 first-pass candidates and 11 second-pass proposals from the exhaustive layer were reviewed; 29 became evidence and 5 were rejected.
3. **Audit** of quote fidelity at build time (100%) and re-check of a random 25% at validation time.

This is **not a systematic review**. It is a structured, non-systematic search with targeted manual curation: there was no dual screening of all records, no full-text review and no formal risk-of-bias instrument.

---

## 6. Inclusion / exclusion applied to anchor studies

Included:
- human epidemiological studies with a defined exposure window and CHD outcome;
- experimental studies with a defined species/model and a cardiac developmental endpoint;
- human genetics with variant-level evidence;
- reviews used **only** as indirect synthesis.

Excluded:
- case reports of anaesthetic/surgical management;
- adult cardiac disease without congenital context;
- technical/methodological papers matching keywords incidentally;
- records without abstract or with unverifiable claims;
- predatory/non-indexed sources.

Examples of excluded retrieved records: PMID 1939319 and 9301187 (malignant hyperthermia during TOF surgery), PMID 34021458 (ultrasound phantom for VSD training), PMID 17692954 (smoking and mortality in adults with CHD).

---

## 7. Reproducibility

```bash
# all searches are cached under data_raw/http_cache; re-running is idempotent
.venv/Scripts/python.exe scripts/collection/01_literature.py
```

Each `literature/searches/*.json` stores: search ID, database, exact query, query translation, date filter, sort, retrieval date, total count, retrieved count and every record (PMID, DOI, title, journal, year, authors, abstract, publication types, MeSH terms).

To audit a query, open the corresponding JSON and compare `query`, `count_total` and `retrieved_at`.
