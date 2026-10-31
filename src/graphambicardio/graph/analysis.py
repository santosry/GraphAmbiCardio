"""Network analyses for the GraphAmbiCardio knowledge graph.

Analyses are deliberately descriptive.  Centrality is reported as a structural
property of the curated graph, not as biological or causal importance.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from itertools import combinations
from typing import Any

import networkx as nx
import pandas as pd

from .. import config
from ..io_utils import get_logger, read_csv, write_csv, write_json

log = get_logger("analysis")

CONCEPTUAL_TYPES = {"Exposure", "Mechanism", "Process", "Phenotype"}


def load_layers() -> tuple[pd.DataFrame, pd.DataFrame]:
    return read_csv(config.GRAPH_OUT / "nodes.csv"), read_csv(config.GRAPH_OUT / "relations.csv")


def build_digraph(
    relations: list[dict[str, Any]],
    nodes: list[dict[str, Any]],
    *,
    allowed_layers: set[str],
    min_confidence: float = 0.0,
    allowed_types: set[str] | None = None,
    exclude_types: set[str] | None = None,
) -> nx.DiGraph:
    node_type = {n["node_id"]: n["type"] for n in nodes}
    best: dict[tuple[str, str], dict[str, Any]] = {}
    for r in relations:
        if r["layer"] not in allowed_layers:
            continue
        if float(r["confidence"]) < min_confidence:
            continue
        su, tv = r["source_id"], r["target_id"]
        if allowed_types is not None and (node_type.get(su) not in allowed_types or node_type.get(tv) not in allowed_types):
            continue
        if exclude_types and (node_type.get(su) in exclude_types or node_type.get(tv) in exclude_types):
            continue
        key = (su, tv)
        if key not in best or float(r["confidence"]) > float(best[key]["confidence"]):
            best[key] = r
    G = nx.DiGraph()
    for (su, tv), r in best.items():
        G.add_edge(su, tv, **r)
    return G


def centrality_table(G: nx.DiGraph, node_type: dict[str, str]) -> list[dict[str, Any]]:
    if G.number_of_nodes() == 0:
        return []
    und = G.to_undirected()
    deg = dict(G.degree())
    indeg = dict(G.in_degree())
    outdeg = dict(G.out_degree())
    btw = nx.betweenness_centrality(und, k=min(200, und.number_of_nodes()), seed=42, normalized=True)
    rows = []
    for n in G.nodes:
        rows.append(
            {
                "node_id": n,
                "node_type": node_type.get(n, ""),
                "degree": deg.get(n, 0),
                "in_degree": indeg.get(n, 0),
                "out_degree": outdeg.get(n, 0),
                "betweenness": round(btw.get(n, 0.0), 6),
            }
        )
    return sorted(rows, key=lambda r: (-r["degree"], -r["betweenness"]))


def communities(G: nx.DiGraph) -> list[dict[str, Any]]:
    und = G.to_undirected()
    if und.number_of_nodes() == 0:
        return []
    comms = nx.community.louvain_communities(und, seed=42, resolution=1.0)
    rows = []
    for i, c in enumerate(sorted(comms, key=len, reverse=True), 1):
        labels = sorted(c)
        rows.append(
            {
                "community": i,
                "size": len(c),
                "members": ";".join(labels[:40]),
                "member_types": ";".join(sorted({x.split(":")[0] for x in labels})),
            }
        )
    return rows


def conceptual_paths(G: nx.DiGraph) -> list[dict[str, Any]]:
    """All simple exposure -> phenotype paths (cutoff 5 nodes) in the conceptual graph."""
    exposures = [n for n, d in G.nodes(data=True) if str(n).startswith("EXP:")]
    phenotypes = [n for n, d in G.nodes(data=True) if str(n).startswith("CHD:")]
    rows = []
    for s in exposures:
        for t in phenotypes:
            if s in G and t in G and nx.has_path(G, s, t):
                for path in nx.all_simple_paths(G, s, t, cutoff=5):
                    confs = [float(G.edges[a, b]["confidence"]) for a, b in zip(path[:-1], path[1:])]
                    layers = [G.edges[a, b]["layer"] for a, b in zip(path[:-1], path[1:])]
                    refs = []
                    for a, b in zip(path[:-1], path[1:]):
                        refs.extend([r for r in str(G.edges[a, b].get("references", "")).split(";") if r])
                    rows.append(
                        {
                            "source": s,
                            "target": t,
                            "path": " -> ".join(path),
                            "n_steps": len(path) - 1,
                            "path_confidence_min": round(min(confs), 3),
                            "path_confidence_mean": round(sum(confs) / len(confs), 3),
                            "layers": ";".join(sorted(set(layers))),
                            "references": ";".join(sorted(set(refs))),
                            "direct": len(path) == 2,
                        }
                    )
    return sorted(rows, key=lambda r: (-r["path_confidence_min"], r["n_steps"]))


def molecular_convergence(relations: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    genes_by_pheno: dict[str, set[str]] = defaultdict(set)
    for r in relations:
        if r["relation"] == "GENE_ASSOCIATED_WITH_PHENOTYPE" and r["layer"] in {"structured", "observed"}:
            genes_by_pheno[r["target_id"]].add(r["source_id"])
    rows = []
    for ph, genes in genes_by_pheno.items():
        rows.append({"phenotype_id": ph, "n_genes": len(genes), "genes": ";".join(sorted(genes)[:50])})
    rows.sort(key=lambda r: -r["n_genes"])
    pairs = []
    for a, b in combinations(sorted(genes_by_pheno), 2):
        ga, gb = genes_by_pheno[a], genes_by_pheno[b]
        if not ga or not gb:
            continue
        inter = ga & gb
        jac = len(inter) / len(ga | gb)
        pairs.append(
            {
                "phenotype_a": a,
                "phenotype_b": b,
                "shared_genes": len(inter),
                "jaccard": round(jac, 4),
                "genes": ";".join(sorted(inter)[:30]),
            }
        )
    pairs.sort(key=lambda r: (-r["shared_genes"], -r["jaccard"]))
    return rows, pairs


def gap_analysis(relations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    exposures = [e["id"] for e in config.EXPOSURES]
    phenotypes = [p["id"] for p in config.PHENOTYPES] + ["CHD:ALL"]
    mechanisms = [m for m, _ in config.MECHANISMS]
    processes = [p for p, _ in config.PROCESSES]

    def has(src: str, dst: str, rel: str) -> bool:
        return any(r["source_id"] == src and r["target_id"] == dst and r["relation"] == rel for r in relations)

    rows = []
    for e in exposures:
        linked = [p for p in phenotypes if has(e, p, "EXPOSURE_ASSOCIATED_WITH_PHENOTYPE")]
        rows.append(
            {
                "entity_type": "Exposure",
                "entity_id": e,
                "n_curated_outgoing": len(linked),
                "linked_to": ";".join(linked),
                "gap_type": "" if linked else "no_retained_exposure_phenotype_evidence",
            }
        )
    for m in mechanisms:
        linked = [p for p in processes if has(m, p, "MECHANISM_INTERFERES_WITH_PROCESS")]
        rows.append(
            {
                "entity_type": "Mechanism",
                "entity_id": m,
                "n_curated_outgoing": len(linked),
                "linked_to": ";".join(linked),
                "gap_type": "" if linked else "no_curated_mechanism_process_edge",
            }
        )
    for p in processes:
        linked = [ph for ph in phenotypes if has(p, ph, "ALTERATION_ASSOCIATED_WITH_PHENOTYPE")]
        rows.append(
            {
                "entity_type": "Process",
                "entity_id": p,
                "n_curated_outgoing": len(linked),
                "linked_to": ";".join(linked),
                "gap_type": "" if linked else "no_curated_process_phenotype_edge",
            }
        )
    return rows


def threshold_sensitivity(
    relations: list[dict[str, Any]], nodes: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    node_type = {n["node_id"]: n["type"] for n in nodes}
    rows = []
    for thr in (0.4, 0.5, 0.55, 0.7, 0.85):
        G = build_digraph(relations, nodes, allowed_layers={"observed", "structured", "inferred"}, min_confidence=thr)
        cg = build_digraph(
            relations, nodes, allowed_layers={"observed", "inferred"}, min_confidence=thr, allowed_types=CONCEPTUAL_TYPES
        )
        paths = conceptual_paths(cg)
        ctab = centrality_table(G, node_type)
        rows.append(
            {
                "threshold": thr,
                "n_edges_all": G.number_of_edges(),
                "n_edges_conceptual": cg.number_of_edges(),
                "n_exposure_phenotype_paths": len(paths),
                "n_direct_pairs": len({(p["source"], p["target"]) for p in paths if p["direct"]}),
                "top5_degree": ";".join(f"{r['node_id']}({r['degree']})" for r in ctab[:5]),
            }
        )
    return rows


def main() -> None:
    nodes, relations = load_layers()
    node_type = {n["node_id"]: n["type"] for n in nodes}

    G = build_digraph(relations, nodes, allowed_layers={"observed", "structured", "inferred"})
    # centrality excluding variants (structural annotation nodes dominate otherwise)
    Gc = G.copy()
    Gc.remove_nodes_from([n for n, t in node_type.items() if t == "Variant"])
    ctab = centrality_table(Gc, node_type)
    write_csv(config.TABLES / "network_centrality.csv", ctab)

    comm = communities(Gc)
    write_csv(config.TABLES / "network_communities.csv", comm)

    cg = build_digraph(
        relations, nodes, allowed_layers={"observed", "inferred"}, allowed_types=CONCEPTUAL_TYPES
    )
    paths = conceptual_paths(cg)
    write_csv(config.TABLES / "paths_exposure_phenotype.csv", paths)

    genes, pairs = molecular_convergence(relations)
    write_csv(config.TABLES / "phenotype_gene_convergence.csv", genes)
    write_csv(config.TABLES / "phenotype_gene_overlap.csv", pairs)

    gaps = gap_analysis(relations)
    write_csv(config.TABLES / "gap_analysis.csv", gaps)

    sens = threshold_sensitivity(relations, nodes)
    write_csv(config.TABLES / "sensitivity_evidence_thresholds.csv", sens)

    summary = {
        "n_nodes": len(nodes),
        "n_relations": len(relations),
        "n_edges_analysis_graph": G.number_of_edges(),
        "n_conceptual_nodes": cg.number_of_nodes(),
        "n_conceptual_edges": cg.number_of_edges(),
        "n_exposure_phenotype_paths": len(paths),
        "n_direct_exposure_phenotype_pairs": len({(p["source"], p["target"]) for p in paths if p["direct"]}),
        "n_gaps": sum(1 for g in gaps if g["gap_type"]),
        "top_degree": ctab[:10],
    }
    write_json(config.REPORTS / "network_analysis_summary.json", summary)
    log.info("analysis complete: %s paths, %s gaps", len(paths), summary["n_gaps"])


if __name__ == "__main__":
    main()
