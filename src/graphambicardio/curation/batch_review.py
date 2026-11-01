"""Review layer for the AI-assisted batch promotion of candidate studies.

Automatic extraction produces a *candidate* queue. Nothing from that queue
enters the graph unless a reviewer has explicitly marked it ``verified`` in
``literature/curated/batch_chd_review.csv``. The review file is the auditable
link between the automated queue and the evidence layer:

* one row per ``(pmid, exposure_id, phenotype_id)``;
* ``review_status`` is ``verified`` or ``rejected``;
* a reviewer may override the automatically captured quote, effect text,
  population and exposure window, and must add a short note with the reason.

This module never touches the network. Quote verification against PubMed is
performed by the graph build, which refuses to continue when a quote is not
verbatim.
"""
from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any, Iterable

from .. import config
from . import seed_edges
from .batch_extract import EXPOSURE_PATTERNS, PHENOTYPE_PATTERNS_ALL, normalise, pluralise

# A batch row must never duplicate an edge that was already curated manually for
# the same study, exposure and phenotype. Double counting would inflate the
# evidence table without adding information.
def _manual_keys() -> set[Key]:
    keys: set[Key] = set()
    for collection in (
        seed_edges.EXPOSURE_PHENOTYPE,
        seed_edges.ADDITIONAL_EDGES,
        seed_edges.CAPES_THESIS_EDGES,
    ):
        for item in collection:
            if item.get("relation") != "EXPOSURE_ASSOCIATED_WITH_PHENOTYPE":
                continue
            keys.add((str(item.get("reference", "")), item["source_id"], item["target_id"]))
    return keys


MANUAL_KEYS = _manual_keys()

REVIEW_FIELDS = [
    "pmid",
    "exposure_id",
    "phenotype_id",
    "review_status",
    "review_quote",
    "review_effect",
    "review_population",
    "review_window",
    "review_design",
    "review_note",
    "reviewed_by",
    "reviewed_at",
]

STATUSES = {"verified", "rejected"}

Key = tuple[str, str, str]


def key_of(row: dict[str, Any]) -> Key:
    return (
        str(row.get("pmid", "")).strip(),
        str(row.get("exposure_id", "")).strip(),
        str(row.get("phenotype_id", "")).strip(),
    )


def load_reviews(path: Path) -> dict[Key, dict[str, Any]]:
    """Load the review CSV into a dictionary keyed by PMID, exposure, phenotype."""
    if not path.exists():
        return {}
    with path.open(encoding="utf-8", newline="") as handle:
        reviews: dict[Key, dict[str, Any]] = {}
        for row in csv.DictReader(handle):
            key = key_of(row)
            reviews[key] = {field: (row.get(field) or "").strip() for field in REVIEW_FIELDS}
        return reviews


def _quote_is_specific(quote: str) -> bool:
    return len(normalise(quote)) >= 30


def review_issues(
    reviews: Iterable[dict[str, Any]],
    queue_rows: Iterable[dict[str, Any]],
) -> list[str]:
    """Return human-readable problems with the review layer.

    Used by the validation pipeline and by the unit tests.
    """
    rows = list(queue_rows)
    queue = {key_of(row): row for row in rows}
    by_pmid: dict[str, dict[str, Any]] = {}
    for row in rows:
        by_pmid.setdefault(str(row.get("pmid", "")).strip(), row)
    issues: list[str] = []
    seen: set[Key] = set()
    for row in reviews:
        key = key_of(row)
        label = "|".join(key)
        if not all(key):
            issues.append(f"incomplete review key: {label}")
            continue
        if key in seen:
            issues.append(f"duplicate review row: {label}")
        seen.add(key)
        status = str(row.get("review_status", "")).strip().lower()
        if status not in STATUSES:
            issues.append(f"unsupported review status: {label} ({status or 'empty'})")
            continue
        queue_row = queue.get(key)
        manual_addition = queue_row is None
        if manual_addition:
            if key[0] not in by_pmid:
                issues.append(f"review row without any queue record for the PMID: {label}")
                continue
            if status == "verified" and not row.get("review_effect"):
                issues.append(f"manual addition without reviewed effect: {label}")
            if status == "verified" and not row.get("review_design"):
                issues.append(f"manual addition without reviewed study design: {label}")
        design = str(row.get("review_design", "")).strip()
        if design and design not in config.STUDY_DESIGN_WEIGHTS:
            issues.append(f"verified row with unknown study design: {label} ({design})")
        if status != "verified":
            continue
        if key in MANUAL_KEYS:
            issues.append(f"verified row duplicates manual curation: {label}")
            continue
        quote = normalise(row.get("review_quote") or queue_row.get("quote", ""))
        if not _quote_is_specific(quote):
            issues.append(f"verified row without a usable quote: {label}")
            continue
        exposure = key[1]
        pattern = EXPOSURE_PATTERNS.get(exposure)
        if pattern is None:
            issues.append(f"verified row with unknown exposure: {label}")
        elif not re.search(pattern, quote, re.I):
            issues.append(f"quote does not mention the exposure: {label}")
        phenotype = key[2]
        ph_pattern = PHENOTYPE_PATTERNS_ALL.get(phenotype)
        if ph_pattern is None:
            issues.append(f"verified row with unknown phenotype: {label}")
        elif not re.search(pluralise(ph_pattern), quote, re.I):
            issues.append(f"quote does not mention the phenotype: {label}")
    return issues


def resolved_rows(
    reviews: dict[Key, dict[str, Any]],
    queue_rows: Iterable[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Merge verified review rows with their queue candidates.

    Only ``verified`` rows are returned. Quote, effect text, population and
    window come from the review when provided, otherwise from the queue.
    """
    rows = list(queue_rows)
    queue = {key_of(row): row for row in rows}
    by_pmid: dict[str, dict[str, Any]] = {}
    for row in rows:
        by_pmid.setdefault(str(row.get("pmid", "")).strip(), row)
    resolved: list[dict[str, Any]] = []
    for key, review in reviews.items():
        if review.get("review_status", "").lower() != "verified":
            continue
        queue_row = queue.get(key)
        if queue_row is None:
            base = by_pmid.get(key[0])
            if base is None:
                continue
            queue_row = {
                **base,
                "exposure_id": key[1],
                "phenotype_id": key[2],
                "quote": "",
                "effect_direction": "",
                "population_or_model": "",
                "exposure_window": "",
                "study_design": "",
                "evidence_type": "",
                "species": "",
            }
        resolved.append(
            {
                **queue_row,
                "pmid": key[0],
                "exposure_id": key[1],
                "phenotype_id": key[2],
                "quote": normalise(review.get("review_quote") or queue_row.get("quote", "")),
                "effect_direction": review.get("review_effect") or queue_row.get("effect_direction", ""),
                "population_or_model": review.get("review_population")
                or queue_row.get("population_or_model", ""),
                "exposure_window": review.get("review_window") or queue_row.get("exposure_window", ""),
                "study_design": review.get("review_design") or queue_row.get("study_design", ""),
                "review_note": review.get("review_note", ""),
                "reviewed_by": review.get("reviewed_by", ""),
                "reviewed_at": review.get("reviewed_at", ""),
            }
        )
    return resolved
