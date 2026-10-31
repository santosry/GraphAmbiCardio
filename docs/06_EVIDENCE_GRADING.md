# 06 — Evidence grading framework

The framework was frozen before graph construction. It is designed to be **transparent and reproducible**, not to produce a single “truth score”. Different study types answer different questions; the graph therefore keeps the evidence type visible and never collapses it.

---

## 1. Evidence types (directness)

| Code | Weight | Meaning |
|---|---:|---|
| `direct_human` | 1.00 | Association investigated in humans with the relevant phenotype and prenatal exposure |
| `experimental_human` | 0.85 | Human cells/organoids/explants with a functional assay |
| `experimental_animal` | 0.65 | In vivo animal model with species and developmental window recorded |
| `experimental_cell` | 0.50 | Cell lines / non-human in vitro systems |
| `structured_database` | 0.70 | Curated database annotation (HPO, ClinVar, Reactome) |
| `indirect` | 0.40 | Supported only through intermediate steps or a review of experiments |
| `hypothesis` | 0.10 | Plausible composition of observed edges; no direct empirical test |

**Why not a single scale for all designs?** A case-control study cannot test a molecular mechanism, and an animal experiment cannot estimate human population risk. Applying one epidemiological scale to both would be a category error. The graph keeps the distinction and the confidence formula only aggregates *within* an edge with the type attached.

---

## 2. Study-design weights

| Design | Weight |
|---|---:|
| Systematic review / meta-analysis | 0.90 |
| Cohort | 0.90 |
| Case-control | 0.80 |
| Registry | 0.80 |
| Cross-sectional | 0.60 |
| Ecological | 0.45 |
| Animal in vivo | 0.60 |
| In vitro | 0.40 |
| In silico | 0.20 |
| Narrative review | 0.70 |
| Curated database | 0.90 |
| Unknown | 0.30 |

A meta-analysis is not automatically “better” than a well-conducted cohort; the weight reflects the synthesis role, and the `evidence_type` still records that a meta-analysis of observational studies is `direct_human`, whereas a narrative review of animal experiments is `indirect`.

---

## 3. Confidence formula

For an edge with evidence rows *i*:

```
base_i   = 0.7 · type_weight_i + 0.3 · design_weight_i
base     = min(0.9, max_i base_i)
n_refs   = number of distinct references
replication          = min(0.15, 0.05 · (n_refs − 1))
species_concordance  = 0.05 if human AND (animal or cell) evidence coexist
single_study_penalty = 0.05 if n_refs ≤ 1
non_significance_penalty = 0.10 if effect_direction/notes contain
                           "non-significant", "marginal" or "null"
contradiction_penalty = 0.10 if notes explicitly record contradiction

confidence = clip(base + replication + species_concordance
                  − single_study_penalty − non_significance_penalty
                  − contradiction_penalty, 0, 0.95)
```

The weighted sum (rather than a product) avoids double-penalising strong animal experiments. The cap at 0.9 prevents a single perfect study from reaching certainty; the cap at 0.95 leaves room for replication.

---

## 4. Grades

| Grade | Confidence | Interpretation |
|---|---:|---|
| A | ≥ 0.88 | Direct human evidence with replication, or strongly replicated human genetics |
| B | 0.72–0.88 | Direct human evidence with caveats (impression, marginal significance) or human experimental |
| C | 0.55–0.70 | Solid experimental animal evidence, or indirect evidence with mechanistic coherence |
| D | 0.40–0.55 | Review-level/indirect/ecological support |
| E | < 0.40 | Sparse, hypothesis-level or unsupported |

Grades are **properties of edges for this study’s question**, not a judgement of the biological truth of a textbook statement. A developmental relation can be grade D because no study tested that exact exposure→phenotype chain, even though the embryology is well established.

### 4.1 Evidence tiers used by the GraphAmbiCardio interface

The three-level hierarchy requested by the scientific review is implemented as a derived field (`evidence_tier`):

| Tier | Rule | Interface colour |
|---|---|---|
| **Bem sustentada** | observed A/B with direct human evidence, or structured database annotation | green |
| **Plausível (experimental)** | observed C with experimental human/animal/cell evidence | amber |
| **Não demonstrada** | observed D/E, indirect review, hypothesis or inferred rule | red |
| **Contextual** | ecological indicators and humidity | blue |
| **Inferida (regra)** | pathway→process keyword mapping | grey |

This tier is a **presentation layer** over the same confidence formula; it does not change the underlying evidence rows.

---

## 5. Worked examples (values from `outputs/graph/relations.csv`)

| Edge | Evidence | Base | Adjustments | Confidence | Grade |
|---|---|---:|---|---:|---|
| HEAT → ASD | human cohort (PMID 27494594) | 0.7·1.0 + 0.3·0.9 = 0.97 → cap 0.90 | −0.05 single study | **0.85** | B |
| PM2.5 → VSD | human case-control, non-significant | 0.90 | −0.05 single, −0.10 non-significance | **0.75** | B |
| PM2.5 → TOF | meta-analysis, marginal | 0.90 | −0.05 single, −0.10 marginal | **0.75** | B |
| VPA → CHD:ALL | meta-analysis (PMID 41161707) | 0.90 | −0.05 single | **0.85** | B |
| HEAT → neural crest | chick/zebrafish experiment | 0.7·0.65 + 0.3·0.60 = 0.635 | −0.05 single | **0.585** | C |
| Dioxin → AHR | human ESC experiment | 0.7·0.85 + 0.3·0.40 = 0.715 | −0.05 | **0.665** | C |
| PM2.5 → oxidative stress | narrative review | 0.7·0.40 + 0.3·0.70 = 0.49 | −0.05 | **0.44** | D |
| OFT → TOF | narrative review | 0.49 | −0.05 | **0.44** | D |
| GATA4 → ASD | human genetics + HPO annotation | 0.90 + replication | +0.05 (2 refs) | **0.95** | A |
| Alcohol → dTGA | meta-analysis, subgroup with overall null | 0.90 | −0.05 single, −0.10 null-overall | **0.75** | B |

---

## 6. What the framework does **not** do

- It does **not** sum publication counts.
- It does **not** use centrality as evidence.
- It does **not** treat a structured database annotation as proof of causation.
- It does **not** equate a human biomarker with a developmental mechanism.
- It does **not** hide contradictory evidence: contradictions lower the confidence and remain visible in `evidence.csv`.
- It does **not** convert an ecological association into an individual-level effect.

---

## 7. Human audit

Every observed (curated) edge was read manually by the study team and its quote is re-verified automatically against PubMed at build time and in the validation step.

---

## 8. Sensitivity

Because the thresholds are conventional, all analyses are repeated at confidence cut-offs 0.40, 0.50, 0.55, 0.70 and 0.85 (`outputs/tables/sensitivity_evidence_thresholds.csv`). Results are reported as stable only if the qualitative conclusion survives the range. In this version, the set of direct exposure→phenotype links shrinks from 11 to 8 between 0.50 and 0.85, which is why the manuscript reports the high-confidence core separately from the fuller graph.
