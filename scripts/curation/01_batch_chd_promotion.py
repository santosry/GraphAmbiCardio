"""Build the candidate queue for CHD-phenotype studies (automatic step).

The queue is only a *candidate* list. The rule is strict on purpose: a clause
must contain exactly one exposure term, exactly one CHD phenotype term and one
explicit effect-size expression, with no competing phenotype in the same
clause. Multi-phenotype result sentences are sent to human review because
assigning the first number to the first phenotype is a known source of wrong
edges.

Nothing here enters the graph directly. The reviewer marks rows in
``literature/curated/batch_chd_review.csv`` and the graph build only accepts
``verified`` rows, re-checking every quote against PubMed.

Usage:
    .venv/Scripts/python.exe scripts/curation/01_batch_chd_promotion.py
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from graphambicardio import config  # noqa: E402
from graphambicardio.curation.batch_extract import (  # noqa: E402
    PHENOTYPE_PATTERNS_ALL,
    extract_clause,
    iter_effects,
    normalise,
    split_clauses,
)
from graphambicardio.io_utils import write_csv  # noqa: E402
from graphambicardio.literature.pubmed import efetch  # noqa: E402
from graphambicardio.literature.screen import WINDOW_PATTERNS  # noqa: E402

CANDIDATES = ROOT / "literature" / "screening" / "exhaustive_candidates.csv"
CURATED = ROOT / "literature" / "curated"
QUEUE = CURATED / "batch_chd_queue.csv"
EDGES = CURATED / "batch_chd_edges.csv"

PHENOTYPE_VOCABULARY = [p["id"] for p in config.PHENOTYPES]
EXPOSURE_LABEL = {e["id"]: e["label"] for e in config.EXPOSURES}
PHENO_LABEL = {p["id"]: p["label"] for p in config.PHENOTYPES}

POP_RE = re.compile(
    r"(?:among|in|of)\s+([^.;]{0,90}?(?:infants|children|women|pregnancies|births|cases|controls|newborns|fetuses))",
    re.I,
)

QUEUE_FIELDS = [
    "candidate_key", "pmid", "doi", "title", "year", "journal",
    "exposure_id", "exposure_label", "phenotype_id", "phenotype_label",
    "candidate_exposures", "candidate_phenotypes",
    "study_design", "species", "evidence_type", "quote", "effect_direction",
    "population_or_model", "exposure_window", "status", "reason",
]
EDGE_FIELDS = [
    "source_id", "source_type", "target_id", "target_type", "relation", "layer",
    "evidence_type", "study_design", "species", "population_or_model",
    "exposure_window", "effect_direction", "context", "quote", "reference",
    "reference_type", "source_database", "notes",
]


def clean(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and value != value:
        return ""
    text = str(value).strip()
    return "" if text.lower() == "nan" else text


def split(value: Any) -> list[str]:
    return [x.strip() for x in clean(value).split(";") if x.strip()]


LOCAL_WINDOWS = {
    "preconception": r"before pregnancy|pre-?pregnan|pre-?conception|months before conception",
    "periconception": r"around conception|periconception|periconceptional",
}


def _window(clause: str, candidate_window: str) -> str:
    for name, pattern in WINDOW_PATTERNS.items():
        if re.search(pattern, clause, re.I):
            return name
    for name, pattern in LOCAL_WINDOWS.items():
        if re.search(pattern, clause, re.I):
            return name
    first = (candidate_window or "").split(";")[0].strip()
    return first or "not specified in abstract"


def _evidence_type(row: dict[str, Any]) -> tuple[str, str]:
    design = clean(row.get("design")).split(";")[0] or "unknown"
    if clean(row.get("is_review")).lower() == "true":
        return "indirect", "human"
    if clean(row.get("species_human")).lower() == "true":
        return "direct_human", "human"
    if clean(row.get("species_animal")).lower() == "true":
        return "experimental_animal", "animal"
    if clean(row.get("species_cell")).lower() == "true":
        return "experimental_cell", "cell"
    return "indirect", ""


def _score(clause: str, effects: list[dict[str, Any]]) -> float:
    # Prefer clauses that report a single effect size; multi-result sentences
    # are error-prone even when the rule accepts them.
    score = 3.0 if len(effects) == 1 else 0.5
    if re.search(r"95\s*%|confidence interval", clause, re.I):
        score += 1.0
    return score - len(effects[0]["text"]) / 1000.0


def main() -> None:
    rows = list(csv.DictReader(CANDIDATES.open(encoding="utf-8")))
    rows = [r for r in rows if "CHD:" in clean(r.get("phenotypes")) and clean(r.get("pmid"))]
    pmids = sorted({clean(r["pmid"]) for r in rows})
    studies = {s.pmid: s for s in efetch(pmids)}
    print(f"CHD candidates with PMID: {len(rows)}; abstracts: {len(studies)}")

    queue: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    seen_edges: set[tuple[str, str, str]] = set()
    for row in rows:
        base = {
            "candidate_key": row.get("candidate_key", ""),
            "pmid": clean(row["pmid"]),
            "doi": row.get("doi", ""),
            "title": row.get("title", ""),
            "year": row.get("year", ""),
            "journal": row.get("journal", ""),
            "candidate_exposures": row.get("exposures", ""),
            "candidate_phenotypes": row.get("phenotypes", ""),
        }
        study = studies.get(base["pmid"])
        if not study or not study.abstract:
            queue.append({
                **{k: "" for k in QUEUE_FIELDS}, **base,
                "status": "needs_review",
                "reason": "abstract not available via PubMed",
            })
            continue

        candidate_exposures = split(row.get("exposures"))
        candidate_phenotypes = [p for p in split(row.get("phenotypes")) if p.startswith("CHD:")]
        clauses = split_clauses(study.abstract)

        best: dict[str, Any] | None = None
        best_score = -1.0
        had_effect = False
        for clause in clauses:
            effects = list(iter_effects(clause))
            if effects:
                had_effect = True
            match = extract_clause(
                clause,
                candidate_exposures,
                candidate_phenotypes,
                PHENOTYPE_VOCABULARY,
                PHENOTYPE_PATTERNS_ALL,
            )
            if match is None:
                continue
            score = _score(clause, effects)
            if score > best_score:
                best_score = score
                best = {**match, "clause": clause}

        if best is None:
            reason = (
                "effect size found in the abstract but exposure or phenotype attribution is ambiguous"
                if had_effect
                else "no explicit effect size in any abstract clause"
            )
            queue.append({
                **{k: "" for k in QUEUE_FIELDS}, **base,
                "status": "needs_review", "reason": reason,
            })
            continue

        exposure = best["exposure_id"]
        phenotype = best["phenotype_id"]
        clause = best["clause"]
        effect = best["effect"]
        evidence_type, species = _evidence_type(row)
        design = clean(row.get("design")).split(";")[0] or "unknown"
        pop_match = POP_RE.search(clause)
        population = pop_match.group(1).strip() if pop_match else "not extracted from abstract"
        window = _window(clause, clean(row.get("window_terms")))

        edge_key = (exposure, phenotype, base["pmid"])
        status = "duplicate" if edge_key in seen_edges else "approved"
        seen_edges.add(edge_key)
        qrow = {
            **{k: "" for k in QUEUE_FIELDS},
            **base,
            "exposure_id": exposure,
            "exposure_label": EXPOSURE_LABEL.get(exposure, exposure),
            "phenotype_id": phenotype,
            "phenotype_label": PHENO_LABEL.get(phenotype, phenotype),
            "study_design": design,
            "species": species,
            "evidence_type": evidence_type,
            "quote": normalise(clause),
            "effect_direction": effect["text"][:220],
            "population_or_model": population,
            "exposure_window": window,
            "status": status,
            "reason": (
                "strict clause-level rule matched"
                if status == "approved"
                else "same study, exposure and phenotype already queued"
            ),
        }
        queue.append(qrow)
        if status != "approved":
            continue
        edges.append({
            "source_id": exposure,
            "source_type": "Exposure",
            "target_id": phenotype,
            "target_type": "Phenotype",
            "relation": "EXPOSURE_ASSOCIATED_WITH_PHENOTYPE",
            "layer": "observed",
            "evidence_type": evidence_type,
            "study_design": design,
            "species": species,
            "population_or_model": population,
            "exposure_window": window,
            "effect_direction": effect["text"][:220],
            "context": (
                f"Automated clause-level extraction: {EXPOSURE_LABEL.get(exposure, exposure)} "
                f"and {PHENO_LABEL.get(phenotype, phenotype)}"
            ),
            "quote": normalise(clause),
            "reference": base["pmid"],
            "reference_type": "PMID",
            "source_database": "Exhaustive screening batch (AI-assisted candidate; not yet reviewed)",
            "notes": "Candidate only. Requires review in batch_chd_review.csv before entering the graph.",
        })

    write_csv(QUEUE, queue, fieldnames=QUEUE_FIELDS)
    write_csv(EDGES, edges, fieldnames=EDGE_FIELDS)
    counts: dict[str, int] = {}
    for item in queue:
        counts[item["status"]] = counts.get(item["status"], 0) + 1
    print(f"queue: {len(queue)} rows; approved candidates: {counts.get('approved', 0)}; written {QUEUE}")
    print(f"candidate edges: {len(edges)}; written {EDGES}")
    print("counts:", ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))


if __name__ == "__main__":
    main()
