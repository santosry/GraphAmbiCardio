"""Read full texts in batches of ten, archive metadata and short quotes, and
delete the downloaded files.

The complete article is never kept. A batch produces:

* one row per study in ``literature/curated/fulltext_metadata.csv``;
* short quotation archives in ``literature/curated/fulltext_quotes/``;
* a review packet in ``reports/fulltext_batch_XX.md``;
* a summary in ``reports/fulltext_reading_log.md``.

Usage:
    .venv/Scripts/python.exe scripts/curation/05_read_fulltext_batch.py --source anchors --batch 1
    .venv/Scripts/python.exe scripts/curation/05_read_fulltext_batch.py --source queue --class human_numeric --batch 1
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path

import requests
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from graphambicardio import config  # noqa: E402
from graphambicardio.curation import fulltext  # noqa: E402
from graphambicardio.io_utils import read_csv, today, write_csv  # noqa: E402
from graphambicardio.literature.pubmed import efetch  # noqa: E402

ANCHORS = ROOT / "literature" / "curated" / "anchor_studies.csv"
QUEUE = ROOT / "literature" / "curated" / "batch_chd_queue.csv"
TRIAGE = ROOT / "literature" / "curated" / "batch_chd_triage.csv"
REVIEW = ROOT / "literature" / "curated" / "batch_chd_review.csv"
METADATA = ROOT / "literature" / "curated" / "fulltext_metadata.csv"
ARCHIVE = ROOT / "literature" / "curated" / "fulltext_quotes"
CACHE = ROOT / "data_raw" / "anchor_fulltext"
REPORTS = ROOT / "reports"

FIELDS = [
    "batch", "source", "pmid", "pmcid", "doi", "title", "authors", "journal",
    "year", "volume", "issue", "pages", "license", "oa_status", "access",
    "source_url", "retrieved_at", "pdf_sha256", "n_pages", "n_chars",
    "sections", "candidate_count", "reviewed_verified", "reviewed_rejected",
    "status", "notes",
]

ALL_EXPOSURES = [e["id"] for e in config.EXPOSURES]
ALL_PHENOTYPES = [p["id"] for p in config.PHENOTYPES]


def cached_files() -> dict[str, dict[str, Path]]:
    out: dict[str, dict[str, Path]] = {}
    manifest = CACHE / "manifest.csv"
    if not manifest.exists():
        return out
    for row in csv.DictReader(manifest.open(encoding="utf-8")):
        pmid = (row.get("pmid") or "").strip()
        if not pmid:
            continue
        entry = {}
        for key, field in (("pdf", "pdf_file"), ("xml", "xml_file")):
            name = row.get(field, "")
            if name and (CACHE / name).exists():
                entry[key] = CACHE / name
        if entry:
            out[pmid] = entry
    return out


def processed_pmids() -> set[str]:
    if not METADATA.exists():
        return set()
    return {row["pmid"] for row in read_csv(METADATA) if row.get("pmid")}


def select_anchors(size: int, batch: int, force: bool) -> list[dict[str, str]]:
    rows = [row for row in read_csv(ANCHORS) if (row.get("pmid") or "").strip()]
    done = set() if force else processed_pmids()
    remaining = [row for row in rows if row["pmid"] not in done]
    # The batch number is a label; each run advances over the first unprocessed
    # studies, so batches can be executed in sequence without recomputing offsets.
    return remaining[:size]


def select_queue(size: int, batch: int, triage_class: str, force: bool) -> list[dict[str, str]]:
    triage = {row["pmid"]: row for row in read_csv(TRIAGE)} if TRIAGE.exists() else {}
    queue = {row["pmid"]: row for row in read_csv(QUEUE) if row.get("status") != "approved"}
    done = set() if force else processed_pmids()
    reviewed = {row["pmid"] for row in read_csv(REVIEW)} if REVIEW.exists() else set()
    selected = [
        row for pmid, row in queue.items()
        if pmid not in done and pmid not in reviewed
        and (not triage_class or triage.get(pmid, {}).get("triage_class") == triage_class)
    ]
    selected.sort(key=lambda row: (triage.get(row["pmid"], {}).get("triage_class", ""), row["pmid"]))
    return selected[:size]


def existing_abstract(pmid: str) -> str:
    try:
        studies = efetch([pmid])
        return (studies[0].abstract or "") if studies else ""
    except Exception:
        return ""


def review_counts() -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = {}
    if not REVIEW.exists():
        return counts
    for row in read_csv(REVIEW):
        archive = Path(row.get("review_archive", "") or "").name
        if not archive:
            continue
        pmid = archive.split("_")[0]
        entry = counts.setdefault(pmid, {"verified": 0, "rejected": 0})
        if row.get("review_status") == "verified":
            entry["verified"] += 1
        elif row.get("review_status") == "rejected":
            entry["rejected"] += 1
    return counts


def upsert_metadata(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    existing = read_csv(METADATA) if METADATA.exists() else []
    by_key = {row["pmid"]: row for row in existing}
    for row in rows:
        by_key[row["pmid"]] = row
    merged = sorted(by_key.values(), key=lambda row: (row.get("batch", ""), row.get("pmid", "")))
    write_csv(METADATA, merged, fieldnames=FIELDS)
    return merged


def write_log(batch: int, source: str, rows: list[dict[str, Any]], audit: dict[str, Any]) -> None:
    all_rows = read_csv(METADATA) if METADATA.exists() else []
    lines = [
        "# Leitura integral em lotes",
        "",
        f"Atualizado: {today()}",
        "",
        "Os PDFs e XMLs completos são baixados em pasta temporária, convertidos em texto",
        "e apagados depois da extração. Ficam apenas os metadados e trechos curtos com",
        "contexto em `literature/curated/fulltext_quotes/`. A tabela completa está em",
        "`literature/curated/fulltext_metadata.csv`.",
        "",
        f"## Lote {batch} ({source})",
        "",
        f"- estudos no lote: **{len(rows)}**",
        f"- com texto completo: **{sum(1 for r in rows if r['access'] in {'pdf', 'xml'})}**",
        f"- só com resumo: **{sum(1 for r in rows if r['access'] == 'abstract_only')}**",
        f"- candidatos extraídos: **{sum(int(r['candidate_count']) for r in rows)}**",
        f"- bytes temporários baixados e apagados: **{audit.get('bytes', 0)}**",
        "",
        "| PMID | Título | Acesso | Páginas | Caracteres | Candidatos | Verificados | Recusados |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        title = (row["title"] or "").replace("|", "/")[:110]
        lines.append(
            f"| {row['pmid']} | {title} | {row['access']} | {row['n_pages']} | "
            f"{row['n_chars']} | {row['candidate_count']} | {row['reviewed_verified']} | {row['reviewed_rejected']} |"
        )
    lines += ["", "## Histórico", "", "| Lote | Fonte | Estudos | Texto completo | Candidatos |", "|---|---|---:|---:|---:|"]
    by_batch: dict[str, list[dict[str, Any]]] = {}
    for row in all_rows:
        by_batch.setdefault(row.get("batch", ""), []).append(row)
    for key in sorted(by_batch):
        subset = by_batch[key]
        full = sum(1 for r in subset if r["access"] in {"pdf", "xml"})
        lines.append(
            f"| {key} | {subset[0].get('source', '')} | {len(subset)} | {full} | "
            f"{sum(int(r['candidate_count']) for r in subset)} |"
        )
    lines.append("")
    (REPORTS / "fulltext_reading_log.md").write_text("\n".join(lines), encoding="utf-8")


def write_packet(batch: int, results: list[dict[str, Any]]) -> None:
    lines = [
        f"# Full-text candidate packet, batch {batch}",
        "",
        f"Generated: {today()}",
        "",
        "These are candidate sentences extracted from full text. They are **not**",
        "evidence until a review row is written. The complete article was deleted;",
        "the archived quotation and context are in `literature/curated/fulltext_quotes/`.",
        "",
    ]
    for result in results:
        row = result["metadata"]
        lines += [
            f"## PMID {row['pmid']}: {row['title']}",
            "",
            f"- Access: **{row['access']}** ({row['n_pages']} pages, {row['n_chars']} characters)",
            f"- Journal: {row['journal']} ({row['year']})",
            f"- DOI: {row['doi']}",
            f"- Source: {row['source_url']}",
            "",
        ]
        for candidate in result["candidates"]:
            lines += [
                f"### {candidate['exposure_id']} -> {candidate['phenotype_id']}",
                "",
                f"- Page {candidate['page']}, section `{candidate['section']}`",
                f"- Effect: `{candidate['effect']}`",
                f"- Rule: {candidate['rule']}",
                f"- Archive: `{candidate['archive']}`",
                "",
                f"> {candidate['quote']}",
                "",
            ]
    (REPORTS / f"fulltext_batch_{batch:02d}.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", choices=["anchors", "queue"], default="anchors")
    parser.add_argument("--batch", type=int, default=1)
    parser.add_argument("--size", type=int, default=10)
    parser.add_argument("--class", dest="triage_class", default="human_numeric")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--max-bytes", type=int, default=30_000_000)
    parser.add_argument("--max-pages", type=int, default=80)
    args = parser.parse_args()

    if args.source == "anchors":
        selected = select_anchors(args.size, args.batch, args.force)
    else:
        selected = select_queue(args.size, args.batch, args.triage_class, args.force)
    if not selected:
        print("no studies left for this selection")
        return

    cache = cached_files()
    counts = review_counts()
    temp = fulltext.temporary_directory()
    results: list[dict[str, Any]] = []
    audit = {"bytes": 0}
    try:
        for index, row in enumerate(selected, start=1):
            pmid = row["pmid"]
            if args.source == "anchors":
                anchor = row
                queue_row = {}
                exposures = ALL_EXPOSURES
            else:
                queue_row = row
                anchor = {}
                # Use the full exposure vocabulary: a full-text paper may study a
                # pollutant or behaviour that the screening did not assign.
                exposures = ALL_EXPOSURES
            record = fulltext.fetch_record(pmid)
            if not record.title:
                record.title = row.get("title", "")
            if not record.journal:
                record.journal = row.get("journal", "")
            if not record.year:
                record.year = row.get("year", "")
            if not record.doi:
                record.doi = row.get("doi", "")

            file_path: Path | None = None
            access = "abstract_only"
            source_url = record.pubmed_url
            pdf_sha = ""
            pages: list[str] = []
            notes = ""
            cached = cache.get(pmid, {})
            if "pdf" in cached:
                file_path = cached["pdf"]
                access = "pdf"
                source_url = record.pubmed_url
                audit["bytes"] += file_path.stat().st_size
            elif "xml" in cached:
                file_path = cached["xml"]
                access = "xml"
                source_url = record.pubmed_url
                audit["bytes"] += file_path.stat().st_size
            else:
                dest = temp / f"{pmid}.pdf"
                urls = fulltext.pdf_candidates(record)
                ok, used = fulltext.download_pdf(urls, dest, max_bytes=args.max_bytes)
                if ok:
                    file_path = dest
                    access = "pdf"
                    source_url = used
                    audit["bytes"] += dest.stat().st_size
                else:
                    if record.xml_url:
                        try:
                            response = requests.get(record.xml_url, headers=fulltext.HEADERS, timeout=90)
                            if response.status_code == 200 and response.content.lstrip().startswith(b"<"):
                                dest = temp / f"{pmid}.xml"
                                dest.write_bytes(response.content)
                                file_path = dest
                                access = "xml"
                                source_url = record.xml_url
                                audit["bytes"] += dest.stat().st_size
                        except Exception:
                            pass

            if file_path and access == "pdf":
                pages, error = fulltext.extract_pdf(file_path, max_pages=args.max_pages)
                if error:
                    notes = f"pdf extraction error: {error}"
                pdf_sha = fulltext.sha256_bytes(file_path.read_bytes())
            elif file_path and access == "xml":
                pages = fulltext.extract_jats(file_path.read_bytes())
                pdf_sha = fulltext.sha256_bytes(file_path.read_bytes())
            n_chars = sum(len(page) for page in pages)
            if access == "pdf" and n_chars < 500:
                access = "pdf_no_text"
                notes = (notes + "; " if notes else "") + "no text layer or extraction failed"
            if not pages:
                abstract = record.abstract or existing_abstract(pmid)
                pages = [abstract] if abstract else []
                n_chars = sum(len(page) for page in pages)
                if abstract:
                    access = "abstract_only"
                else:
                    access = "unavailable"

            candidates = fulltext.candidate_sentences(
                pages, exposures, ALL_PHENOTYPES, max_candidates=15
            ) if pages else []
            archived = []
            for candidate in candidates:
                archive = fulltext.save_quote(
                    ARCHIVE, record, candidate,
                    source_url=source_url,
                    retrieved_at=today(),
                    pdf_sha256=pdf_sha,
                )
                archived.append({**candidate, "archive": archive})

            review = counts.get(pmid, {"verified": 0, "rejected": 0})
            metadata = {
                "batch": str(args.batch),
                "source": args.source,
                "pmid": pmid,
                "pmcid": record.pmcid,
                "doi": record.doi,
                "title": record.title,
                "authors": record.authors,
                "journal": record.journal,
                "year": record.year,
                "volume": record.volume,
                "issue": record.issue,
                "pages": record.pages,
                "license": record.license,
                "oa_status": record.oa_status,
                "access": access,
                "source_url": source_url,
                "retrieved_at": today(),
                "pdf_sha256": pdf_sha,
                "n_pages": str(len(pages)),
                "n_chars": str(n_chars),
                "sections": ",".join(sorted({c["section"] for c in archived})),
                "candidate_count": str(len(archived)),
                "reviewed_verified": str(review["verified"]),
                "reviewed_rejected": str(review["rejected"]),
                "status": "read" if access in {"pdf", "xml"} else access,
                "notes": notes,
            }
            results.append({"metadata": metadata, "candidates": archived})
            print(
                f"{index:02d}/{len(selected)} {pmid} {access} pages={len(pages)} "
                f"chars={n_chars} candidates={len(archived)} {record.title[:70]}",
                flush=True,
            )
            if file_path:
                try:
                    file_path.unlink()
                except OSError:
                    pass
            time.sleep(0.2)
    finally:
        fulltext.cleanup(temp)

    rows = [result["metadata"] for result in results]
    upsert_metadata(rows)
    write_packet(args.batch, results)
    print(f"metadata: {METADATA}")
    print(f"packet: {REPORTS / f'fulltext_batch_{args.batch:02d}.md'}")
    print(f"temporary bytes deleted: {audit['bytes']}")


if __name__ == "__main__":
    main()
