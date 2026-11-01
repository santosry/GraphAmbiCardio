"""Re-screen the archived exhaustive raw records without re-downloading them.

This is useful after changes to the text normalisation or candidate rules.
It reads data_raw/literature/full/*.jsonl.gz, rebuilds
literature/screening/exhaustive_candidates.csv, updates
reports/exhaustive_retrieval.csv and reports/exhaustive_retrieval.md.
"""
from __future__ import annotations

import gzip
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from graphambicardio.io_utils import read_csv, write_csv  # noqa: E402

MODULE_PATH = ROOT / "scripts" / "collection" / "04_exhaustive_literature.py"
spec = importlib.util.spec_from_file_location("exhaustive_literature", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)

REPORTS = ROOT / "reports"
SCREENING = ROOT / "literature" / "screening"


def candidate_rows() -> list[dict]:
    rows = []
    for key, c in sorted(mod.CANDIDATES.items()):
        rows.append(
            {
                **{
                    k: v
                    for k, v in c.items()
                    if k not in {"sources", "search_ids", "exposures", "phenotypes", "mechanisms"}
                },
                "sources": ";".join(sorted(c["sources"])),
                "search_ids": ";".join(sorted(c["search_ids"])),
                "exposures": ";".join(sorted(c["exposures"])),
                "phenotypes": ";".join(sorted(c["phenotypes"])),
                "mechanisms": ";".join(sorted(c["mechanisms"])),
            }
        )
    return rows


def main() -> None:
    summary = read_csv(REPORTS / "exhaustive_retrieval.csv")
    for row in summary:
        path = ROOT / row["raw_file"]
        n_candidates = 0
        n_records = 0
        with gzip.open(path, "rt", encoding="utf-8") as fh:
            for line in fh:
                rec = json.loads(line)
                n_records += 1
                n_candidates += int(mod.consider(rec, row["source"], row["search_id"]))
        row["retrieved"] = n_records
        row["candidates_before_dedup"] = n_candidates
        print(row["source"], row["search_id"], n_candidates)
    write_csv(REPORTS / "exhaustive_retrieval.csv", summary)

    rows = candidate_rows()
    write_csv(SCREENING / "exhaustive_candidates.csv", rows)

    by_source: dict[str, dict[str, int]] = {}
    for r in summary:
        d = by_source.setdefault(r["source"], {"searches": 0, "hits": 0, "retrieved": 0, "candidates": 0})
        d["searches"] += 1
        d["hits"] += int(r["total_hits"])
        d["retrieved"] += int(r["retrieved"])
        d["candidates"] += int(r["candidates_before_dedup"])
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
    print(f"candidates: {len(rows)}")


if __name__ == "__main__":
    main()
