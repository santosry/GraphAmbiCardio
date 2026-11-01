"""Build the full-text metadata table and reading log.

The complete articles are not kept. This script reads the metadata CSV and the
review CSV and writes a human-readable table with one row per study, plus totals
by access type and batch.

Usage:
    .venv/Scripts/python.exe scripts/curation/06_fulltext_report.py
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
METADATA = ROOT / "literature" / "curated" / "fulltext_metadata.csv"
REVIEW = ROOT / "literature" / "curated" / "batch_chd_review.csv"
OUT = ROOT / "reports" / "fulltext_reading_log.md"


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    rows = read_csv(METADATA)
    reviews = read_csv(REVIEW)
    counts: dict[str, Counter] = {}
    fulltext_counts: dict[str, Counter] = {}
    for row in reviews:
        pmid = row.get("pmid", "")
        entry = counts.setdefault(pmid, Counter())
        if row.get("review_status") == "verified":
            entry["verified"] += 1
        elif row.get("review_status") == "rejected":
            entry["rejected"] += 1
        if row.get("review_archive"):
            ft = fulltext_counts.setdefault(pmid, Counter())
            if row.get("review_status") == "verified":
                ft["verified"] += 1

    access = Counter(row.get("access", "") for row in rows)
    full_text = access.get("pdf", 0) + access.get("xml", 0)
    candidates = sum(int(row.get("candidate_count") or 0) for row in rows)
    verified = sum(counter["verified"] for counter in counts.values())
    rejected = sum(counter["rejected"] for counter in counts.values())
    fulltext_verified = sum(counter["verified"] for counter in fulltext_counts.values())

    def batch_key(row: dict[str, str]) -> tuple[int, str]:
        batch = row.get("batch", "")
        return (int(batch) if batch.isdigit() else 9999, row.get("pmid", ""))

    rows.sort(key=batch_key)
    if rows:
        fields = list(rows[0].keys())
        for row in rows:
            counter = counts.get(row.get("pmid", ""), Counter())
            row["reviewed_verified"] = str(counter["verified"])
            row["reviewed_rejected"] = str(counter["rejected"])
        with METADATA.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    lines = [
        "# Leitura integral em lotes",
        "",
        "Os artigos completos são baixados em pasta temporária, convertidos em texto e",
        "apagados depois da extração. Ficam apenas os metadados e trechos curtos com",
        "contexto em `literature/curated/fulltext_quotes/`. Esta tabela é gerada por",
        "`scripts/curation/06_fulltext_report.py`.",
        "",
        "## Resumo",
        "",
        f"- estudos registrados: **{len(rows)}**",
        f"- com texto completo (PDF ou XML): **{full_text}** ({access.get('pdf', 0)} PDF, {access.get('xml', 0)} XML)",
        f"- somente resumo: **{access.get('abstract_only', 0)}**",
        f"- sem resumo: **{access.get('unavailable', 0)}**",
        f"- candidatos extraídos: **{candidates}**",
        f"- linhas de revisão verificadas (resumo ou texto completo): **{verified}**",
        f"- dessas, com citação de texto completo arquivada: **{fulltext_verified}**",
        f"- candidatos recusados: **{rejected}**",
        "",
        "## Estudos",
        "",
        "| PMID | Lote | Acesso | Páginas | Caracteres | Candidatos | Verificados | Recusados | Ano | Título | DOI |",
        "|---|---:|---|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in rows:
        title = (row.get("title") or "").replace("|", "/")[:120]
        counter = counts.get(row.get("pmid", ""), Counter())
        lines.append(
            f"| {row.get('pmid', '')} | {row.get('batch', '')} | {row.get('access', '')} | "
            f"{row.get('n_pages', '')} | {row.get('n_chars', '')} | {row.get('candidate_count', '')} | "
            f"{counter['verified']} | {counter['rejected']} | {row.get('year', '')} | {title} | {row.get('doi', '')} |"
        )
    lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"written {OUT} ({len(rows)} studies)")


if __name__ == "__main__":
    main()
