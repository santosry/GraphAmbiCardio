"""Exhaustive retrieval and first-pass screening for PubMed, Europe PMC and SciELO.

Unlike the feasibility searches (top-N), this script retrieves **all hits** for
the pre-registered queries. Raw records are written as gzipped JSONL under
``data_raw/literature/full/`` (ignored by Git). Only a compact candidate table
and a coverage/hash summary are versioned.

This is still **not** a systematic review: it performs exhaustive retrieval and
automated triage, not dual manual screening. A retrieved record becomes graph
evidence only after manual curation with a verbatim quote.

Run:
    .venv/Scripts/python.exe scripts/collection/04_exhaustive_literature.py
"""
from __future__ import annotations

import gzip
import hashlib
import json
import re
import sys
import time
from pathlib import Path
from typing import Any

import requests

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from graphambicardio import config  # noqa: E402
from graphambicardio.io_utils import write_csv  # noqa: E402
from graphambicardio.literature.europepmc import to_europepmc_query  # noqa: E402
from graphambicardio.literature.feasibility import pair_query  # noqa: E402
from graphambicardio.literature.pubmed import domain_queries, efetch, esearch  # noqa: E402
from graphambicardio.literature.screen import screen_record  # noqa: E402

RAW = ROOT / "data_raw" / "literature" / "full"
SCREENING = ROOT / "literature" / "screening"
REPORTS = ROOT / "reports"
for d in (RAW, SCREENING, REPORTS):
    d.mkdir(parents=True, exist_ok=True)

USER_AGENT = "GraphAmbiCardio/0.1 (academic research; mailto:ryan.paulo@gsuite.iff.edu.br)"
SCIELO_QUERIES = {
    "scielo_cardiopatia_ambiente": "cardiopatia congênita exposição ambiental",
    "scielo_poluicao_ar": "cardiopatia congênita poluição do ar material particulado",
    "scielo_agrotoxicos": "cardiopatia congênita agrotóxicos pesticidas",
    "scielo_temperatura": "cardiopatia congênita temperatura calor",
    "scielo_umidade": "cardiopatia congênita umidade",
}

EXPOSURE_PATTERNS = {
    "EXP:PM25": r"\bpm\s*2[.,]?5\b|fine particulate|particulate matter.{0,30}(2[.,]?5|fine)",
    "EXP:PM10": r"\bpm\s*10\b|particulate matter",
    "EXP:NO2": r"\bno2\b|nitrogen dioxide|nitrogen oxides|traffic[- ]related",
    "EXP:O3": r"\bo3\b|ozone",
    "EXP:CO": r"carbon monoxide|\bco\b",
    "EXP:HEAT": r"\bheat\b|high temperature|ambient temperature|hot temperature|climate",
    "EXP:HUMIDITY": r"humidity|relative humidity",
    "EXP:PEST": r"pesticid|agrochemical|agricultural chemical|organophosphate",
    "EXP:SOLV": r"solvent",
    "EXP:METALS": r"\bmetal|lead|mercury|arsenic|cadmium",
    "EXP:SMOKE": r"smok|tobacco|cigarette",
    "EXP:ALCOHOL": r"alcohol|ethanol",
    "EXP:VPA": r"valproi|valproate",
    "EXP:DIOXIN": r"dioxin|tcdd|\bpcb",
}


def compact_text(text: str) -> str:
    """Normalise Crossref abstracts that sometimes arrive with spaces between letters."""
    t = re.sub(r"\s+", " ", text or "").strip()
    previous = None
    while previous != t:
        previous = t
        t = re.sub(r"(?<=\b\w) (?=\w\b)", "", t)
    return t


def norm_key(pmid: str = "", doi: str = "", title: str = "") -> str:
    if pmid:
        return "pmid:" + str(pmid)
    if doi:
        return "doi:" + str(doi).lower()
    return "title:" + re.sub(r"[^a-z0-9]", "", (title or "").lower())[:200]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


CANDIDATES: dict[str, dict[str, Any]] = {}


def consider(rec: dict[str, Any], source: str, search_id: str) -> bool:
    rec = {
        **rec,
        "title": compact_text(rec.get("title", "")),
        "abstract": compact_text(rec.get("abstract", "")),
    }
    text = " ".join(str(rec.get(k, "")) for k in ("title", "abstract", "mesh_terms", "pubtypes"))
    exposures = [k for k, pat in EXPOSURE_PATTERNS.items() if re.search(pat, text, flags=re.I)]
    if not exposures:
        return False
    if not rec.get("abstract"):
        return False
    s = screen_record(rec)
    if not (s["species_human"] or s["species_animal"] or s["species_cell"]):
        return False
    heart_context = bool(re.search(r"heart|cardiac|cardiogen|embryo|congenital|septal|fallot|transposition", text, flags=re.I))
    if not heart_context:
        return False
    if not s["phenotypes"] and not s["mechanisms"]:
        return False
    key = norm_key(rec.get("pmid", ""), rec.get("doi", ""), rec.get("title", ""))
    if key not in CANDIDATES:
        CANDIDATES[key] = {
            "candidate_key": key,
            "sources": set(),
            "search_ids": set(),
            "record_id": rec.get("record_id", ""),
            "pmid": rec.get("pmid", ""),
            "doi": rec.get("doi", ""),
            "title": compact_text(rec.get("title", "")),
            "year": rec.get("year", ""),
            "journal": rec.get("journal", ""),
            "first_author": rec.get("first_author", ""),
            "exposures": set(exposures),
            "phenotypes": set(x for x in s["phenotypes"].split(";") if x),
            "mechanisms": set(x for x in s["mechanisms"].split(";") if x),
            "species_human": s["species_human"],
            "species_animal": s["species_animal"],
            "species_cell": s["species_cell"],
            "design": s["design"],
            "window_terms": s["window_terms"],
            "is_review": s["is_review"],
        }
    else:
        CANDIDATES[key]["sources"].add(source)
        CANDIDATES[key]["search_ids"].add(search_id)
    CANDIDATES[key]["sources"].add(source)
    CANDIDATES[key]["search_ids"].add(search_id)
    return True


def write_raw(writer, rec: dict[str, Any]) -> None:
    writer.write(json.dumps(rec, ensure_ascii=False) + "\n")


def run_pubmed_query(search_id: str, query: str, source: str, summary: list[dict[str, Any]]) -> None:
    first = esearch(query, retmax=0)
    total = int(first.get("count", 0))
    pmids: list[str] = []
    for offset in range(0, total, 10000):
        res = esearch(query, retmax=min(10000, total - offset), retstart=offset)
        pmids.extend(res.get("pmids", []))
    pmids = list(dict.fromkeys(pmids))
    path = RAW / f"pubmed_{search_id}.jsonl.gz"
    n_candidates = 0
    with gzip.open(path, "wt", encoding="utf-8") as fh:
        for i in range(0, len(pmids), 200):
            for s in efetch(pmids[i : i + 200]):
                rec = s.as_dict()
                rec.update({"record_id": s.pmid, "source": source, "search_id": search_id})
                write_raw(fh, rec)
                n_candidates += int(consider(rec, source, search_id))
    summary.append(
        {
            "source": source,
            "search_id": search_id,
            "query": query,
            "total_hits": total,
            "retrieved": len(pmids),
            "candidates_before_dedup": n_candidates,
            "retrieval_scope": "all",
            "raw_file": str(path.relative_to(ROOT)),
            "sha256": sha256(path),
        }
    )
    print(f"PubMed {search_id}: {len(pmids)}/{total} retrieved; {n_candidates} candidates", flush=True)


def run_europepmc_query(search_id: str, query: str, source: str, summary: list[dict[str, Any]]) -> None:
    q = to_europepmc_query(query)
    path = RAW / f"europepmc_{search_id}.jsonl.gz"
    cursor = "*"
    total = 0
    n = 0
    n_candidates = 0
    with gzip.open(path, "wt", encoding="utf-8") as fh:
        while True:
            params = {
                "query": q,
                "format": "json",
                "pageSize": 1000,
                "resultType": "core",
                "cursorMark": cursor,
            }
            for attempt in range(4):
                r = requests.get(
                    f"{config.EUROPEPMC_BASE}/search", params=params,
                    headers={"User-Agent": USER_AGENT}, timeout=120,
                )
                if r.status_code == 200:
                    break
                time.sleep(2 ** attempt)
            r.raise_for_status()
            data = r.json()
            total = int(data.get("hitCount", total or 0))
            items = data.get("resultList", {}).get("result", [])
            for it in items:
                rec = {
                    "record_id": it.get("pmid", "") or it.get("doi", "") or it.get("title", ""),
                    "pmid": it.get("pmid", ""),
                    "doi": it.get("doi", ""),
                    "title": it.get("title", ""),
                    "abstract": it.get("abstractText", ""),
                    "journal": it.get("journalTitle", ""),
                    "year": str(it.get("pubYear", "")),
                    "first_author": (it.get("authorString", "") or "").split(",")[0],
                    "pubtypes": ";".join(
                        p.get("name", "") if isinstance(p, dict) else str(p)
                        for p in (it.get("pubTypeList", {}) or {}).get("pubType", [])
                    ),
                    "mesh_terms": ";".join(
                        m.get("descriptorName", "") if isinstance(m, dict) else str(m)
                        for m in (it.get("meshHeadingList", {}) or {}).get("meshHeading", [])
                    ),
                    "source": source,
                    "search_id": search_id,
                }
                write_raw(fh, rec)
                n_candidates += int(consider(rec, source, search_id))
            n += len(items)
            nxt = data.get("nextCursorMark")
            if not items or not nxt or nxt == cursor:
                break
            cursor = nxt
            time.sleep(0.3)
    summary.append(
        {
            "source": source,
            "search_id": search_id,
            "query": query,
            "total_hits": total,
            "retrieved": n,
            "candidates_before_dedup": n_candidates,
            "retrieval_scope": "all",
            "raw_file": str(path.relative_to(ROOT)),
            "sha256": sha256(path),
        }
    )
    print(f"Europe PMC {search_id}: {n}/{total} retrieved; {n_candidates} candidates", flush=True)


def run_scielo_query(search_id: str, query: str, source: str, summary: list[dict[str, Any]]) -> None:
    path = RAW / f"scielo_{search_id}.jsonl.gz"
    cursor = "*"
    total = 0
    n = 0
    n_candidates = 0
    with gzip.open(path, "wt", encoding="utf-8") as fh:
        while True:
            params = {
                "query": query,
                "filter": "prefix:10.1590,from-pub-date:2010-01-01",
                "rows": 1000,
                "cursor": cursor,
                "select": "DOI,title,container-title,issued,author,abstract,URL,type",
                "mailto": "ryan.paulo@gsuite.iff.edu.br",
            }
            for attempt in range(4):
                r = requests.get(
                    "https://api.crossref.org/works", params=params,
                    headers={"User-Agent": USER_AGENT}, timeout=180,
                )
                if r.status_code == 200:
                    break
                time.sleep(2 ** attempt)
            r.raise_for_status()
            data = r.json()["message"]
            total = int(data.get("total-results", total or 0))
            items = data.get("items", [])
            for it in items:
                title = " ".join(it.get("title", []) or [])
                abstract = re.sub(r"<[^>]+>", " ", " ".join(it.get("abstract", []) or []))
                issued = (it.get("issued", {}) or {}).get("date-parts", [[None]])
                year = issued[0][0] if issued and issued[0] else ""
                authors = "; ".join(
                    " ".join(x for x in (a.get("given", ""), a.get("family", "")) if x)
                    for a in (it.get("author", []) or [])
                )
                rec = {
                    "record_id": it.get("DOI", ""),
                    "pmid": "",
                    "doi": it.get("DOI", ""),
                    "title": title,
                    "abstract": abstract,
                    "journal": " ".join(it.get("container-title", []) or []),
                    "year": str(year),
                    "first_author": authors.split(";")[0].strip(),
                    "pubtypes": it.get("type", ""),
                    "mesh_terms": "",
                    "source": source,
                    "search_id": search_id,
                }
                write_raw(fh, rec)
                n_candidates += int(consider(rec, source, search_id))
            n += len(items)
            nxt = data.get("next-cursor")
            if not items or not nxt or nxt == cursor:
                break
            cursor = nxt
            time.sleep(0.5)
    summary.append(
        {
            "source": source,
            "search_id": search_id,
            "query": query,
            "total_hits": total,
            "retrieved": n,
            "candidates_before_dedup": n_candidates,
            "retrieval_scope": "all",
            "raw_file": str(path.relative_to(ROOT)),
            "sha256": sha256(path),
        }
    )
    print(f"SciELO {search_id}: {n}/{total} retrieved; {n_candidates} candidates", flush=True)


def main() -> None:
    summary: list[dict[str, Any]] = []

    for name, q in domain_queries().items():
        run_pubmed_query(name, q, "PubMed/MEDLINE (domínios)", summary)

    for exposure in config.EXPOSURES:
        for phenotype in config.PHENOTYPES:
            sid = f"pair_{exposure['id'].split(':')[1]}_{phenotype['id'].split(':')[1]}"
            q = pair_query(exposure["query_terms"], phenotype)
            run_pubmed_query(sid, q, "PubMed/MEDLINE (pares)", summary)

    for name, q in domain_queries().items():
        run_europepmc_query(name, q, "Europe PMC", summary)

    for name, q in SCIELO_QUERIES.items():
        run_scielo_query(name, q, "SciELO (Crossref 10.1590)", summary)

    write_csv(REPORTS / "exhaustive_retrieval.csv", summary)

    rows = []
    for key, c in sorted(CANDIDATES.items()):
        rows.append(
            {
                **{k: v for k, v in c.items() if k not in {"sources", "search_ids", "exposures", "phenotypes", "mechanisms"}},
                "sources": ";".join(sorted(c["sources"])),
                "search_ids": ";".join(sorted(c["search_ids"])),
                "exposures": ";".join(sorted(c["exposures"])),
                "phenotypes": ";".join(sorted(c["phenotypes"])),
                "mechanisms": ";".join(sorted(c["mechanisms"])),
            }
        )
    write_csv(SCREENING / "exhaustive_candidates.csv", rows)

    by_source: dict[str, dict[str, int]] = {}
    for r in summary:
        d = by_source.setdefault(r["source"], {"searches": 0, "hits": 0, "retrieved": 0, "candidates": 0})
        d["searches"] += 1
        d["hits"] += r["total_hits"]
        d["retrieved"] += r["retrieved"]
        d["candidates"] += r["candidates_before_dedup"]
    lines = [
        "# Recuperação exaustiva por base",
        "",
        "Todos os hits das consultas pré-registradas foram recuperados. Os registros brutos ficam em `data_raw/literature/full/` (não versionado); a tabela de candidatos e o resumo com SHA-256 são versionados.",
        "",
        "| Base | Buscas | Hits totais | Recuperados | Candidatos (antes de dedup) |",
        "|---|---:|---:|---:|---:|",
    ]
    for source, d in sorted(by_source.items()):
        lines.append(f"| {source} | {d['searches']} | {d['hits']:,} | {d['retrieved']:,} | {d['candidates']:,} |")
    lines += [
        "",
        f"Candidatos únicos após deduplicação por PMID/DOI/título: **{len(rows):,}**.",
        "",
        "Critério de candidato: resumo disponível + espécie humana/animal/célula + pelo menos um termo de exposição + fenótipo CHD ou mecanismo com contexto cardíaco/embrionário. "
        "Isso é **triagem automática**, não curadoria: um candidato não é uma aresta de evidência.",
        "",
        "A curadoria manual continua sendo a única porta de entrada para `evidence.csv`; ver `docs/06_EVIDENCE_GRADING.md`.",
    ]
    (REPORTS / "exhaustive_retrieval.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"candidates: {len(rows)}; summary -> reports/exhaustive_retrieval.csv")


if __name__ == "__main__":
    main()
