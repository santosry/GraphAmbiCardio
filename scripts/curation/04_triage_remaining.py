"""Prioritised triage of queue rows that still need manual reading.

This is not a curation step and it does not change evidence. It classifies the
rows that the strict extractor sent to review so the team can start with the
records that actually contain a human epidemiological estimate.

Classes
-------
human_numeric      human study with at least one explicit effect size
human_qualitative  human study with association language but no numeric estimate
human_no_effect    human study without association language in the abstract
synthesis          review, meta-analysis or other synthesis
experimental       animal or cell study
clinical           surgical, diagnostic or device study
unclassified       none of the above
no_abstract        PubMed abstract not available
reviewed           already has a verified or rejected review entry

Usage:
    .venv/Scripts/python.exe scripts/curation/04_triage_remaining.py
"""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from graphambicardio.curation import batch_review  # noqa: E402
from graphambicardio.curation.batch_extract import (  # noqa: E402
    EXPOSURE_PATTERNS,
    PHENOTYPE_PATTERNS_ALL,
    iter_effects,
    pluralise,
    split_clauses,
)
from graphambicardio.io_utils import read_csv, today, write_csv  # noqa: E402
from graphambicardio.literature.pubmed import efetch  # noqa: E402
from graphambicardio.literature.screen import SPECIES_PATTERNS  # noqa: E402

QUEUE = ROOT / "literature" / "curated" / "batch_chd_queue.csv"
REVIEW = ROOT / "literature" / "curated" / "batch_chd_review.csv"
OUT = ROOT / "literature" / "curated" / "batch_chd_triage.csv"
REPORT = ROOT / "reports" / "batch_chd_triage.md"

FIELDS = [
    "pmid", "title", "year", "journal", "candidate_exposures", "candidate_phenotypes",
    "triage_class", "triage_reason", "has_effect_size", "has_association_language",
]
ASSOCIATION = re.compile(r"\b(associat|risk|odds|increased|decreased|higher|lower|excess|relation)", re.I)
CLINICAL_TITLE = re.compile(
    r"\b(surg|repair|operation|operative|transcatheter|catheter|implant|device|"
    r"technique|outcome after|follow-up|anomalous|diagnos|management|case report|"
    r"echocardiograph|stent|valvuloplasty|palliation)\b",
    re.I,
)
EPIDEMIOLOGY = re.compile(
    r"\b(case-control|cohort|odds ratio|risk factor|association|birth|infant|maternal|pregnan|registry)\b",
    re.I,
)


def species_in(text: str) -> set[str]:
    return {name for name, pattern in SPECIES_PATTERNS.items() if re.search(pattern, text, re.I)}


def triage(row: dict[str, Any], abstract: str) -> tuple[str, str]:
    title = row.get("title", "") or ""
    text = f"{title}. {abstract}"
    exposures = [e for e in (row.get("candidate_exposures") or "").split(";") if e]
    phenotypes = [p for p in (row.get("candidate_phenotypes") or "").split(";") if p]
    exposure_present = any(
        e in EXPOSURE_PATTERNS and re.search(EXPOSURE_PATTERNS[e], abstract, re.I)
        for e in exposures
    )
    phenotype_present = any(
        re.search(pluralise(PHENOTYPE_PATTERNS_ALL[p]), abstract, re.I)
        for p in phenotypes if p in PHENOTYPE_PATTERNS_ALL
    )
    species = species_in(text)
    human = "human" in species
    animal_or_cell = bool(species & {"mouse", "rat", "zebrafish", "chick", "xenopus", "cell", "organoid"})
    has_effect = any(iter_effects(clause) for clause in split_clauses(abstract))
    has_assoc = bool(ASSOCIATION.search(abstract))

    if re.search(r"\b(review|meta-analys|systematic review)\b", title, re.I) or re.search(
        r"\bmeta-analys|systematic review\b", abstract, re.I
    ):
        return "synthesis", "review or meta-analysis"
    if animal_or_cell and not human:
        return "experimental", "animal or cell study without human epidemiological signals"
    if CLINICAL_TITLE.search(title) and not re.search(
        r"risk|exposure|associat|epidemiolog", title, re.I
    ):
        return "clinical", "title indicates surgical, diagnostic or device study"
    if not (exposure_present and phenotype_present):
        if human:
            return "human_unconfirmed", "human study; candidate exposure or phenotype not confirmed in the abstract"
        return "unclassified", "candidate exposure or phenotype not confirmed in the abstract"
    if has_effect:
        return "human_numeric", "explicit effect size with candidate exposure and phenotype in the abstract"
    if has_assoc:
        return "human_qualitative", "association language without an explicit numeric estimate"
    if human:
        return "human_no_effect", "human study without association language in the abstract"
    return "unclassified", "no species, design or effect signal"


def main() -> None:
    queue = read_csv(QUEUE)
    pending = [row for row in queue if row.get("status") != "approved"]
    reviews = batch_review.load_reviews(REVIEW)
    decided_pmids = {key[0] for key in reviews}
    studies = {s.pmid: s for s in efetch(sorted({row["pmid"] for row in pending}))}

    rows = []
    for row in pending:
        if row["pmid"] in decided_pmids:
            rows.append({
                "pmid": row["pmid"], "title": row.get("title", ""), "year": row.get("year", ""),
                "journal": row.get("journal", ""),
                "candidate_exposures": row.get("candidate_exposures", ""),
                "candidate_phenotypes": row.get("candidate_phenotypes", ""),
                "triage_class": "reviewed", "triage_reason": "review entry already exists",
                "has_effect_size": "", "has_association_language": "",
            })
            continue
        study = studies.get(row["pmid"])
        abstract = (study.abstract if study else "") or ""
        if not abstract:
            rows.append({
                "pmid": row["pmid"], "title": row.get("title", ""), "year": row.get("year", ""),
                "journal": row.get("journal", ""),
                "candidate_exposures": row.get("candidate_exposures", ""),
                "candidate_phenotypes": row.get("candidate_phenotypes", ""),
                "triage_class": "no_abstract", "triage_reason": "PubMed abstract not available",
                "has_effect_size": "", "has_association_language": "",
            })
            continue
        cls, reason = triage(row, abstract)
        rows.append({
            "pmid": row["pmid"], "title": row.get("title", ""), "year": row.get("year", ""),
            "journal": row.get("journal", ""),
            "candidate_exposures": row.get("candidate_exposures", ""),
            "candidate_phenotypes": row.get("candidate_phenotypes", ""),
            "triage_class": cls, "triage_reason": reason,
            "has_effect_size": str(any(iter_effects(clause) for clause in split_clauses(abstract))),
            "has_association_language": str(bool(ASSOCIATION.search(abstract))),
        })

    rows.sort(key=lambda r: (r["triage_class"], r["pmid"]))
    write_csv(OUT, rows, fieldnames=FIELDS)
    counts = Counter(r["triage_class"] for r in rows)

    lines = [
        "# Triagem da fila de curadoria em lote",
        "",
        f"Gerado: {today()}",
        "",
        "Esta triagem **não altera evidências**. Ela apenas prioriza a leitura humana",
        "dos registros que a regra estrita não promoveu. A classe é heurística e o",
        "motivo está na coluna `triage_reason` do CSV.",
        "",
        "| Classe | Registros | O que significa |",
        "|---|---:|---|",
        "| human_numeric | {human_numeric} | estudo humano com tamanho de efeito explícito |",
        "| human_qualitative | {human_qualitative} | estudo humano com associação descrita sem número |",
        "| human_no_effect | {human_no_effect} | estudo humano sem linguagem de associação no resumo |",
        "| human_unconfirmed | {human_unconfirmed} | estudo humano; exposição ou fenótipo candidato não confirmado no resumo |",
        "| synthesis | {synthesis} | revisão ou meta-análise |",
        "| experimental | {experimental} | estudo animal ou celular |",
        "| clinical | {clinical} | estudo cirúrgico, diagnóstico ou de dispositivo |",
        "| unclassified | {unclassified} | sem sinal suficiente para classificar |",
        "| no_abstract | {no_abstract} | resumo indisponível no PubMed |",
        "| reviewed | {reviewed} | já possui decisão de revisão |",
        "",
    ]
    full = {cls: counts.get(cls, 0) for cls in [
        "human_numeric", "human_qualitative", "human_no_effect", "human_unconfirmed",
        "synthesis", "experimental", "clinical", "unclassified", "no_abstract", "reviewed",
    ]}
    lines = [line.format(**full) for line in lines]

    priority = ["human_numeric", "human_qualitative"]
    for cls in priority:
        subset = [r for r in rows if r["triage_class"] == cls]
        if not subset:
            continue
        lines += [f"## {cls} ({len(subset)})", ""]
        lines += ["| PMID | Título | Exposições candidatas | Fenótipos candidatos |", "|---|---|---|---|"]
        for row in subset:
            title = (row["title"] or "").replace("|", "/")[:120]
            lines.append(
                f"| {row['pmid']} | {title} | {row['candidate_exposures']} | {row['candidate_phenotypes']} |"
            )
        lines.append("")

    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"triage rows: {len(rows)}")
    for cls, count in counts.most_common():
        print(f"  {cls}: {count}")
    print(f"written {OUT}")
    print(f"written {REPORT}")


if __name__ == "__main__":
    main()
