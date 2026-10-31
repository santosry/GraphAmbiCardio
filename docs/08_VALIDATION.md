# 08 — Validation report

Generated: 2026-10-31. Machine-readable: `reports/validation_results.json`; human-readable: `reports/validation_report.md`.

---

## 1. Levels of validation and results

| Level | Check | Result |
|---|---|---|
| Bibliographic | 46 curated edges have a PMID and a verbatim quote; 100% verified at build time; 25% (11 edges) re-checked at validation | **Passed** |
| Bibliographic | 29 anchor PMIDs resolvable via NCBI E-utilities | **Passed** (29/29) |
| Biological | Manual reading of every curated edge for developmental/molecular coherence; layers and caveats recorded | **Passed with documented caveats** |
| Data | Municipality, period, missingness, duplicates, range checks for SINASC, SIH and climate | **Passed** |
| Computational | Unique node IDs, unique evidence IDs, edge endpoints exist, no self-loops, valid relation vocabulary, confidence ∈ [0,1], grade ∈ {A–E} | **Passed** |
| Robustness | Confidence-threshold sensitivity (0.40–0.85); leave-one-year-out models | **Executed; results reported with instability** |
| Human audit | Two-reviewer sample | **Pending** (sheet provided) |

---

## 2. Automated checks

```
nodes: 2,234 | relations: 4,100 | evidence rows: 4,596
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

- SINASC: 98,598 births; all `CODMUNRES` = 330100; years 2010–2022 + 2025; 2023–2024 explicitly absent; 59 CHD cases; 8 with multiple CHD codes; 3 records with `IDANOMAL=1` and no code.
- SIH: 549 primary-CHD admissions; all `MUNIC_RES` = 330100; years 2010–2025; 18 hospitals; 55% outside municipality; 33 deaths.
- Climate: 5,844 days; zero missing Tmax; P90 threshold 34.2 °C; 73 heat waves.
- Exposure linkage: 90,008/98,598 births with a complete organogenesis window (91.3%); completeness 100% among linked births.
- Cross-checks: counts in `outputs/tables/*` reconcile with the processed CSVs (no manual edits).

---

## 5. Robustness

### Confidence thresholds

| Threshold | Conceptual edges | Exposure→phenotype paths | Direct pairs |
|---:|---:|---:|---:|
| 0.40 | 39 | 23 | 13 |
| 0.50 | 20 | 11 | 11 |
| 0.55 | 20 | 11 | 11 |
| 0.70 | 12 | 11 | 11 |
| 0.85 | 9 | 8 | 8 |

The qualitative conclusion “few direct human links, many mechanism-level gaps” is stable. The *number* of retained links is highly threshold-dependent, which is why the manuscript reports both the full graph and the high-confidence core.

### Local model

Leave-one-year-out OR per SD: 1.47–1.66; p ranged 0.010–0.056. The direction is stable but statistical significance is not. The monthly model was null. The local heat finding is therefore **not robust enough for a causal claim**.

---

## 6. Manual audit (pending)

`reports/manual_audit_sample.csv` contains 20 randomly selected curated edges with columns for two independent reviewers (`reviewer_1_supports`, `reviewer_2_supports`, `agreement`, `resolution`). Until completed:

- the curated layer is **single-reviewer verified**;
- no kappa is reported;
- the manuscript must state this limitation.

---

## 7. What was not validated

- Full texts of the 29 anchors (only abstracts were verified).
- Records not retrieved by the top-N search strategy.
- Portuguese-language literature (SciELO/BVS blocked).
- HPO/ClinVar/Reactome annotations against primary sources (treated as curated databases).
- Causal claims (none are made).
