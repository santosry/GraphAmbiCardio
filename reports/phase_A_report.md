# Phase A — Feasibility report (executive summary)

Date: 2026-10-31. Full report: `docs/01_SCIENTIFIC_VIABILITY.md`. Matrices: `reports/feasibility_*.csv`.

## What was searched

| Domain | PubMed | Europe PMC |
|---|---:|---:|
| A1 exposure → CHD | 1,512 | 1,599 |
| A2 exposure → mechanism | 8,520 | 171 |
| A3 mechanism → cardiogenesis | 6,736 | 39 |
| A4 cardiogenesis → phenotype | 7,681 | 593 |
| A5 gene → phenotype | 992 | 2,387 |

196 exposure × phenotype pairs: **546 total hits / 513 retrieved**. 73 pairs (37%) had no direct literature; only 2 were high-volume.

## Classification of connections

| Connection | Verdict | Basis |
|---|---|---|
| Exposure → CHD | Viable but phenotype-specific | direct human evidence for heat/aspects of air pollution/valproate/smoking/alcohol (d-TGA)/occupational metals; PM2.5→VSD non-significant; pesticides/solvents review-level only |
| Exposure → mechanism | Viable for a subset | PM2.5→inflammation (human cohort), heat→neural crest (chick/zebrafish), VPA→HDAC (zebrafish), dioxin→AHR (human ESC), alcohol→RA-sensitive cardiogenesis (zebrafish) |
| Mechanism → cardiogenesis | Viable, experimental | oxidative stress→neural crest, HDAC→AV cushion, AHR→differentiation/looping, RA→OFT/looping |
| Cardiogenesis → phenotype | Indirect only | human embryology timing + reviews of OFT/AV cushion/neural crest |
| Gene → phenotype | Strong/structured | HPO 2,803 annotations/814 genes; ClinVar 945 variants; classic NKX2-5/GATA4/TBX5/NOTCH1 papers |

## Decision

Proceed to graph construction with a **restricted observed core**:

- 14 exposures, 14 phenotypes + `CHD:ALL`, 16 mechanisms, 11 processes;
- 46 manually curated relations from 29 anchor studies (quotes machine-verified);
- structured layers: HPO, ClinVar, Reactome;
- explicit gap layer for exposures/mechanisms/processes without retained edges.

Not admitted as established: PM2.5→VSD, pesticides→CHD, solvents→CHD, any exposure→gene or exposure→case link.

## Principal incompatibilities resolved

1. HLHS lacks a dedicated HPO term → mapped to HP:0004383 with OMIM 241550 note.
2. `CODANOMAL` concatenates codes → parsed in 4-character blocks.
3. SINASC under-ascertainment (59/98,598) → reported as reported-count, not prevalence.
4. SIH AIH ≠ individuals; 55% outside municipality → admissions only, referral flow reported.
5. Birth month ≠ exposure month → gestational-window estimation.
6. Area-level climate ≠ personal exposure → ecological design label.
7. Bibliometric volume ≠ evidence strength → manual curation for grades.
8. CTD/DisGeNET/OMIM inaccessible; SciELO search interface blocked (Crossref used) → documented.

**Apt to advance:** yes, as a provenance and gap-mapping instrument; not as a causal model or as a local aetiological study.
