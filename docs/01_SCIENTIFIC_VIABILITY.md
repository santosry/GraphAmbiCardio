# 01: Scientific viability assessment (Phase A)

**Decision document.** Date of retrieval: 2026-10-31.
All counts below were produced by the pipeline (`reports/feasibility_*.csv`, `literature/searches/*.json`) and are reproducible.

---

## 1. What was assessed

Five connection domains were searched separately, because they answer different questions and have different evidence standards:

| ID | Connection | Why it is a separate domain |
|---|---|---|
| A1 | environmental exposure → CHD | requires human epidemiological design with prenatal exposure |
| A2 | exposure → molecular mechanism | can be human biomarker, animal or cell study |
| A3 | mechanism → cardiogenesis | almost exclusively experimental |
| A4 | cardiogenesis → CHD phenotype | developmental/embryological inference |
| A5 | gene/protein → CHD phenotype | human genetics + curated annotations |

In addition, **196 exposure × phenotype pairs** were queried to quantify where the literature is dense, sparse or absent. The pair query forces a prenatal/developmental context (`pregnan* OR maternal OR prenatal OR teratogen* OR "birth defect*" OR embry* OR "in utero"`) to reduce contamination by adult cardiac disease and surgical case reports.

### Important caveat established during Phase A

Bibliometric volume is **not** evidence strength. Automated triage of the top records showed that high-recall queries still retrieve:
- anaesthetic/surgical case reports (e.g. “malignant hyperthermia” during tetralogy of Fallot repair, PMID 1939319, 9301187);
- adult cardiac disease and valve surgery;
- technical papers using the same words (e.g. ultrasound phantoms for VSD training, PMID 34021458).

Therefore the pair matrix is used only to decide **where to look**, never to grade evidence. Grades come from manually read anchor studies.

---

## 2. Results by domain

| Domain | PubMed hits | Screened (top 100) | Human* | Animal* | Reviews* | With mechanism terms* |
|---|---:|---:|---:|---:|---:|---:|
| A1 exposure → CHD | 1,512 | 100 | 83 | 11 | 14 | 25 |
| A2 exposure → mechanism | 8,520 | 100 | 84 | 40 | 22 | 93 |
| A3 mechanism → cardiogenesis | 6,736 | 100 | 13 | 71 | 30 | 100 |
| A4 cardiogenesis → phenotype | 7,681 | 100 | 32 | 56 | 38 | 69 |
| A5 gene → phenotype | 992 | 98 | 38 | 41 | 14 | 44 |

\*Automated triage flags on the screened records; not mutually exclusive and not a quality assessment.

Europe PMC (independent discovery source): **1,599 / 171 / 39 / 593 / 2,387** hits for A1–A5. The much lower A3 count reflects the narrower free-text query accepted by Europe PMC.

### Exposure × phenotype matrix (196 pairs)

| Volume stratum | Pairs | Share |
|---|---:|---:|
| No direct literature | 73 | 37.2% |
| Sparse (1–2) | 66 | 33.7% |
| Limited (3–7) | 36 | 18.4% |
| Moderate (8–19) | 19 | 9.7% |
| High (≥20) | 2 | 1.0% |

The two “high” pairs were **alcohol → VSD** (32 records) and **retinoic acid → TGA** (20). PM2.5, NO2, pesticides, solvents, tobacco, metals and heat were mostly in the sparse-to-moderate range. Cold and dioxins/PCBs had 5 records each across all 14 phenotypes.

### Per-exposure totals (all 14 phenotypes)

| Exposure | Total records | Pairs with ≥1 | Human-triage hits |
|---|---:|---:|---:|
| Alcohol | 101 | 13 | 61 |
| PM2.5 | 76 | 11 | 66 |
| Retinoic acid | 72 | 10 | 23 |
| NO2/traffic | 55 | 8 | 50 |
| Pesticides | 50 | 12 | 41 |
| Tobacco smoke | 35 | 11 | 35 |
| Heavy metals | 34 | 8 | 31 |
| Ozone | 32 | 9 | 31 |
| SO2 | 27 | 8 | 27 |
| Organic solvents | 24 | 9 | 21 |
| Valproic acid | 16 | 9 | 16 |
| Heat | 14 | 5 | 14 |
| Cold | 5 | 5 | 4 |
| Dioxins/PCBs | 5 | 5 | 3 |

### Exposure × mechanism counts (selected)

Very large volumes exist for retinoic acid → gene expression (3,653), heavy metals → oxidative stress (2,247), heavy metals → gene expression (1,739), heavy metals → mitochondria (1,597), alcohol → oxidative stress (1,148), tobacco → inflammation (1,062). These are **domain-level** counts and do not establish that the mechanism mediates the CHD association.

---

## 3. Viability by connection type

### 3.1 Exposure → CHD (direct human evidence)

**Verdict: viable, but phenotype-specific and heterogeneous.**

Anchors verified by reading (see `literature/curated/`):
- Heat → ASD: cohort of 704,209 fetuses, PR 1.37 (1.10–1.70) (PMID 27494594).
- PM2.5 → perimembranous VSD: OR 1.34 (0.98–1.83), **non-significant** (PMID 26705853).
- NO2 → coarctation: OR 1.14 (1.02–1.26); O3 → ASD: OR 1.09 per 10 ppb (1.02–1.17); PM2.5 → TOF marginal (PMID 32278917, meta-analysis).
- Valproate → CHD: RR 2.53 (2.16–2.96) vs other antiepileptics (PMID 41161707).
- Alcohol → d-TGA: OR 1.64 (1.17–2.30), but **null for overall CHD** (PMID 26110619).
- Smoking → TOF: RR 9.84 (2.49–38.84); smoking → overall CHD RR 2.65 (1.76–3.98) (PMID 35916623).
- Occupational metal dust/fumes → CHD: OR 2.40 (1.09–5.30) (PMID 33135766).
- Pesticides/solvents: only review-level statements (PMID 30257432), not usable as phenotype-specific evidence.

**Limitations:** exposure misclassification, residual confounding, phenotype heterogeneity, inconsistent exposure windows, publication bias. The PM2.5, pesticide and solvent edges do **not** meet a “demonstrated association” bar.

### 3.2 Exposure → molecular mechanism

**Verdict: viable for a subset; human evidence is mostly biomarker-based.**

- PM2.5 → inflammation: human pregnancy cohort, CRP increase (PMID 34934889).
- PM2.5 → oxidative stress / epigenetic change: review-level synthesis only (PMID 34253165), graded **indirect**.
- Heat → neural crest perturbation: chick/zebrafish TRPV1/TRPV4 mechanism (PMID 29018170): **experimental animal**.
- Valproate → HDAC inhibition: zebrafish heart malformation with HDAC-inhibitor rationale (PMID 32699959); HDAC requirement in valve formation (PMID 22634317).
- Dioxin → AHR: human ESC cardiomyocyte differentiation (PMID 30266049): **human experimental**.
- Alcohol → retinoic-acid-sensitive cardiogenesis: zebrafish rescue experiment (PMID 23832875).
- Smoking → epigenetic (miRNA) mechanisms: review only (PMID 31556862): **indirect**.

**Limitations:** animal/cell mechanisms cannot be assumed to operate at human environmental doses; biomarker associations in late pregnancy are not developmental mechanisms.

### 3.3 Mechanism → cardiogenesis

**Verdict: viable, but almost entirely experimental (animal/human cells).**

- Oxidative stress → cardiac neural crest apoptosis/migration → OFT defects (mouse; PMID 18435457). Note: upstream exposure was maternal diabetes, not an environmental pollutant.
- HDAC → Wnt/β-catenin → AVC cushion EMT (zebrafish; PMID 22634317).
- AHR → cardiomyocyte differentiation (human ESC; PMID 30266049); AHR → looping/endocardial integrity (zebrafish/sturgeon; PMID 33662880).
- Retinoic acid → looping and OFT septation (review of animal work; PMID 31021052).
- Neural crest → OFT septation (review; PMID 32071091).

### 3.4 Cardiogenesis → phenotype

**Verdict: viable only as indirect developmental inference.**

Descriptive human embryology (Carnegie stages; PMID 38884703) establishes the timing (heart tube end of week 4, looping week 5, chambers week 6, septation weeks 7–8; basic layout 26–32 days). Reviews of OFT, AV cushion and neural crest (PMIDs 24014420, 16107477, 32071091) support the mapping from process failure to phenotype groups. No study directly tests “process X failure causes phenotype Y” in a population; these edges are correctly graded **indirect (D)**.

### 3.5 Genes/proteins/pathways → phenotype

**Verdict: strong, structured and quantifiable.**

- HPO release: **2,803 gene–phenotype annotations** across **814 genes** for the 14 sentinel HPO terms.
- ClinVar: **945 pathogenic/likely pathogenic variants** (after excluding large CNVs) across the 47-gene panel; **150 variant–phenotype edges** where the trait text matched the study vocabulary.
- Reactome: **649 developmental/cardiac gene–pathway edges** (FDR < 0.05) for 170 genes.
- Classic human genetics anchors: NKX2-5 (PMID 9651244, 10587520), GATA4 (12845333), TBX5 (8988165), NOTCH1 (16025100).

**Limitations:** HPO/ClinVar are phenotype- and syndrome-oriented and over-represent Mendelian/syndromic disease; they do not establish population-attributable risk. NOTCH1 is mapped to aortic valve stenosis (Q23.0) although the primary phenotype is bicuspid aortic valve/calcification, an explicit mapping caveat.

---

### 3.6 Atualização após a revisão científica (PM10, CO, umidade e eixo PM2,5–AHR–Wnt)

A revisão do protocolo acrescentou três variáveis e fortaleceu o eixo principal:

- **PM10 → ASD:** OR 1,04 por 10 µg/m³ (1,00–1,09; meta-análise, PMID 32278917), associação modesta e heterogênea.
- **CO → VSD:** associado a defeitos septais em estudo de base populacional (PMID 21329916); **CO → TOF:** OR 1,21 (1,04–1,41; PMID 32278917).
- **Temperatura no Brasil:** estudo nacional com >11 milhões de nascimentos encontrou OR 1,08 (1,01–1,17) para defeitos do sistema circulatório no primeiro trimestre, ajustado por PM2,5 e umidade (PMID 39105774). Isso reforça a temperatura como **eixo secundário**, não como mecanismo estabelecido.
- **PM2,5 → AHR → Wnt/β-catenina:** em zebrafish, o extrato orgânico de PM2,5 ativa AHR, reprime alvos de Wnt/β-catenina e causa malformações cardíacas; antagonista de AHR e agonista de β-catenina resgatam o fenótipo (PMID 27216425). Esse é o elo mecanístico mais específico disponível para PM2,5.
- **PM2,5 → mitocôndria:** disfunção mitocondrial via AHR/cyp1a1, com apoptose e defeitos cardíacos (PMID 36841371).
- **Wnt → diferenciação de cardiomiócitos:** organoides cardíacos humanos dependem de modulação bifásica de Wnt (PMID 33558697).

**Umidade:** não foi identificada evidência direta de associação com CHD na busca estruturada. Ela permanece como variável contextual/confundidora no modelo local (OR 0,82; IC 0,63–1,07), sem aresta causal no grafo.

## 4. Conceptual, biological, epidemiological and computational incompatibilities found

| # | Incompatibility | Resolution adopted |
|---|---|---|
| 1 | CID-10 and HPO are not isomorphic (HLHS has no dedicated HPO term) | Mapped HLHS to HP:0004383 (hypoplastic left ventricle) with OMIM 241550 and an explicit note |
| 2 | `CODANOMAL` concatenates multiple 4-character ICD codes | Parsed in blocks of four; core Q20–Q26 retained, Q27–Q28 kept separate |
| 3 | SINASC records 52 core CHD (Q20–Q26) plus 8 Q27–Q28 cases in 98,598 births | Reported as **under-ascertainment**, not prevalence; not used to estimate risk |
| 4 | SIH AIHs are not individuals and 55% occur outside the municipality | Reported as admissions, never incidence; residence and admission municipality separated |
| 5 | Birth month ≠ exposure month | Exposure assigned to an estimated gestational window (weeks 3–8 post-conception) |
| 6 | Area-level climate ≠ personal exposure | All local analyses labelled ecological-exposure designs |
| 7 | Bibliometric volume ≠ evidence strength | Pair matrix used only for feasibility; grades from manual curation |
| 8 | Reviews are not primary evidence | Graded “indirect” with design `narrative_review` |
| 9 | CTD/DisGeNET/OMIM not programmatically accessible | Structured layer restricted to HPO, ClinVar, NCBI Gene, Reactome, Enrichr |
| 10 | SciELO search interface and CAPES Portal blocked automated access | SciELO metadata via Crossref and CAPES thesis catalogue were used; Portuguese-language coverage remains partial |

---

## 5. Decision on the first graph version

**Proceed to graph construction, with a restricted evidence core.**

Included:
- **17 exposures** as nodes (the original 14 plus PM10, CO and relative humidity); only those with verified evidence receive edges. Humidity remains contextual and has no causal edge.
- **14 phenotypes + `CHD:ALL`**.
- **16 mechanisms**, **11 developmental processes**, **47-gene panel + 814 HPO genes**.
- **54 unique manually curated relations** from **55 evidence rows** across 34 anchor studies (33 PubMed-indexed + 1 CAPES thesis), every quote verified against PubMed or the archived thesis abstract.
- Structured gene–phenotype, gene–pathway and variant edges.
- **Explicit gap layer**: SO2, cold, retinoic acid and dioxins/PCBs had no retained exposure→CHD edge (retinoic acid and dioxins have mechanism-level experimental evidence only).

Excluded from the observed core:
- PM2.5 → VSD as an “established association” (kept, but grade B with a non-significance penalty).
- Pesticides/solvents → CHD as phenotype-specific claims (kept only as aggregate indirect edges).
- Any exposure → gene or exposure → individual-case link (not supported by the data).

**Is Phase A apt to advance?** Yes. The graph is viable as a **provenance and gap-mapping instrument**. It is not viable as a causal model, and the local data are not viable as an aetiological test.
