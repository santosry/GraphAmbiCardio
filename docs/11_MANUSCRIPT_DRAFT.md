# 11 — Manuscript draft (v0.1.0)

**Title:** A provenance-first knowledge graph linking environmental exposures, molecular mechanisms, cardiogenesis and congenital heart defects: a computational study in Campos dos Goytacazes, Brazil (2010–2025)

**Running title:** Knowledge graph of environmental exposures and congenital heart defects

**Authors:** [to be completed]
**Affiliations:** [to be completed]
**Corresponding author:** [to be completed]
**Word count (draft):** ~3,800 (excluding references)

---

## Abstract

**Background.** Congenital heart defects (CHD) are multifactorial, but evidence on environmental exposures, molecular mechanisms, cardiac developmental processes and phenotypes is fragmented across epidemiology, toxicology, developmental biology and genetics. Simple association networks obscure provenance and overstate mechanisms that were never tested.

**Objective.** To build and analyse a provenance-first knowledge graph connecting environmental exposures, molecular mechanisms, cardiogenesis and CHD phenotypes, and to integrate local epidemiological and environmental data from Campos dos Goytacazes (RJ, Brazil) as ecological context.

**Methods.** We performed a rapid scoping review (PubMed/MEDLINE and Europe PMC; retrieval 2026-10-31) across five pre-registered evidence domains and 196 exposure × phenotype queries. We curated 29 anchor studies (46 edges) with verbatim quotes verified programmatically against PubMed, and integrated structured annotations from HPO, ClinVar, NCBI Gene and Reactome. Local data comprised SINASC live births (2010–2022 and 2025), SIH/SUS hospital admissions (2010–2025) and ERA5-Land daily climate (2010–2025). Exposure was assigned to an estimated cardiac organogenesis window (weeks 3–8 post-conception). Every relation carries evidence type, species, design, window, reference, confidence and limitations; observed, structured, inferred, hypothesis and ecological layers were kept separate.

**Results.** Searches returned 1,512 / 8,520 / 6,736 / 7,681 / 992 PubMed records for the five domains; 1,450 records were retrieved and screened (1,095 unique). Of 196 exposure × phenotype pairs, 73 (37%) had no direct literature and only 2 were high-volume. The graph contains 2,234 nodes, 4,100 relations and 4,596 evidence rows; 23 exposure→phenotype paths were found (13 direct, 10 via mechanism/process chains), and 20 explicit gaps were identified. Direct human evidence was concentrated in a few exposure–phenotype pairs (heat→ASD; valproate→CHD; smoking→TOF; alcohol→d-TGA; NO2→coarctation; O3→ASD), whereas most mechanistic links were experimental. Locally, SINASC reported only 59 CHD cases among 98,598 births (5.98 per 10,000), indicating severe under-ascertainment; SIH recorded 549 admissions (55% outside the municipality) and 33 deaths. In exploratory models (56–59 events), gestational-window mean Tmax was associated with reported CHD (OR 1.30 per SD, 95% CI 1.00–1.69; season-adjusted OR 1.65, 1.13–2.42), but the monthly count model was null (RR 1.22, 0.94–1.60) and leave-one-year-out estimates varied (OR 1.47–1.66).

**Conclusions.** A provenance-first graph makes explicit that only a minority of exposure→CHD links have direct human support, that mechanistic chains are largely experimental, and that several plausible exposures and mechanisms remain unconnected. Local routine data cannot support aetiological inference in this municipality, but they quantify an important surveillance gap. The graph is proposed as a reproducible instrument for evidence appraisal and gap prioritisation, not as a causal model.

**Keywords:** congenital heart defects; environmental exposure; knowledge graph; cardiogenesis; evidence grading; health information systems; Brazil.

---

## 1. Introduction

Congenital heart defects are the most common major congenital anomalies and a leading cause of infant morbidity and mortality. Their aetiology is multifactorial: chromosomal and Mendelian causes explain a minority of cases, while environmental, behavioural, metabolic and developmental factors contribute with effect sizes that are usually modest and heterogeneous across phenotypes.

The literature is fragmented in a way that is easy to overlook. Epidemiological studies estimate associations between exposures and CHD categories but rarely measure mechanisms. Animal and cell studies identify molecular pathways but use doses and developmental windows that are difficult to translate. Genetics identifies genes and variants but usually in syndromic or Mendelian subsets. Reviews synthesize these strands, but synthesis often creates implicit causal chains (“exposure → oxidative stress → neural crest → outflow tract defect”) that were never tested as a whole.

Knowledge graphs are attractive precisely because they can represent these heterogeneous relations explicitly. However, a graph is only as defensible as its provenance model. Generic “associated with” edges, mixed evidence layers, and centrality-based interpretations can produce a visually impressive but scientifically misleading object.

We therefore developed GraphAmbiCardio with three commitments: (i) every relation is typed and sourced; (ii) every evidence item is retained separately with species, design, exposure window, effect direction and limitations; (iii) observed, structured, inferred, hypothesis and ecological layers are never merged. We applied the approach to Campos dos Goytacazes, a municipality in the Norte Fluminense region of Brazil with agricultural activity, biomass burning and no local air-quality monitoring, and we integrated SINASC, SIH/SUS and ERA5-Land data for 2010–2025.

Our aims were to determine which exposure→CHD links have direct human support, which mechanistic chains are experimental, where evidence converges, and which gaps remain — and to quantify what local routine data can and cannot add.

---

## 2. Methods

### 2.1 Study design and reporting

Rapid scoping review with targeted manual curation, structured-database integration, and ecological analysis of local secondary data. Reporting follows PRISMA-ScR for the scoping component; search reporting follows PRISMA-S principles. The protocol was frozen before graph construction (docs/00_PROTOCOL.md); deviations are logged (docs/10_PHASE_LOG.md).

### 2.2 Literature searches

Five pre-registered domains were searched on 2026-10-31 in PubMed/MEDLINE (E-utilities) and Europe PMC:
A1 exposure→CHD; A2 exposure→mechanism; A3 mechanism→cardiogenesis; A4 cardiogenesis→phenotype; A5 gene→phenotype.
In addition, 196 exposure × phenotype pairs (14 × 14) were queried with a prenatal/developmental context block. Biological literature was not restricted to 2010–2025; the period applies only to local data.

Exact strings, translations, counts and retrieved records are stored in `literature/searches/*.json` and documented in docs/02_SEARCH_STRATEGY.md.

### 2.3 Selection and curation

Records were deduplicated by PMID, DOI and normalised title. Automated triage flagged species, design, exposure-window vocabulary, mechanisms and phenotypes. Twenty-nine anchor studies were read manually and 46 edges encoded with verbatim quotes; a build-time verifier aborts if a quote is not found in the PubMed abstract. No dual independent screening of all records was performed (see Limitations).

### 2.4 Structured databases

HPO gene-to-phenotype annotations (2,803; 814 genes), ClinVar pathogenic/likely pathogenic variants (945 after excluding large CNVs), NCBI Gene identifiers (170), Reactome per-gene over-representation (FDR < 0.05; 649 developmental/cardiac gene–pathway edges) and Enrichr GO Biological Process 2023 (descriptive only). CTD, DisGeNET and OMIM were not programmatically accessible.

### 2.5 Ontology and evidence model

Node types: Exposure, Mechanism, Gene, Pathway, Process, Phenotype, Variant, Indicator, Population, Period. Relation types include EXPOSURE_ASSOCIATED_WITH_PHENOTYPE, EXPOSURE_MODULATES_MECHANISM, MECHANISM_INTERFERES_WITH_PROCESS, GENE_ASSOCIATED_WITH_PHENOTYPE, GENE_PARTICIPATES_IN_PATHWAY, PATHWAY_REGULATES_PROCESS, VARIANT_IN_GENE, ALTERATION_ASSOCIATED_WITH_PHENOTYPE, INDICATOR_DESCRIBES_PHENOTYPE, ECOLOGICAL_CONTEXT_FOR and HYPOTHESIS_LINK. Each evidence row records layer, evidence type, study design, species, population/model, exposure window, effect direction, quote, reference, retrieval date and limitations.

Edge confidence uses a pre-registered weighted formula (0.7 × evidence-type weight + 0.3 × design weight, capped at 0.9, plus replication and species-concordance bonuses, minus single-study, non-significance and contradiction penalties). Grades: A ≥ 0.88, B ≥ 0.72, C ≥ 0.55, D ≥ 0.40, E < 0.40.

### 2.6 Local data

SINASC: all live births to resident mothers (IBGE 330100), 2010–2022 and 2025. Case definition: any CID-10 Q20–Q28 code in `CODANOMAL`, parsed in blocks of four characters (multiple codes preserved). 2023–2024 were absent from the DATASUS FTP; 2025 is preliminary; no imputation.

SIH/SUS: 192 monthly files (2010–2025), residents with primary diagnosis Q20–Q28; 12 additional admissions with CHD only as a secondary diagnosis were evaluated separately. AIHs, not individuals; residence and admission municipality kept separate.

Environment: ERA5-Land daily series via Open-Meteo for the municipality grid cell. No local PM2.5 series exists; no proxy was fabricated.

Exposure window: conception estimated as birth date minus gestational age; cardiac organogenesis defined as days 21–56 post-conception; daily climate averaged over the window. Area-level exposure assigned to individual pregnancy windows — an ecological-exposure design.

### 2.7 Statistical analysis

Descriptive indicators for both systems; completeness and under-ascertainment assessment. Birth-level logistic regression of CHD on exposure z-score adjusted for year, maternal age and sex; season-adjusted sensitivity adding quarter of conception; monthly Poisson/negative-binomial counts by conception month with log(live births) offset; leave-one-year-out sensitivity.

### 2.8 Network analysis

Degree, betweenness and Louvain communities (variants excluded from centrality); all simple exposure→phenotype paths (cut-off 5 nodes) with minimum edge confidence; gene convergence per phenotype and gene-set overlap; explicit gap analysis; confidence-threshold sensitivity (0.40–0.85). Hypothesis and ecological layers were excluded from path analysis.

### 2.9 Validation

Integrity checks (unique IDs, endpoints, no self-loops, valid vocabulary), quote re-verification (25%), PMID resolution and data-range checks. A two-reviewer audit sheet was generated but not completed.

---

## 3. Results

### 3.1 Evidence base

PubMed returned 1,512 records for exposure→CHD, 8,520 for exposure→mechanism, 6,736 for mechanism→cardiogenesis, 7,681 for cardiogenesis→phenotype and 992 for gene→phenotype. Europe PMC returned 1,599 / 171 / 39 / 593 / 2,387. Across the retrieved top-N records, 1,450 records yielded 1,095 unique records (1,003 with abstracts).

The 196-pair matrix showed a sparse evidence landscape: 73 pairs (37%) had no direct literature under the context filter, 66 were sparse (1–2 records), 36 limited (3–7), 19 moderate (8–19) and only 2 high-volume (alcohol→VSD, 32; retinoic acid→TGA, 20). Automated triage over-represented “human” records because it flagged any mention of children or patients, reinforcing that volume is not quality.

### 3.2 Graph structure

The graph contains 2,234 nodes, 4,100 relations and 4,596 evidence rows. Relations by layer: observed 46, structured 4,040, inferred 4, hypothesis 7, ecological 3. Structured relations include 2,314 gene–phenotype, 649 gene–pathway, 945 variant–gene and 150 variant–phenotype edges.

### 3.3 Exposure→phenotype paths

Twenty-three exposure→phenotype paths were identified in the conceptual core: 13 direct and 10 through mechanism/process chains. Direct human evidence was concentrated in:
- heat → ASD (PR 1.37, 1.10–1.70; PMID 27494594);
- valproate → CHD (RR 2.53, 2.16–2.96; PMID 41161707);
- smoking → TOF (RR 9.84, 2.49–38.84) and → overall CHD (RR 2.65, 1.76–3.98; PMID 35916623);
- alcohol → d-TGA (OR 1.64, 1.17–2.30; PMID 26110619), with a null overall association;
- NO2 → coarctation (OR 1.14, 1.02–1.26) and O3 → ASD (OR 1.09 per 10 ppb, 1.02–1.17; PMID 32278917);
- PM2.5 → VSD (OR 1.34, 0.98–1.83, non-significant; PMID 26705853).

Mechanistic chains included heat→neural crest→outflow tract→TOF/TGA/DORV; PM2.5→oxidative stress→neural crest→TOF/TGA; valproate→HDAC→AV cushion→VSD/AVSD; and alcohol→retinoic acid→outflow tract→TOF/TGA/DORV. All mechanistic chains had a minimum edge confidence of 0.44 (grade D), reflecting review/indirect evidence at the process→phenotype step.

### 3.4 Gene convergence and communities

The phenotypes with most annotated genes were VSD (526), ASD (489), PDA (408), TOF (193) and coarctation (159). ASD and VSD shared 307 genes (Jaccard 0.43), consistent with overlapping developmental programmes and pleiotropy; this is annotation overlap, not evidence of a shared environmental mechanism. The graph formed eight communities, the largest (273 nodes) mixing phenotypes, genes and pathways.

Centrality was dominated by phenotypes because HPO annotates many genes to VSD/ASD/PDA; betweenness was 0.35 for VSD and 0.32 for ASD. We do not interpret this as biological importance.

### 3.5 Local epidemiology

SINASC recorded 98,598 live births and only 59 CHD cases (5.98 per 10,000; 0.6 per 1,000), roughly one order of magnitude below expected birth prevalence. Unspecified codes dominated (Q249, 20; Q248, 12; Q219, 2). The most plausible interpretation is severe under-ascertainment. CHD records had lower mean birth weight (2,844 vs 3,165 g) and higher preterm proportion (19.2% vs 12.1%), but with 59 cases these are descriptive.

SIH recorded 549 admissions with primary CHD diagnosis, 33 deaths (6.0%), mean length of stay 12.0 days and BRL 4.16 million in nominal reimbursement. Nearly half of admissions (245/549) occurred in Rio de Janeiro and only 247 in Campos; 138 admissions were in adults. This is a referral pattern, not incidence.

### 3.6 Local environmental analysis

The organogenesis window was estimable for 90,008 births (91.3%). Mean Tmax during the window was 29.9 °C in CHD records vs 29.0 °C in non-CHD records. In birth-level logistic regression, the OR was 1.30 per SD (1.00–1.69) and 1.65 (1.13–2.42) after quarter-of-conception adjustment; leave-one-year-out ORs ranged 1.47–1.66 with p from 0.010 to 0.056. The monthly count model was null (RR 1.22, 0.94–1.60; RR 1.38 per IQR). Given the ecological exposure, small number of events, incomplete ascertainment and model disagreement, this is reported as hypothesis-generating only.

### 3.7 Gaps

Twenty gaps were identified. SO2, cold, retinoic acid and dioxins/PCBs had no retained exposure→CHD edge. Inflammation, epigenetic alteration, mitochondrial dysfunction, signalling, gene expression, apoptosis, proliferation, heat-shock, Wnt, hypoxia and endothelial mechanisms had no curated mechanism→process edge. Heart tube, looping, cardiomyocyte differentiation, coronary development and conduction had no curated process→phenotype edge. Ebstein, pulmonary stenosis, TAPVC and truncus had no exposure→phenotype path.

---

## 4. Discussion

### 4.1 Principal findings

Three findings stand out. First, direct human evidence is concentrated in a small number of exposure–phenotype pairs; most of the 196 pairs are empty or sparse. Second, the mechanistic architecture of the graph is experimental: exposure→mechanism and mechanism→process edges come predominantly from animal or cell studies, while process→phenotype edges are indirect. Third, the local data quantify a surveillance gap rather than an aetiological signal: SINASC captures a small fraction of expected CHD, and SIH reflects referral and access patterns.

### 4.2 Comparison with the literature

The direct estimates we retained are consistent with recent syntheses: air pollution and specific CHD subtypes (PM2.5/PM10, NO2, O3, CO) show modest, subtype-specific associations; valproate and smoking show larger relative risks; alcohol shows a phenotype-specific signal for d-TGA against a null overall estimate. Heat and ASD have been reported in large cohorts, but the evidence base is smaller and susceptible to exposure misclassification.

The mechanistic chains we encoded are biologically coherent but not human-validated as chains. Heat activates TRPV1/TRPV4 in neural crest cells; oxidative stress depletes cardiac neural crest and causes outflow tract defects; HDAC activity is required for Wnt/β-catenin-dependent valve formation; dioxin impairs human ESC cardiac differentiation via AHR. Each step is supported, but the composition is a hypothesis, not a demonstrated pathway for any specific environmental exposure at human doses.

### 4.3 Why the graph is useful

The graph’s value is not a list of “top” nodes. It is the ability to see where evidence is missing. For example, inflammation is a well-studied mechanism of PM2.5, yet no curated inflammation→cardiogenesis edge survived; retinoic acid has strong developmental biology but no verified human CHD association; cold has five records across all phenotypes. These are actionable gaps, not failures of the search.

The separation of layers also prevents a common error: using centrality or gene overlap as evidence of environmental causation. VSD has the highest degree because HPO annotates many genes to it, not because it is more environmentally determined.

### 4.4 Local implications

For Campos dos Goytacazes, the practical implication is that routine SINASC/SIH data cannot support aetiological claims. A congenital anomaly registry with postnatal follow-up, local air-quality monitoring and individual-level exposure assessment would be required. Until then, ecological analyses should be reported as exploratory and should not drive policy claims about heat or pollution.

### 4.5 Implications for evidence synthesis

Provenance-first graphs could complement systematic reviews: they make indirect chains explicit, preserve contradictory and null findings, and allow sensitivity analysis by evidence threshold. They also expose the cost of missing databases: without CTD/DisGeNET/OMIM, the chemical–gene layer is incomplete.

---

## 5. Limitations

This is a rapid scoping review, not a full systematic review: 1,095 unique records were triaged automatically, 29 anchor studies were read manually, and no dual independent screening or formal risk-of-bias assessment was performed. Searches retrieved top-N records; SciELO, BVS and CAPES were inaccessible (HTTP 403), so Portuguese-language literature is under-represented. CTD, DisGeNET and OMIM were unavailable. Most mechanistic edges rely on animal/cell models at doses not equivalent to human exposure. HPO and ClinVar are Mendelian/syndromic and over-represent rare disease. Process→phenotype edges are indirect. Local SINASC data are severely under-ascertained; 2023–2024 are missing; 2025 is preliminary. SIH AIHs are not individuals. Exposure is area-level reanalysis, not personal exposure; conception dates are estimated. The local heat model has 56–59 events and is fragile. The graph’s confidence score is a heuristic, not a probability. Two-reviewer audit is pending.

---

## 6. Conclusion

A provenance-first knowledge graph shows that the evidence linking environmental exposures to congenital heart defects is narrower and more phenotype-specific than the volume of publications suggests, and that most mechanistic chains remain experimental. In Campos dos Goytacazes, routine data reveal a major surveillance gap rather than an aetiological signal. The graph, code and evidence tables are released to support transparent re-analysis, explicit gap prioritisation and future linkage to better local data.

---

## Declarations

**Data availability.** All code, search records, curated evidence, processed data and graph exports are in the repository. Raw DATASUS files are not redistributed; download scripts are provided. No individual-level identifiers are included.

**Ethics.** Secondary analysis of public aggregate data; no re-identification attempted.

**Funding.** [to be completed]

**Conflicts of interest.** None declared.

**Author contributions.** [to be completed]

---

## References

### Anchor studies (manual curation)

1. Basson CT, et al. Mutations in human TBX5 cause limb and cardiac malformation in Holt-Oram syndrome. *Nat Genet.* 1997. PMID 8988165. doi:10.1038/ng0197-30.
2. Schott JJ, et al. Congenital heart disease caused by mutations in the transcription factor NKX2-5. *Science.* 1998. PMID 9651244. doi:10.1126/science.281.5373.108.
3. Benson DW, et al. Mutations in the cardiac transcription factor NKX2.5 affect diverse cardiac developmental pathways. *J Clin Invest.* 1999. PMID 10587520. doi:10.1172/JCI8154.
4. Garg V, et al. GATA4 mutations cause human congenital heart defects and reveal an interaction with TBX5. *Nature.* 2003. PMID 12845333. doi:10.1038/nature01827.
5. Garg V, et al. Mutations in NOTCH1 cause aortic valve disease. *Nature.* 2005. PMID 16025100. doi:10.1038/nature03940.
6. Beis D, et al. Genetic and cellular analyses of zebrafish atrioventricular cushion and valve development. *Development.* 2005. PMID 16107477. doi:10.1242/dev.01970.
7. Morgan SC, et al. Oxidative stress during diabetic pregnancy disrupts cardiac neural crest migration and causes outflow tract defects. *Birth Defects Res A Clin Mol Teratol.* 2008. PMID 18435457. doi:10.1002/bdra.20457.
8. Dadvand P, et al. Ambient air pollution and congenital heart disease: a register-based study. *Environ Res.* 2011. PMID 21329916. doi:10.1016/j.envres.2011.01.022.
9. Kim YS, et al. Histone deacetylase is required for the activation of Wnt/β-catenin signaling crucial for heart valve formation in zebrafish embryos. *Biochem Biophys Res Commun.* 2012. PMID 22634317. doi:10.1016/j.bbrc.2012.05.098.
10. Sarmah S, et al. Complex cardiac defects after ethanol exposure during discrete cardiogenic events in zebrafish: prevention with folic acid. *Dev Dyn.* 2013. PMID 23832875. doi:10.1002/dvdy.24015.
11. Neeb Z, et al. Cardiac outflow tract anomalies. *Wiley Interdiscip Rev Dev Biol.* 2013. PMID 24014420. doi:10.1002/wdev.98.
12. Yang J, et al. Prenatal alcohol exposure and congenital heart defects: a meta-analysis. *PLoS One.* 2015. PMID 26110619. doi:10.1371/journal.pone.0130681.
13. Girguis MS, et al. Maternal exposure to traffic-related air pollution and birth defects in Massachusetts. *Environ Res.* 2016. PMID 26705853. doi:10.1016/j.envres.2015.12.010.
14. Auger N, et al. Risk of congenital heart defects after ambient heat exposure early in pregnancy. *Environ Health Perspect.* 2017. PMID 27494594. doi:10.1289/EHP171.
15. Hutson MR, et al. Temperature-activated ion channels in neural crest cells confer maternal fever-associated birth defects. *Sci Signal.* 2017. PMID 29018170. doi:10.1126/scisignal.aal4055.
16. Nicoll R, et al. Environmental contaminants and congenital heart defects: a re-evaluation of the evidence. *Int J Environ Res Public Health.* 2018. PMID 30257432. doi:10.3390/ijerph15102096.
17. Nakajima Y. Retinoic acid signaling in heart development. *Genesis.* 2019. PMID 31021052. doi:10.1002/dvg.23300.
18. Fu H, et al. Dioxin and AHR impairs mesoderm gene expression and cardiac differentiation in human embryonic stem cells. *Sci Total Environ.* 2019. PMID 30266049. doi:10.1016/j.scitotenv.2018.09.247.
19. Seelan RS, et al. MicroRNAs as epigenetic targets of cigarette smoke during embryonic development. *Microrna.* 2020. PMID 31556862. doi:10.2174/2211536608666190926114704.
20. Hu CY, et al. Maternal air pollution exposure and congenital heart defects in offspring: a systematic review and meta-analysis. *Chemosphere.* 2020. PMID 32278917. doi:10.1016/j.chemosphere.2020.126668.
21. Rajesh V, et al. Heart malformation is an early response to valproic acid in developing zebrafish. *Naunyn Schmiedebergs Arch Pharmacol.* 2020. PMID 32699959. doi:10.1007/s00210-020-01949-4.
22. Spinder N, et al. Maternal occupational exposure and congenital heart defects in offspring. *Scand J Work Environ Health.* 2020. PMID 33135766. doi:10.5271/sjweh.3912.
23. Yamagishi H. Cardiac neural crest. *Cold Spring Harb Perspect Biol.* 2021. PMID 32071091. doi:10.1101/cshperspect.a036715.
24. Singleman C, et al. PCB and TCDD derived embryonic cardiac defects result from a novel AhR pathway. *Aquat Toxicol.* 2021. PMID 33662880. doi:10.1016/j.aquatox.2021.105794.
25. Gogna P, et al. Ambient air pollution and inflammatory effects in a Canadian pregnancy cohort. *Environ Epidemiol.* 2021. PMID 34934889. doi:10.1097/EE9.0000000000000168.
26. Johnson NM, et al. Air pollution and children's health—a review of adverse effects associated with prenatal exposure from fine to ultrafine particulate matter. *Environ Health Prev Med.* 2021. PMID 34253165. doi:10.1186/s12199-021-00995-5.
27. Wang T, et al. Maternal pre-pregnancy/early-pregnancy smoking and risk of congenital heart diseases in offspring: a prospective cohort study in Central China. *J Glob Health.* 2022. PMID 35916623. doi:10.7189/jogh.12.11009.
28. Hikspoors JPJM, et al. Human cardiac development. *Adv Exp Med Biol.* 2024. PMID 38884703. doi:10.1007/978-3-031-44087-8_1.
29. Yang X, et al. Safety of valproic acid use in pregnant women: a systematic review and meta-analysis. *J Obstet Gynaecol Res.* 2025. PMID 41161707. doi:10.1111/jog.70121.

### Databases and data sources

30. Köhler S, et al. The Human Phenotype Ontology in 2021. *Nucleic Acids Res.* 2021;49:D1207–D1217. PMID 33264411.
31. Landrum MJ, et al. ClinVar: improving access to variant interpretations and supporting evidence. *Nucleic Acids Res.* 2018;46:D1062–D1067. PMID 29165669.
32. Gillespie M, et al. The Reactome pathway knowledgebase 2022. *Nucleic Acids Res.* 2022;50:D687–D692. PMID 34788843.
33. Muñoz-Sabater J, et al. ERA5-Land: a state-of-the-art global reanalysis dataset for land applications. *Earth Syst Sci Data.* 2021;13:4349–4383. doi:10.5194/essd-13-4349-2021.
34. Open-Meteo. Historical Weather API documentation. https://open-meteo.com/en/docs/historical-weather-api (accessed 2026-10-31).
35. Brasil. Ministério da Saúde. DATASUS. SINASC — Sistema de Informações sobre Nascidos Vivos; SIH/SUS — Sistema de Informações Hospitalares. https://datasus.saude.gov.br (accessed 2026-10-31).
36. Chen EY, et al. Enrichr: interactive and collaborative HTML5 gene list enrichment analysis tool. *BMC Bioinformatics.* 2013;14:128. PMID 23586463.

---

### Table/Figure legends (draft)

**Figure 1.** Curated conceptual core (exposures, mechanisms, processes, phenotypes); edge width proportional to confidence; inferred and hypothesis layers excluded.

**Figure 2.** Evidence density per phenotype (genes, curated exposures, developmental processes). Counts are structural, not quality.

**Figure 3.** Sensitivity of the core graph to the confidence threshold.

**Figure 4.** Local data: area-level heat exposure by CHD status and annual reported CHD cases in SINASC.

**Table 1.** Feasibility matrix summary (196 exposure × phenotype pairs).

**Table 2.** Curated anchor studies and evidence grades.

**Table 3.** Local epidemiological indicators (SINASC and SIH).

**Table 4.** Exploratory models of gestational-window heat exposure.
