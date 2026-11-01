"""Tests for the deterministic batch-curation rules and review layer."""
from __future__ import annotations

from graphambicardio.curation.batch_extract import (
    EXPOSURE_PATTERNS,
    PHENOTYPE_PATTERNS_ALL,
    extract_clause,
    find_effect,
    split_clauses,
)
from graphambicardio.curation.batch_review import (
    resolved_rows,
    review_issues,
)
from graphambicardio.literature.screen import PHENOTYPE_PATTERNS

VOCABULARY = list(PHENOTYPE_PATTERNS)
PATTERNS = PHENOTYPE_PATTERNS_ALL


def _extract(clause, exposures, phenotypes):
    return extract_clause(clause, exposures, phenotypes, VOCABULARY, PATTERNS)


def test_lowercase_or_is_not_an_odds_ratio():
    clause = (
        "Only valvar pulmonary stenosis (VPS) was highly associated with mothers "
        "who smoked 20 cigarettes or more per day (p = 0.03)."
    )
    assert find_effect(clause) is None
    assert _extract(clause, ["EXP:SMOKE"], ["CHD:PS"]) is None


def test_p_value_is_not_an_effect_size():
    assert find_effect("Smoking was associated with VSD (OR p = 0.03).") is None
    assert find_effect("Smoking was associated with VSD (OR = 1.2; p = 0.03).")["value"] == 1.2


def test_confidence_interval_bounds_are_not_effects():
    assert find_effect("Heat was associated with ASD (OR (95% CI 1.1-1.4)).") is None
    assert find_effect("Heat was associated with ASD (95% CI: 1.1-1.4).") is None


def test_ordinal_text_is_rejected():
    clause = (
        "Patent ductus arteriosus was associated with PM10 (OR 1st trimester=3.96, "
        "95% Confidence Interval (CI): 1.36, 11.53)."
    )
    assert find_effect(clause) is None
    assert _extract(clause, ["EXP:PM10"], ["CHD:PDA"]) is None


def test_common_effect_formats_are_accepted():
    cases = {
        "Maternal alcohol consumption doubled the risk of atrial septal defect (OR = 1.9, CI95 1.0-3.4).": 1.9,
        "Non-isolated atrial septal defect showed an association with PM2.5 (aOR range: 1.882 to 4.382).": 1.882,
        "Children exposed to alcohol had increased risk of tetralogy of Fallot (adjusted-RR:8.62).": 8.62,
        "Nitrogen dioxide was associated with coarctation of the aorta (OR for high versus low = 1.14).": 1.14,
        "Arsenic exposure was associated with coarctation (prevalence odds ratio = 3.4).": 3.4,
        "PM2.5 was associated with patent ductus arteriosus (adjusted OR 0.78).": 0.78,
    }
    for clause, expected in cases.items():
        found = find_effect(clause)
        assert found is not None, clause
        assert abs(found["value"] - expected) < 1e-9, clause


def test_inverse_direction_is_flagged():
    found = find_effect("PM2.5 was inversely associated with PDA (OR 0.78).")
    assert found is not None
    assert found["direction"] == "inverse"


def test_multi_phenotype_sentence_is_rejected():
    clause = (
        "A 10 microgram increase in PM2.5 was associated with ventricular septal "
        "defects (OR=1.34) and patent ductus arteriosus (OR=1.19)."
    )
    assert _extract(clause, ["EXP:PM25"], ["CHD:VSD", "CHD:PDA"]) is None


def test_phenotype_must_be_in_the_candidate_list():
    clause = "Maternal smoking was associated with tetralogy of Fallot (OR = 1.5)."
    assert _extract(clause, ["EXP:SMOKE"], ["CHD:VSD"]) is None
    assert _extract(clause, ["EXP:SMOKE"], ["CHD:TOF"])["phenotype_id"] == "CHD:TOF"


def test_asd_needs_cardiac_context():
    autism = "Maternal exposure was associated with autism spectrum disorder (ASD) (OR = 1.5)."
    assert _extract(autism, ["EXP:SMOKE"], ["CHD:ASD"]) is None
    heart = "Maternal smoking was associated with atrial septal defect (ASD) (OR = 1.5)."
    assert _extract(heart, ["EXP:SMOKE"], ["CHD:ASD"])["phenotype_id"] == "CHD:ASD"


def test_lead_as_a_verb_is_not_a_metal_exposure():
    clause = "Higher temperatures lead to an increased risk of ventricular septal defect (OR 1.2)."
    assert _extract(clause, ["EXP:METALS"], ["CHD:VSD"]) is None
    metal = "Paternal metal exposure was associated with increased risk of VSD (adjusted prevalence ratio = 2.70)."
    assert _extract(metal, ["EXP:METALS"], ["CHD:VSD"])["exposure_id"] == "EXP:METALS"


def test_two_exposures_are_rejected():
    clause = (
        "Co-exposure to PM2.5 and heat was associated with ventricular septal defect "
        "(OR = 1.5)."
    )
    assert _extract(clause, ["EXP:PM25", "EXP:HEAT"], ["CHD:VSD"]) is None


def test_split_clauses_keeps_sentences_and_semicolons():
    parts = split_clauses(
        "The first result was positive and significant (OR = 1.5). "
        "The second result was null and non-significant; "
        "the third result was negative and imprecise."
    )
    assert len(parts) == 3
    assert parts[0].startswith("The first")


def test_every_exposure_pattern_compiles():
    import re

    for name, pattern in EXPOSURE_PATTERNS.items():
        re.compile(pattern)
        assert name.startswith("EXP:")


# ---------------------------------------------------------------------------
# Review layer
# ---------------------------------------------------------------------------
def _queue_row(**overrides):
    row = {
        "candidate_key": "k",
        "pmid": "123",
        "doi": "",
        "title": "T",
        "year": "2020",
        "journal": "J",
        "exposure_id": "EXP:SMOKE",
        "phenotype_id": "CHD:VSD",
        "study_design": "cohort",
        "evidence_type": "direct_human",
        "species": "human",
        "quote": "Maternal smoking was associated with ventricular septal defect (OR = 1.5).",
        "effect_direction": "OR = 1.5",
        "population_or_model": "infants",
        "exposure_window": "first_trimester",
        "status": "approved",
        "reason": "strict clause-level rule matched",
    }
    row.update(overrides)
    return row


def _review(**overrides):
    row = {
        "pmid": "123",
        "exposure_id": "EXP:SMOKE",
        "phenotype_id": "CHD:VSD",
        "review_status": "verified",
        "review_quote": "",
        "review_effect": "",
        "review_population": "",
        "review_window": "",
        "review_note": "checked",
        "reviewed_by": "reviewer",
        "reviewed_at": "2026-11-01",
    }
    row.update(overrides)
    return row


def test_review_layer_accepts_a_verified_row():
    assert review_issues([_review()], [_queue_row()]) == []
    resolved = resolved_rows(
        {("123", "EXP:SMOKE", "CHD:VSD"): _review(review_effect="reviewed effect")},
        [_queue_row()],
    )
    assert len(resolved) == 1
    assert resolved[0]["effect_direction"] == "reviewed effect"


def test_review_layer_rejects_unknown_status_and_requires_manual_metadata():
    assert any("status" in i for i in review_issues([_review(review_status="maybe")], [_queue_row()]))
    manual = _review(
        pmid="999",
        review_quote="Maternal smoking was associated with ventricular septal defect (OR = 1.5).",
        review_effect="OR 1.5",
        review_design="case_control",
    )
    assert review_issues([manual], [_queue_row()]) == []


def test_review_layer_checks_the_quote():
    bad = _review(review_quote="Maternal smoking was associated with asthma (OR = 1.5).")
    issues = review_issues([bad], [_queue_row()])
    assert any("exposure" in i or "phenotype" in i for i in issues)


def test_manual_addition_uses_the_review_fields():
    manual = _review(
        phenotype_id="CHD:ASD",
        review_quote="Maternal smoking was associated with atrial septal defect (OR = 1.4).",
        review_effect="OR 1.4",
        review_design="case_control",
        review_population="infants",
        review_window="first trimester",
    )
    issues = review_issues([manual], [_queue_row()])
    assert issues == []
    resolved = resolved_rows({("123", "EXP:SMOKE", "CHD:ASD"): manual}, [_queue_row()])
    assert len(resolved) == 1
    assert resolved[0]["phenotype_id"] == "CHD:ASD"
    assert resolved[0]["study_design"] == "case_control"


def test_manual_addition_requires_design_and_effect():
    manual = _review(phenotype_id="CHD:ASD", review_quote="Maternal smoking was associated with atrial septal defect (OR = 1.4).")
    issues = review_issues([manual], [_queue_row()])
    assert any("effect" in i for i in issues)
    assert any("design" in i for i in issues)


def test_only_verified_rows_are_resolved():
    reviews = {
        ("123", "EXP:SMOKE", "CHD:VSD"): _review(review_status="rejected"),
    }
    assert resolved_rows(reviews, [_queue_row()]) == []
