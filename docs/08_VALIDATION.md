# 08: Validation report

Generated: 2026-11-01. Machine-readable: `reports/validation_results.json`; human-readable: `reports/validation_report.md`.

---

## 1. Levels of validation and results

| Level | Check | Result |
|---|---|---|
| Bibliographic | 104 curated evidence rows (87 unique relations; 54 manual, 49 AI-assisted reviewed and 1 CAPES) have a PMID or CAPES reference and a verbatim quote; 100% verified at build time; 25% of PubMed rows re-checked at validation; 100% of CAPES abstracts re-checked locally | **Passed** |
| Bibliographic | 33 anchor PMIDs resolvable via NCBI E-utilities; 1 CAPES thesis abstract archived locally | **Passed** (33/33 PMIDs; 1/1 CAPES) |
| Biological | Manual reading of every curated edge for developmental/molecular coherence; layers and caveats recorded | **Passed with documented caveats** |
| Data | Municipality, period, missingness, duplicates, range checks for SINASC, SIH and climate | **Passed** |
| Computational | Unique node IDs, unique evidence IDs, edge endpoints exist, no self-loops, valid relation vocabulary, confidence ∈ [0,1], grade ∈ {A–E} | **Passed** |
| Robustness | Confidence-threshold sensitivity (0.40–0.85); leave-one-year-out models | **Executed; results reported with instability** |
| Human curation | Manual reading of every anchor abstract and curated edge | **Completed by the study team** |

---

## 2. Automated checks

```
nodes: 2,238 | relations: 4,146 | evidence rows: 4,659
duplicate node IDs: 0
duplicate evidence IDs: 0
missing edge endpoints: 0
self-loops: 0
invalid relations: 0
curated quotes not found on re-check: 0
SINASC records outside 330100: 0
SINASC years outside 2010–2025: 0
SIH records outside 330100: 0
climate missing Tmax: 0
```

---

## 3. Biological validation (what was checked)

For every curated edge the reviewer checked:

1. Does the source actually study the stated exposure/mechanism/process/phenotype?
2. Is the species and study design correctly recorded?
3. Is the direction of effect stated accurately (including non-significance)?
4. Is the exposure window relevant to cardiac organogenesis (weeks 3–8)?
5. Is the relation being used at the same level as the evidence (e.g. animal experiment not presented as human association)?

Specific corrections made during validation:

- **Alcohol → VSD** was removed: the retrieved records were dominated by phantom/imaging papers; the meta-analysis (PMID 26110619) reported a null association for VSD. Only the d-TGA association was retained.
- **Pesticides/solvents** were downgraded to **indirect** aggregate edges because no phenotype-specific human estimate was verified.
- **PM2.5 → VSD** was kept but penalised for non-significance (grade B).
- **HEAT → TOF** is a *hypothesis path* (through neural crest/OFT), not a direct human association; it appears only in the path table as a mechanism chain, not as an observed edge.
- **NOTCH1 → aortic stenosis** carries a mapping caveat (bicuspid aortic valve/calcification vs Q23.0).

---

## 4. Data validation details

- SINASC: 98,598 births; all `CODMUNRES` = 330100; years 2010–2022 + 2025; 2023–2024 explicitly absent; 52 core CHD (Q20–Q26) and 8 Q27–Q28 records; 7 with multiple core CHD codes; 3 records with `IDANOMAL=1` and no code.
- SIH: 474 primary core-CHD admissions (Q20–Q26), 75 primary Q27–Q28; all `MUNIC_RES` = 330100; years 2010–2025; 16 hospitals; 51.9% outside municipality; 30 deaths.
- Climate: 5,844 days; zero missing Tmax; model fixed to `era5_land`; P90 threshold 33.3 °C; 68 heat waves.
- Exposure linkage: 90,258/98,598 births with a complete main organogenesis window (91.5%); completeness 100% among linked births; ±7-day windows stored.
- Cross-checks: counts in `outputs/tables/*` reconcile with the processed CSVs (no manual edits).

---

## 5. Robustness

### Confidence thresholds

| Threshold | Conceptual edges | Exposure→phenotype paths | Direct pairs |
|---:|---:|---:|---:|
| 0.40 | 47 | 27 | 17 |
| 0.50 | 28 | 15 | 15 |
| 0.55 | 28 | 15 | 15 |
| 0.70 | 16 | 15 | 15 |
| 0.85 | 13 | 12 | 12 |

The qualitative conclusion “few direct human links, many mechanism-level gaps” is stable. The *number* of retained links is highly threshold-dependent, which is why the manuscript reports both the full graph and the high-confidence core.

### Local model

After correcting the conception window, the main birth-level model had OR 1.155 per SD (p = 0.318, q = 0.509). Firth regression gave OR 1.159 (p = 0.304), cluster-robust SE by month of conception gave OR 1.155 (0.829–1.611; p = 0.394), and the socio-economic Firth model gave OR 1.187 (0.889–1.571; p = 0.236). The ±7-day gestational-window sensitivity gave ORs of 1.071–1.221. Leave-one-year-out OR per SD was 1.136–1.608; p ranged 0.024–0.546. No model survives FDR in the primary family. The monthly model was null (RR 1.211; p = 0.176). The local heat finding is therefore **not robust enough for a causal claim**.

---

## 6. Human curation check

All 104 curated evidence rows (87 unique relations) have a verbatim quote. The 54 manual rows were read by the study team; the 49 batch rows were promoted only after an explicit review entry (including second-pass proposals, manual additions and full-text reading) and are flagged as AI-assisted, so independent human confirmation is recommended. Full-text quotations are re-checked against their archived short quotation, not against the abstract. PubMed quotes are verified automatically at build time and 25% are re-checked in validation; the CAPES thesis quote is checked against the archived Sucupira abstract. The curated layer is described as **team curation plus reviewed batch promotion**, without a dual independent screening step.

---

## 7. What was not validated

- Full texts of the 33 PubMed anchors and the CAPES thesis (only abstracts were verified).
- Records not retrieved by the top-N search strategy.
- Portuguese-language coverage is partial (SciELO via Crossref; CAPES thesis catalogue only, although all 560 hits/552 unique records were now retrieved and title-screened).
- HPO/ClinVar/Reactome annotations against primary sources (treated as curated databases).
- Causal claims (none are made).
