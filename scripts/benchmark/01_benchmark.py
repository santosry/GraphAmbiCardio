"""Benchmarks for the graph pipeline and query layer.

Measures wall-clock time and peak RSS for the operations used by the Shiny
application and by the network analyses. Results are descriptive for this
machine; they are not a performance guarantee.
"""

from __future__ import annotations

import json
import platform
import time
import tracemalloc
from pathlib import Path

import pandas as pd
import psutil

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reports"
OUT.mkdir(exist_ok=True)

import sys

sys.path.insert(0, str(ROOT / "src"))
from graphambicardio.graph import analysis  # noqa: E402


def timed(label, fn):
    t0 = time.perf_counter()
    value = fn()
    dt = time.perf_counter() - t0
    return {"operation": label, "seconds": round(dt, 4), "result": value}


def main() -> None:
    proc = psutil.Process()
    rss0 = proc.memory_info().rss / 1e6
    tracemalloc.start()
    results = []

    results.append(timed("read_nodes", lambda: len(pd.read_csv(ROOT / "outputs/graph/nodes.csv"))))
    results.append(timed("read_relations", lambda: len(pd.read_csv(ROOT / "outputs/graph/relations.csv"))))
    results.append(timed("read_evidence", lambda: len(pd.read_csv(ROOT / "outputs/graph/evidence.csv"))))

    nodes, relations = analysis.load_layers()
    results.append(timed("load_layers", lambda: [len(nodes), len(relations)]))

    G = analysis.build_digraph(relations, nodes, allowed_layers={"observed", "structured", "inferred"})
    results.append(timed("build_digraph", lambda: [G.number_of_nodes(), G.number_of_edges()]))

    cg = analysis.build_digraph(relations, nodes, allowed_layers={"observed", "inferred"},
                                allowed_types=analysis.CONCEPTUAL_TYPES)
    paths = analysis.conceptual_paths(cg)
    results.append(timed("conceptual_paths", lambda: len(paths)))

    node_type = {n["node_id"]: n["type"] for n in nodes}
    Gc = G.copy()
    Gc.remove_nodes_from([n for n, t in node_type.items() if t == "Variant"])
    results.append(timed("centrality_table", lambda: len(analysis.centrality_table(Gc, node_type))))

    # 1000 random node lookups (app query path)
    ids = list(G.nodes)
    import random
    random.seed(1)
    sample = [random.choice(ids) for _ in range(1000)]
    results.append(timed("1000_node_lookups", lambda: sum(1 for i in sample if i in G)))

    current, peak = tracemalloc.get_traced_memory()
    rss1 = proc.memory_info().rss / 1e6
    payload = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "rss_start_mb": round(rss0, 1),
        "rss_end_mb": round(rss1, 1),
        "rss_delta_mb": round(rss1 - rss0, 1),
        "tracemalloc_peak_mb": round(peak / 1e6, 2),
        "results": results,
    }
    (OUT / "benchmark.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = ["# Benchmark — pipeline e consultas", "", f"Gerado: {payload['generated_at']}", "",
             f"- Python: {payload['python']}", f"- Plataforma: {payload['platform']}",
             f"- RSS: {payload['rss_start_mb']} → {payload['rss_end_mb']} MB (Δ {payload['rss_delta_mb']} MB)",
             f"- Pico tracemalloc: {payload['tracemalloc_peak_mb']} MB", "",
             "| Operação | Tempo (s) | Resultado |", "|---|---:|---|"]
    for r in results:
        lines.append(f"| {r['operation']} | {r['seconds']} | {r['result']} |")
    lines += ["", "Tempos descritivos para esta máquina; não são garantia de desempenho."]
    (OUT / "benchmark.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(payload, indent=2)[:2000])


if __name__ == "__main__":
    main()
