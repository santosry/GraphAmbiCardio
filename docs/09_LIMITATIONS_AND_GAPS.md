# 09 — Limitations, biases and knowledge gaps

This document lists limitations that materially affect interpretation. They are not boilerplate.

---

## 1. Literature and evidence synthesis

1. **Rapid scoping, not a full systematic review.** 1,095 unique records were triaged automatically; 29 anchor studies were read manually. There was no dual independent screening of all records, no full-text review and no formal risk-of-bias instrument (ROBINS-I, SYRCLE, Cochrane) applied study-by-study. The evidence grades reflect directness and design, not a full risk-of-bias assessment.
2. **Top-N retrieval.** Domain searches retrieved the top 100 by relevance; pair searches retrieved the top 15. Counts are total hits, but screening was not exhaustive.
3. **Language and regional bias.** PubMed/Europe PMC over-represent English-language, high-income-country research. SciELO, BVS/LILACS and Portal CAPES returned HTTP 403 or required interactive access; Latin American evidence is missing.
4. **Query contamination.** Automated triage over-detects “human” studies (any mention of children/patients) and mechanism terms. The pair matrix is therefore a **feasibility screen**, not an evidence map.
5. **Publication and reporting bias.** Positive associations are more likely published; phenotype-specific subgroup findings are often reported without correction for multiple comparisons (e.g. alcohol → d-TGA in a meta-analysis with a null overall effect).
6. **Healthcare-access confounding in human studies.** Associations may reflect diagnosis/access rather than aetiology, especially for mild phenotypes (small VSD, ASD).

---

## 2. Molecular and developmental evidence

1. **Species and dose translation.** Most mechanism edges come from zebrafish, chick or mouse experiments, often at doses far above human environmental exposure. The graph records species but cannot quantify dose equivalence.
2. **Human relevance of cell models.** Dioxin/AHR evidence comes from human ESC differentiation; this is human-relevant but still in vitro.
3. **Reviews as indirect evidence.** Process→phenotype edges rest on narrative reviews and descriptive embryology. The embryology is well established, but the edge grade (D) correctly signals that no study tested that exact exposure→phenotype chain.
4. **Gene–phenotype databases are Mendelian/syndromic.** HPO (2,803 annotations, 814 genes) and ClinVar over-represent rare Mendelian disease. They do not estimate population-attributable risk and can overstate the role of syndromic genes in non-syndromic CHD.
5. **Pathway inference is heuristic.** The Reactome→process map is a keyword rule (8 edges), explicitly labelled `inferred`.
6. **No expression data.** GEO was not used because no dataset met the stage/species/tissue criteria; adult expression was not accepted as cardiogenesis evidence.
7. **Missing databases.** CTD (captcha), DisGeNET (API key) and OMIM (licence) were not used. Chemical–gene–disease edges are therefore under-represented.

---

## 3. Local epidemiological data

1. **SINASC under-ascertainment is severe.** 59 CHD cases in 98,598 births (0.6 per 1,000) versus an expected 6–9 per 1,000. Diagnoses made after the birth record are not captured. The SINASC count is a **reported** count, not prevalence.
2. **Missing years.** 2023 and 2024 microdata were absent from the DATASUS FTP; 2025 is preliminary. No imputation was performed, so the time series is incomplete and not directly comparable across years.
3. **Unspecified codes.** Q249/Q248/Q219 dominate; phenotype-specific analyses are underpowered.
4. **SIH is not incidence and not people.** AIH counts depend on access, referral and coding; 55% of admissions occur outside the municipality; there is no patient identifier, so readmissions cannot be measured.
5. **Adult admissions.** 138/549 admissions are in adults (≥18 years), reflecting adult CHD, not incident childhood disease.
6. **Costs are nominal.** No deflation or purchasing-power adjustment was applied.
7. **Denominators.** Birth-level models use SINASC live births; SIH indicators lack age-specific population denominators.
8. **Residence at birth ≠ residence at conception.** Migration during pregnancy is not captured.
9. **Small numbers.** 56–59 events make all models imprecise; the season-adjusted estimate is fragile under leave-one-year-out.

---

## 4. Environmental exposure

1. **No local PM2.5 series.** Air-pollution edges are literature-only; no local air-pollution analysis was possible. No proxy was fabricated.
2. **Reanalysis ≠ station.** ERA5-Land is a ~9 km grid cell; it does not represent street-level or indoor exposure, urban heat islands, or the full municipality.
3. **Ecological exposure.** All births in the same window receive the same exposure value; this is not personal exposure and cannot support individual risk statements.
4. **Gestational age misclassification.** Conception dates are estimated from gestational age at birth (and from category midpoints when missing), producing window misclassification.
5. **No exposure mixture analysis.** Real exposures are correlated (heat, ozone, PM2.5, season); single-exposure models cannot separate them.
6. **No air-quality covariates.** The local models cannot adjust for pollution or humidity interactions.

---

## 5. Graph and computational limitations

1. **Node coverage is uneven.** Genes (814 HPO + 170 with metadata) dominate the graph; mechanisms (16) and processes (11) are coarse.
2. **Centrality is structural.** VSD/ASD/PDA have the highest degree because HPO annotates many genes to them, not because they are “more important”.
3. **Confidence is not probability.** The formula is a transparent heuristic; grades are not calibrated against external truth.
4. **Threshold dependence.** Direct links fall from 13 to 8 between confidence 0.40 and 0.85.
5. **Hypothesis layer is small (7 edges) and excluded from all path analyses.**
6. **No Neo4j.** The graph is small enough for NetworkX/GraphML; a database would add complexity without a current query need.
7. **Version drift.** HPO/ClinVar/Reactome change continuously; the retrieval date is stored, but exact release hashes are not pinned for ClinVar/Reactome.

---

## 6. Explicit gaps identified by the graph (20)

**Exposures with no retained exposure→phenotype edge:** SO2, cold, retinoic acid (vitamin A derivatives), dioxins/PCBs. (Dioxins and retinoic acid have experimental mechanism-level evidence but no verified human CHD association in this extraction.)

**Mechanisms with no curated mechanism→process edge:** inflammation, epigenetic alteration, mitochondrial dysfunction, altered cell signalling, altered gene expression, apoptosis, proliferation, heat-shock response, Wnt/β-catenin, hypoxia, endothelial/vascular perturbation. These are plausible and heavily studied, but the retrieved evidence did not allow a specific, verifiable edge at this stage.

**Processes with no curated process→phenotype edge:** heart tube formation, looping, cardiomyocyte differentiation, coronary/vascular development, conduction system development. (Looping and cardiomyocyte differentiation do have mechanism-level incoming edges.)

**Phenotypes with no exposure→phenotype path:** Ebstein anomaly, pulmonary stenosis, TAPVC, truncus arteriosus. This reflects the literature, not absence of environmental aetiology.

**These gaps are results.** They define the next search and curation priorities.

---

## 7. What would change the conclusions

- A local congenital anomaly registry with active postnatal follow-up (would fix under-ascertainment).
- Local PM2.5 monitoring or a validated satellite/land-use model (would allow air-pollution analysis).
- Individual-level exposure and residential history (would move beyond ecological design).
- Full-text dual screening with risk-of-bias tools (would strengthen the evidence grades).
- Access to CTD/DisGeNET/OMIM (would enrich the chemical–gene–disease layer).
- Stage-specific embryonic transcriptomics (would allow expression evidence for cardiogenesis).
