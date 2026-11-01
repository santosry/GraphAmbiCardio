"""Second-pass proposals for abstracts with an effect size but ambiguous attribution.

The strict first pass rejects a clause when it mentions more than one phenotype,
because assigning the first number to the first phenotype is a known error. This
second pass only *proposes* pairs: it maps each explicit effect size to the
nearest phenotype mention in the same clause and records how far apart they are.

Proposals are not evidence. A reviewer must copy the proposal into
``batch_chd_review.csv`` with ``review_status=verified`` (or reject it), and the
graph build re-verifies the quote against PubMed.

Usage:
    .venv/Scripts/python.exe scripts/curation/03_propose_ambiguous.py
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
from graphambicardio.curation import batch_review  # noqa: E402
from graphambicardio.curation.batch_extract import (  # noqa: E402
    COMPETING_EXPOSURES,
    EXPOSURE_PATTERNS,
    PHENOTYPE_PATTERNS_ALL,
    iter_effects,
    normalise,
    pluralise,
    split_clauses,
)
from graphambicardio.io_utils import read_csv, today, write_csv  # noqa: E402
from graphambicardio.literature.pubmed import efetch  # noqa: E402

QUEUE = ROOT / "literature" / "curated" / "batch_chd_queue.csv"
REVIEW = ROOT / "literature" / "curated" / "batch_chd_review.csv"
OUT = ROOT / "literature" / "curated" / "batch_chd_proposals.csv"
REPORT = ROOT / "reports" / "batch_chd_proposals.md"

PATTERNS = PHENOTYPE_PATTERNS_ALL
VOCABULARY = [p["id"] for p in config.PHENOTYPES]
PROPOSAL_FIELDS = [
    "pmid", "exposure_id", "phenotype_id", "quote", "effect", "gap_chars",
    "orientation", "n_phenotypes", "n_effects", "title", "year", "journal",
    "status", "reason",
]


def phenotype_mentions(clause: str) -> list[tuple[int, int, str]]:
    found: list[tuple[int, int, str]] = []
    for pid in VOCABULARY:
        pattern = PATTERNS.get(pid)
        if not pattern:
            continue
        for match in re.finditer(pluralise(pattern), clause, re.I):
            if pid == "CHD:ASD" and not re.search(
                r"heart|cardiac|septal|atrial", clause, re.I
            ):
                continue
            found.append((match.start(), match.end(), pid))
    return sorted(found)


ALL_EXPOSURE_PATTERNS = {
    **EXPOSURE_PATTERNS,
    **COMPETING_EXPOSURES,
}


def exposure_mentions(clause: str) -> list[tuple[int, int, str]]:
    found: list[tuple[int, int, str]] = []
    for eid, pattern in ALL_EXPOSURE_PATTERNS.items():
        for match in re.finditer(pattern, clause, re.I):
            found.append((match.start(), match.end(), eid))
    return sorted(found)


def nearest_exposure_id(
    clause: str, effect_start: int, effect_end: int, mentions: list[tuple[int, int, str]]
) -> str | None:
    left = [m for m in mentions if m[1] <= effect_start]
    if left:
        mention = max(left, key=lambda m: m[1])
        if effect_start - mention[1] <= 400:
            return mention[2]
    right = [m for m in mentions if m[0] >= effect_end]
    if right:
        mention = min(right, key=lambda m: m[0])
        if mention[0] - effect_end <= 80:
            return mention[2]
    return None


def propose(row: dict[str, Any], abstract: str) -> list[dict[str, Any]]:
    candidate_exposures = [e for e in (row.get("candidate_exposures") or "").split(";") if e]
    candidate_phenotypes = [p for p in (row.get("candidate_phenotypes") or "").split(";") if p]
    proposals: list[dict[str, Any]] = []
    for clause in split_clauses(abstract):
        effects = list(iter_effects(clause))
        if not effects:
            continue
        exposures = [
            e for e in candidate_exposures
            if e in EXPOSURE_PATTERNS and re.search(EXPOSURE_PATTERNS[e], clause, re.I)
        ]
        if len(exposures) != 1:
            continue
        mentions = phenotype_mentions(clause)
        if not mentions:
            continue
        exp_mentions = exposure_mentions(clause)
        for effect in effects:
            nearest_exposure = nearest_exposure_id(
                clause, effect["start"], effect["end"], exp_mentions
            )
            if nearest_exposure != exposures[0]:
                continue
            left = [m for m in mentions if m[1] <= effect["start"]]
            right = [m for m in mentions if m[0] >= effect["end"]]
            orientation = "effect_after_phenotype"
            if left:
                mention = max(left, key=lambda m: m[1])
                gap = effect["start"] - mention[1]
            elif right:
                mention = min(right, key=lambda m: m[0])
                gap = mention[0] - effect["end"]
                orientation = "effect_before_phenotype"
            else:
                continue
            limit = 160 if orientation == "effect_after_phenotype" else 60
            if gap > limit:
                continue
            phenotype = mention[2]
            if phenotype not in candidate_phenotypes:
                continue
            proposals.append(
                {
                    "pmid": row["pmid"],
                    "exposure_id": exposures[0],
                    "phenotype_id": phenotype,
                    "quote": normalise(clause),
                    "effect": effect["text"],
                    "gap_chars": gap,
                    "orientation": orientation,
                    "n_phenotypes": len({m[2] for m in mentions}),
                    "n_effects": len(effects),
                    "title": row.get("title", ""),
                    "year": row.get("year", ""),
                    "journal": row.get("journal", ""),
                    "status": "proposed",
                    "reason": "nearest-phenotype attribution; requires review",
                }
            )
    return proposals


def main() -> None:
    queue = read_csv(QUEUE)
    pending = [row for row in queue if row.get("status") != "approved"]
    reviews = batch_review.load_reviews(REVIEW)
    blocked = {batch_review.key_of(r) for r in reviews.values()} | set(batch_review.MANUAL_KEYS)
    candidates = pending
    studies = {s.pmid: s for s in efetch(sorted({row["pmid"] for row in candidates}))}

    best: dict[tuple[str, str, str], dict[str, Any]] = {}
    blocked_skipped = 0
    for row in candidates:
        study = studies.get(row["pmid"])
        if not study or not study.abstract:
            continue
        for proposal in propose(row, study.abstract):
            key = (proposal["pmid"], proposal["exposure_id"], proposal["phenotype_id"])
            if key in blocked:
                blocked_skipped += 1
                continue
            if key not in best or proposal["gap_chars"] < best[key]["gap_chars"]:
                best[key] = proposal
    proposals = sorted(best.values(), key=lambda p: (p["pmid"], p["exposure_id"], p["phenotype_id"]))

    write_csv(OUT, proposals, fieldnames=PROPOSAL_FIELDS)

    lines = [
        "# Second-pass proposals for ambiguous abstracts",
        "",
        f"Generated: {today()}",
        "",
        "These proposals are **not evidence**. Each row maps an explicit effect size",
        "to the nearest phenotype mention in the same clause. A reviewer must accept",
        "or reject every row in `literature/curated/batch_chd_review.csv` before the",
        "build can use it.",
        "",
        f"- queue rows without a decision: **{len(pending)}**",
        f"- proposal pairs skipped because already reviewed or already manual: **{blocked_skipped}**",
        f"- proposals: **{len(proposals)}**",
        "",
    ]
    for proposal in proposals:
        study = studies.get(proposal["pmid"])
        lines += [
            f"## PMID {proposal['pmid']}: {proposal['title']}",
            "",
            f"- Proposal: **{proposal['exposure_id']} -> {proposal['phenotype_id']}**",
            f"- Effect: `{proposal['effect']}`",
            f"- Gap to phenotype mention: {proposal['gap_chars']} characters ({proposal['orientation']})",
            f"- Phenotypes in clause: {proposal['n_phenotypes']}; effects in clause: {proposal['n_effects']}",
            "",
            "**Clause:**",
            "",
            f"> {proposal['quote']}",
            "",
        ]
        if study and study.abstract:
            lines += ["**Abstract:**", "", study.abstract, ""]
    REPORT.write_text("\n".join(lines), encoding="utf-8")

    print(f"pending rows: {len(pending)}; proposals: {len(proposals)}")
    print(f"written {OUT}")
    print(f"written {REPORT}")


if __name__ == "__main__":
    main()
