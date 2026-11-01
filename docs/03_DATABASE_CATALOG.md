# 03 — Catalogue of databases and access status

**Probe date:** 2026-10-31. “Status” refers to what the pipeline actually used, not what exists in principle.

Legend: **Used** = records in the graph; **Probed** = accessed but not used; **Blocked** = technical/licence barrier; **Not used** = deliberately excluded (reason given).

---

## 1. Literature and bibliographic metadata

### 1.1 PubMed / MEDLINE (NCBI E-utilities)
- **URL:** https://eutils.ncbi.nlm.nih.gov/entrez/eutils/
- **Entities:** PMID, title, abstract, journal, year, authors, DOI, publication types, MeSH terms.
- **Coverage:** biomedical literature; no date restriction for biological domains.
- **Access:** REST/XML; 3 req/s without key, 10 req/s with `NCBI_API_KEY`.
- **Licence/terms:** NLM terms; abstracts are quoted only as short verbatim fragments for verification.
- **Used:** 5 domain searches + 196 pair searches + 33 anchor studies.
- **Limitations:** indexing lags; no full-text; MeSH-only queries have low recall for emergency pollutants.

### 1.2 Europe PMC
- **URL:** https://www.ebi.ac.uk/europepmc/webservices/rest
- **Entities:** PMID, PMCID, DOI, title, abstract, journal, year, open-access flag.
- **Access:** public REST JSON.
- **Used:** 5 domain searches (independent discovery).
- **Limitation:** query syntax differs from PubMed; the translation is recorded per search.

### 1.3 SciELO
- **Status: Used via Crossref (DOI prefix 10.1590).**
- The direct SciELO search interface (`search.scielo.org`) returned **HTTP 403 / Bunny Shield** to automated clients; the R collector therefore queries Crossref, which indexes SciELO articles with the official 10.1590 prefix.
- **Results:** 100 records per query; 42–60 contained CHD terms plus exposure terms.
- **Limitation:** Crossref search is metadata-based (title/abstract), not the full SciELO search engine; relevance ranking differs.

### 1.4 CAPES
- **Status: Used (Catálogo de Teses e Dissertações only).**
- Public REST endpoint `https://catalogodeteses.capes.gov.br/catalogo-teses/rest/busca` (POST JSON, field `termo`). R collector in `R/collection/capes.R`.
- **Results:** 552 theses/dissertations for “cardiopatias congênitas” (20 retrieved on the first page); 1 for agrotóxicos; 7 for temperatura; 0 for poluição do ar + cardiopatia.
- **Limitation:** this is the thesis catalogue, **not** the paywalled Portal de Periódicos full-text collection. The Portal requires institutional authentication and was not used.


---

## 2. Genes, variants and phenotypes

### 2.1 Human Phenotype Ontology (HPO)
- **URL:** https://hpo.jax.org/ ; API https://ontology.jax.org/api/hp
- **Entities:** HPO terms, definitions, synonyms, xrefs; gene-to-phenotype annotations.
- **Files used:** `genes_to_phenotype.txt` (release *latest* on 2026-10-31), term metadata via API.
- **Coverage:** 2,803 annotations for the 14 sentinel terms, **814 genes**.
- **Licence:** HPO ontology/annotations are openly available (see HPO site); xrefs to OMIM/Orphanet retain their own terms.
- **Used:** phenotype labels/definitions and gene→phenotype structured edges.
- **Limitation:** Mendelian/syndromic orientation; frequency strings are heterogeneous (`1/6`, `HP:0040283`, `-`).

### 2.2 ClinVar
- **URL:** https://www.ncbi.nlm.nih.gov/clinvar/ (E-utilities `db=clinvar`)
- **Entities:** variant accession, classification, review status, trait set, cDNA change, molecular consequence.
- **Query:** `GENE[gene] AND (pathogenic[clinsig] OR "likely pathogenic"[clinsig])`, 50 records/gene.
- **Used:** 945 pathogenic/likely pathogenic variants after excluding large CNVs; 150 variant→phenotype matches.
- **Limitations:** classification is submitter-dependent; traits are syndrome-level; NOTCH1’s bicuspid valve phenotype does not map cleanly to Q23.0.

### 2.3 NCBI Gene
- **URL:** https://www.ncbi.nlm.nih.gov/gene/ (E-utilities `db=gene`)
- **Used:** stable NCBI Gene IDs and descriptions for 170 genes (panel + HPO top-150).
- **Limitation:** HPO genes outside the top-150 lack NCBI metadata in this version.

### 2.4 OMIM — **Not used (licence).** Access requires registration/licence; content was not redistributed.
### 2.5 Orphanet — **Not used.** No stable programmatic endpoint was required for this version; HPO xrefs to ORPHA IDs are retained where present.
### 2.6 DisGeNET — **Blocked.** Current API requires a key; not used.
### 2.7 Monarch Initiative — **Probed**, not used systematically. Its API was reachable and cross-checks NKX2-5, but HPO files provided the needed annotations with simpler provenance.
### 2.8 GWAS Catalog — **Not used.** No CHD GWAS signal was required for the first graph version; phenotype harmonisation across studies would be needed.
### 2.9 Ensembl / UniProt — **Not used for nodes.** NCBI Gene IDs are the primary gene key; Reactome accepts gene symbols. A future version should add Ensembl/UniProt accession mapping.

---

## 3. Pathways and functional annotation

### 3.1 Reactome
- **URL:** https://reactome.org/ ; Analysis Service `https://reactome.org/AnalysisService`
- **Method:** one over-representation analysis per gene (`projection`, FDR < 0.05), so each gene→pathway edge has its own provenance.
- **Used:** 1,956 gene–pathway results; **649** retained after a developmental/cardiac keyword filter; **248** pathway nodes.
- **Limitations:** pathway names are broad; the keyword filter is a documented heuristic; single-gene over-representation is not a biological validation.

### 3.2 Gene Ontology / Enrichr
- **URL:** https://maayanlab.cloud/Enrichr/
- **Library:** `GO_Biological_Process_2023`; 1,631 enriched terms for the gene universe (listed in `data_processed/enrichr_GO_Biological_Process_2023.csv`).
- **Used:** descriptive over-representation only; **not** encoded as graph edges (GO term→gene mapping was not resolved per gene in this version).
- **Limitation:** Enrichr is a third-party service; terms are statistical, not causal.

### 3.3 KEGG — **Not used.** REST access and redistribution terms require care; Reactome covered the pathway layer.
### 3.4 Comparative Toxicogenomics Database (CTD) — **Blocked.** The batch-query endpoint redirected to a human-verification page (“verify you are a human”) on 2026-10-31; no automated retrieval was possible.
### 3.5 ToxCast / PubChem — **Not used.** ToxCast does not provide human developmental cardiac outcomes at the required granularity; PubChem was unnecessary because exposures were represented at the class level.

---

## 4. Expression data

### 4.1 GEO — **Not used in v0.1.0 (deliberate).**
GEO was evaluated but no dataset was admitted. Rationale: adult myocardial expression or non-cardiac tissue cannot be interpreted as cardiogenesis; embryonic cardiac datasets require careful stage/species matching that was outside the scope of this version. Adding GEO without that curation would violate the study’s own rules. The pipeline leaves a placeholder for future stage-specific embryonic datasets.

---

## 5. Local epidemiological data

### 5.1 SINASC (Live Birth Information System)
- **URL:** DATASUS FTP `.../SINASC/NOV/DNRES/` and `.../SINASC/PRELIM/DNRES/`
- **Files:** `DNRJ{year}.dbc` (Rio de Janeiro state), converted with `pyreaddbc` and read with `dbfread`.
- **Coverage obtained:** 2010–2022 microdata (consolidated) and **2025 (preliminary)**. **2023 and 2024 microdata were absent from the FTP**; aggregate counts were obtained from **TabNet** (`nvrj23.dbf`, `nvrj24.dbf`).
- **Fields used:** CODMUNRES, DTNASC, SEXO, IDANOMAL, CODANOMAL, IDADEMAE, ESCMAE, GESTACAO, SEMAGESTAC, PESO, APGAR1/5, GRAVIDEZ, PARTO, CONSULTAS, RACACOR.
- **Limitation:** `CODANOMAL` concatenates 4-character codes; CHD ascertainment at birth is incomplete (59 cases in 98,598 births).

### 5.1b TabNet (SINASC aggregates)
- **URL:** `http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sinasc/cnv/nvRJ.def`
- **Method:** Latin-1 form POST after session handshake (script `src/graphambicardio/epi/tabnet.py`).
- **Obtained:** 2022 (control), 2023, 2024 and 2025 births and Q20–Q28 group counts.
- **Validated:** 2025 TabNet (5.924 births, 9 cases) matches the microdata exactly.
- **Limitation:** TabNet counts only records whose anomaly group is “malformações congênitas do aparelho circulatório”; the microdata parser counts **any** Q20–Q28 code. The two series are kept separate.

### 5.2 SIH/SUS (Hospital admissions)
- **URL:** DATASUS FTP `.../SIHSUS/200801_/Dados/RDRJ{yy}{mm}.dbc`
- **Coverage:** 192 monthly files, 2010–2025.
- **Fields used:** MUNIC_RES, MUNIC_MOV, DIAG_PRINC, DIAG_SECUN, CID_ASSO, CID_MORTE, DT_INTER, DT_SAIDA, DIAS_PERM, MORTE, VAL_TOT, CAR_INT, IDADE, COD_IDADE, SEXO, N_AIH, CNES.
- **Limitation:** AIH ≠ person; no stable patient identifier; 55% of admissions occur outside the municipality.

### 5.3 Population denominators
Not fetched in v0.1.0. The birth-level models use SINASC live births as the denominator; SIH indicators are reported as counts. A future version should add IBGE population estimates for age-specific rates.

---

## 6. Environmental data

### 6.1 INMET — **Used for validation.**
- **Station:** A607 (Campos dos Goytacazes/RJ; latitude −21,7167; longitude −41,3500; altitude 25 m; automatic station).
- **Access:** R package `BrazilMet` 0.5.0 (`download_AWS_INMET_daily`), historical files at `https://portal.inmet.gov.br/uploads/dadoshistoricos/`.
- **Variables:** Tmean, Tmax, Tmin, relative humidity (mean/min/max), rainfall, wind.
- **Coverage:** 5,754 days, 2010-01-01 to 2025-12-31; 138 missing Tmax and 153 missing RH.
- **Role:** validation/comparison with ERA5-Land (Tmax r=0.94; Tmin r=0.94; Tmean r=0.97; RH r=0.81), not personal exposure.
- **Limitation:** automatic station; sensor gaps and local siting; does not represent the whole municipality.
### 6.2 ERA5 / ERA5-Land via Open-Meteo — **Used.**
- **URL:** https://archive-api.open-meteo.com/v1/archive
- **Variables:** Tmean, Tmax, Tmin, relative humidity, precipitation, wind.
- **Grid cell returned:** latitude −21.757, longitude −41.354, elevation 12 m (requested −21.7545, −41.3245).
- **Coverage:** 5,844 days, 2010-01-01 to 2025-12-31, no missing Tmax.
- **Licence/terms:** Open-Meteo terms; underlying ERA5 data © Copernicus.
- **Limitation:** reanalysis grid cell, not a station; ~9 km resolution; no personal exposure.

### 6.3 PM2.5 — **Used: VIGIAR via `vigiar`.**
- **Source:** VIGIAR (Vigilância em Saúde Ambiental, Ministério da Saúde), dashboard público Power BI, accessed with the R package `vigiar` 0.7.2 (`R/collection/pm25_vigiar.R`).
- **Coverage:** annual 2010–2025 (16 values) and monthly 2010–2025 (192 values) for municipality 330100.
- **Values:** annual 6.50–9.04 µg/m³ (mean 7.72); monthly 3.83–13.84 µg/m³.
- **Access note:** the Power BI endpoint caps responses at ~30,000 rows; the collector filters server-side by municipality code instead of downloading all of Brazil.
- **Limitations:** municipal area-level estimate, not a local monitoring station; cannot represent street-level, indoor or personal exposure. The VIGIAR series is used in exploratory ecological models, never as individual exposure.

---

## 7. Compatibility and identifiers

| Entity | Primary key | Secondary identifiers | Conflict handling |
|---|---|---|---|
| Gene | `GENE:<symbol>` | NCBI Gene ID | symbol from NCBI/HPO; duplicates by symbol resolved |
| Phenotype | `CHD:<abbrev>` | CID-10, HPO, OMIM (where applicable) | mapping table with explicit caveats |
| Variant | `VAR:<ClinVar accession>` | cDNA change | large CNVs excluded from gene attribution |
| Pathway | `PATH:<Reactome stId>` | Reactome dbId | stable stId |
| Study | PMID | DOI | PMID is the join key |
| Exposure | `EXP:<abbrev>` | class (air pollutant, chemical, climate, medication) | class-level nodes, not mixture-specific |

**Versioning:** every output table carries `retrieved_at`. HPO file release date is recorded next to the download (`data_raw/external/genes_to_phenotype.retrieved_at`).

---

## 8. What was deliberately not used, and why

- **CTD** (captcha), **DisGeNET** (key), **OMIM** (licence), **SciELO search interface** (403): access barriers, all documented. **INMET** was initially unreachable through the portal but was later obtained via `BrazilMet` and is used for validation (section 6.1).
- **GEO**: no dataset met the stage/species/tissue criteria.
- **KEGG**: Reactome covered the pathway layer.
- **ToxCast/PubChem**: exposure classes, not individual chemicals, were the unit of analysis.
- **GWAS Catalog**: no CHD GWAS harmonisation performed in this version.
