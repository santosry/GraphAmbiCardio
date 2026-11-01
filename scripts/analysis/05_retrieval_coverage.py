"""Build a transparent register of what each literature source retrieved and screened.

This does not change the evidence graph. It records, per search:

* total hits reported by the source;
* how many records were retrieved (top-N vs all pages);
* how many were triaged automatically;
* whether each retrieved record became an anchor, was included/excluded in the
  CAPES manual triage, or was only automatically triaged.

Outputs
-------
reports/retrieval_coverage.csv
reports/retrieval_coverage.md
literature/screening/all_records_triage.csv
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from graphambicardio.io_utils import read_csv, write_csv  # noqa: E402
from graphambicardio.literature.screen import screen_record  # noqa: E402

SEARCHES = ROOT / "literature" / "searches"
CURATED = ROOT / "literature" / "curated"
SCREENING = ROOT / "literature" / "screening"
REPORTS = ROOT / "reports"

CAPES_TRIAGE = {
    row["capes_id"]: row
    for row in read_csv(SCREENING / "capes_triage.csv")
    if row.get("capes_id")
}

ANCHORS = read_csv(CURATED / "anchor_studies.csv")
ANCHOR_PMIDS = {str(r.get("pmid", "")).strip() for r in ANCHORS if str(r.get("pmid", "")).strip()}
ANCHOR_REFERENCES = {str(r.get("reference", "")).strip() for r in ANCHORS if str(r.get("reference", "")).strip()}


def source_and_cap(name: str) -> tuple[str, str, str]:
    if name.startswith("capes_"):
        return "CAPES Teses", "all_pages", "all"
    if name.startswith("scielo_"):
        return "SciELO (Crossref 10.1590)", "top_n", "100/query"
    if name.endswith("_europepmc.json"):
        return "Europe PMC", "top_n", "100/domain"
    if name.startswith("pair_"):
        return "PubMed (pares)", "top_n", "15/pair"
    return "PubMed (domínios)", "top_n", "100/domain"


def iter_records(path: Path) -> tuple[str, str, int, list[dict[str, Any]]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    name = path.name
    if name.startswith("capes_"):
        items = data.get("items", [])
        recs = [
            {
                "record_id": str(it.get("id", "")),
                "pmid": "",
                "doi": "",
                "title": it.get("titulo", ""),
                "abstract": "",
                "journal": it.get("instituicao", ""),
                "year": str(it.get("dataDefesa", ""))[:4],
                "first_author": it.get("autor", ""),
                "pubtypes": it.get("grauAcademico", ""),
                "mesh_terms": "",
            }
            for it in items
        ]
        return str(data.get("query", "")), str(data.get("total", "")), len(recs), recs
    if name.startswith("scielo_"):
        items = data.get("items", [])
        recs = [
            {
                "record_id": it.get("doi", ""),
                "pmid": "",
                "doi": it.get("doi", ""),
                "title": it.get("title", ""),
                "abstract": it.get("abstract", ""),
                "journal": it.get("journal", ""),
                "year": str(it.get("year", "")),
                "first_author": it.get("authors", ""),
                "pubtypes": "",
                "mesh_terms": "",
            }
            for it in items
        ]
        return str(data.get("query", "")), str(data.get("total_results", "")), len(recs), recs
    items = data.get("studies", [])
    recs = [
        {
            "record_id": str(it.get("pmid", "") or it.get("doi", "") or it.get("title", "")),
            "pmid": str(it.get("pmid", "")),
            "doi": str(it.get("doi", "")),
            "title": it.get("title", ""),
            "abstract": it.get("abstract", ""),
            "journal": it.get("journal", ""),
            "year": str(it.get("year", "")),
            "first_author": it.get("first_author", ""),
            "pubtypes": it.get("pubtypes", ""),
            "mesh_terms": it.get("mesh_terms", ""),
        }
        for it in items
    ]
    return str(data.get("query", "")), str(data.get("count_total", "")), len(recs), recs


def main() -> None:
    coverage: list[dict[str, Any]] = []
    register: list[dict[str, Any]] = []

    for path in sorted(SEARCHES.glob("*.json")):
        source, scope, cap = source_and_cap(path.name)
        query, total, n_retrieved, recs = iter_records(path)
        try:
            total_n = int(float(total))
        except (TypeError, ValueError):
            total_n = 0
        coverage.append(
            {
                "search_file": path.name,
                "source": source,
                "query": query,
                "total_hits": total_n,
                "retrieved": n_retrieved,
                "retrieval_scope": scope,
                "retrieval_cap": cap,
                "coverage_fraction": round(n_retrieved / total_n, 4) if total_n else "",
            }
        )
        for rec in recs:
            s = screen_record(rec)
            if source == "CAPES Teses":
                triage = CAPES_TRIAGE.get(rec["record_id"], {})
                status = {
                    "Included": "included",
                    "Excluded": "excluded",
                }.get(triage.get("decision", ""), "triaged_not_selected")
                reason = triage.get("reason", "")
                screening_level = triage.get("screening_level", "")
            else:
                is_anchor = rec["pmid"] in ANCHOR_PMIDS
                status = "anchor" if is_anchor else "triaged_not_selected"
                reason = "usado como estudo-âncora" if is_anchor else "triagem automática; não selecionado como âncora"
                screening_level = "abstract (manual)" if is_anchor else "automated"
            register.append(
                {
                    "source": source,
                    "search_file": path.name,
                    "record_id": rec["record_id"],
                    "pmid": rec["pmid"],
                    "doi": rec["doi"],
                    "title": rec["title"],
                    "year": rec["year"],
                    "has_abstract": bool(rec["abstract"]),
                    "species_human": s["species_human"],
                    "species_animal": s["species_animal"],
                    "species_cell": s["species_cell"],
                    "design": s["design"],
                    "window_terms": s["window_terms"],
                    "mechanisms": s["mechanisms"],
                    "phenotypes": s["phenotypes"],
                    "is_review": s["is_review"],
                    "status": status,
                    "screening_level": screening_level,
                    "reason": reason,
                }
            )

    write_csv(REPORTS / "retrieval_coverage.csv", coverage)
    write_csv(SCREENING / "all_records_triage.csv", register)

    by_source: dict[str, dict[str, int]] = {}
    for row in coverage:
        d = by_source.setdefault(row["source"], {"searches": 0, "hits": 0, "retrieved": 0})
        d["searches"] += 1
        d["hits"] += row["total_hits"]
        d["retrieved"] += row["retrieved"]
    status_counts: dict[str, int] = {}
    for row in register:
        status_counts[row["status"]] = status_counts.get(row["status"], 0) + 1
    unique_anchor_pmids = {r["pmid"] for r in register if r["status"] == "anchor" and r["pmid"]}
    anchor_not_in_topn = ANCHOR_PMIDS - unique_anchor_pmids
    capes_included_ids = {r["record_id"] for r in register if r["status"] == "included"}
    capes_excluded_ids = {r["record_id"] for r in register if r["status"] == "excluded"}

    lines = [
        "# Cobertura de recuperação e triagem por base",
        "",
        "Este relatório separa **o que foi recuperado** de **o que foi usado como evidência**.",
        "A busca é estruturada e não sistemática; a cobertura é assimétrica e declarada.",
        "",
        "| Base | Buscas | Hits totais | Registros recuperados |",
        "|---|---:|---:|---:|",
    ]
    for source, d in sorted(by_source.items()):
        lines.append(f"| {source} | {d['searches']} | {d['hits']:,} | {d['retrieved']:,} |")
    lines += [
        "",
        "## Status dos registros recuperados (inclui repetições entre buscas)",
        "",
        "| Status | Registros |",
        "|---|---:|",
    ]
    for status, n in sorted(status_counts.items()):
        lines.append(f"| {status} | {n:,} |")
    lines += [
        "",
        f"**Estudos-âncora no grafo:** {len(ANCHOR_PMIDS)} PMIDs + {len(capes_included_ids)} tese CAPES = {len(ANCHOR_PMIDS) + len(capes_included_ids)}.",
        f"**Desses, aparecem nos registros top-N recuperados:** {len(unique_anchor_pmids)} PMIDs + {len(capes_included_ids)} tese CAPES. Os outros **{len(anchor_not_in_topn)} PMIDs** foram incluídos por busca dirigida/referências e não estão no top-N.",
        f"**CAPES:** {len(capes_included_ids)} ID incluído, {len(capes_excluded_ids)} IDs excluídos; os 560 registros incluem 8 repetições entre consultas.",
        "",
        "## Política de recuperação",
        "",
        "- **PubMed:** top 100 por domínio e top 15 por par exposição × fenótipo.",
        "- **Europe PMC:** top 100 por domínio.",
        "- **SciELO via Crossref:** top 100 por consulta.",
        "- **CAPES:** todas as páginas (560 registros; 552 IDs únicos), com triagem manual de título e leitura de resumo dos candidatos.",
        "",
        "Os registros recuperados das bases top-N foram triados automaticamente (`src/graphambicardio/literature/screen.py`); apenas uma parte se tornou estudo-âncora. "
        "Além disso, 23 PMIDs-âncora vieram de busca dirigida/referências e não do top-N. "
        "Isso **não** é uma revisão sistemática e não há triagem dupla de todos os hits.",
        "",
        "Arquivos: `reports/retrieval_coverage.csv` e `literature/screening/all_records_triage.csv`.",
    ]
    (REPORTS / "retrieval_coverage.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"coverage: {len(coverage)} searches; register: {len(register)} records")
    for source, d in sorted(by_source.items()):
        print(source, d)


if __name__ == "__main__":
    main()
