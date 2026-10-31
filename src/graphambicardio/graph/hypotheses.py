"""Hypothesis-generation layer (explicitly non-evidential).

Two complementary, documented rules are used:

1. **Composition** (already produced in the build script): exposure -> mechanism
   plus mechanism -> process implies a candidate exposure -> process link.
2. **Gene-set overlap** (this module): a canonical gene set for a mechanism is
   intersected with the genes annotated to a phenotype.  A large overlap
   prioritises a candidate exposure -> phenotype hypothesis, but it is **not**
   evidence that the exposure causes the phenotype.

Every candidate records the supporting documented edges, the overlapping genes,
and the missing link that would be required to turn it into a testable
mechanistic chain.  Candidates are written to the hypothesis layer only and are
never used in path or centrality analyses.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

import networkx as nx
import pandas as pd

from .. import config
from ..io_utils import get_logger, read_csv, write_csv, write_json
from . import build

log = get_logger("hypotheses")

# Canonical seed gene sets (biological knowledge, NOT evidence for any exposure).
MECH_GENES = {
    "MECH:OXSTRESS": ["NFE2L2", "KEAP1", "HMOX1", "SOD1", "SOD2", "CAT", "GPX1", "TXN", "TXNRD1", "NQO1"],
    "MECH:INFLAM": ["IL6", "TNF", "IL1B", "CRP", "NFKB1", "NLRP3", "IL10", "CCL2"],
    "MECH:EPIGEN": ["DNMT1", "DNMT3A", "DNMT3B", "HDAC1", "HDAC2", "KMT2A", "EZH2", "TET1", "TET2"],
    "MECH:MITO": ["SIRT3", "PPARGC1A", "TFAM", "NDUFS1", "SDHA", "UQCRC2", "ATP5F1A"],
    "MECH:WNT": ["CTNNB1", "AXIN2", "LEF1", "TCF7L2", "GSK3B", "APC", "RSPO2", "WNT3A"],
    "MECH:AHR": ["AHR", "ARNT", "CYP1A1", "CYP1B1", "AHRR"],
    "MECH:RA_SIGNAL": ["RARA", "RARB", "ALDH1A2", "CYP26A1", "RBP1", "CRABP2"],
    "MECH:HDAC": ["HDAC1", "HDAC2", "HDAC3", "HDAC4", "HDAC5"],
    "MECH:HYPOXIA": ["HIF1A", "EPAS1", "VHL", "EGLN1", "EGLN2"],
    "MECH:NEURAL_CREST": ["SOX10", "PAX3", "SNAI2", "TWIST1", "FOXD3", "TFAP2A", "EDNRB"],
    "MECH:HEATSHOCK": ["HSPA1A", "HSPA1B", "HSP90AA1", "HSF1", "HSPB1"],
    "MECH:APOPTOSIS": ["BAX", "BCL2", "CASP3", "CASP8", "TP53", "BAK1"],
    "MECH:PROLIF": ["CCND1", "CDKN1A", "MYC", "MKI67", "CDK4"],
    "MECH:CELLSIG": ["NOTCH1", "JAG1", "BMP4", "FGF8", "TGFB1", "SMAD4"],
    "MECH:GENE_EXPR": ["GATA4", "NKX2-5", "TBX5", "MEF2C", "HAND2", "TBX20"],
    "MECH:ENDOTHELIAL": ["VEGFA", "FLT4", "KDR", "PECAM1", "CDH5"],
}

MIN_OVERLAP = 2
MAX_CANDIDATES = 40


def _phenotype_genes() -> dict[str, set[str]]:
    genes: dict[str, set[str]] = defaultdict(set)
    path = config.DATA_PROCESSED / "hpo_gene_phenotype_edges.csv"
    if path.exists():
        for r in read_csv(path):
            genes[r["phenotype_id"]].add(r["gene_symbol"].upper())
    for r in read_csv(config.GRAPH_OUT / "relations.csv"):
        if r["relation"] == "GENE_ASSOCIATED_WITH_PHENOTYPE" and r["target_type"] == "Phenotype":
            genes[r["target_id"]].add(r["source_id"].split(":", 1)[1].upper())
    return genes


def generate() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    relations = read_csv(config.GRAPH_OUT / "relations.csv")
    pheno_genes = _phenotype_genes()
    evidence_rows: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []

    # documented exposure -> mechanism edges (observed only)
    exp_mech: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in relations:
        if r["layer"] == "observed" and r["relation"] == "EXPOSURE_MODULATES_MECHANISM":
            exp_mech[r["source_id"]].append(r)
    direct = {(r["source_id"], r["target_id"]) for r in relations if r["relation"] == "EXPOSURE_ASSOCIATED_WITH_PHENOTYPE"}

    for exp, mech_edges in exp_mech.items():
        for ph, genes in pheno_genes.items():
            if (exp, ph) in direct:
                continue
            best = None
            for mech_edge in mech_edges:
                mech = mech_edge["target_id"]
                seed = {g.upper() for g in MECH_GENES.get(mech, [])}
                if not seed:
                    continue
                overlap = sorted(seed & genes)
                if len(overlap) < MIN_OVERLAP:
                    continue
                score = len(overlap) / max(1, len(seed))
                if best is None or score > best["score"]:
                    best = {
                        "mechanism": mech,
                        "overlap": overlap,
                        "score": score,
                        "mechanism_edge": mech_edge,
                    }
            if best is None:
                continue
            candidates.append({
                "exposure_id": exp,
                "phenotype_id": ph,
                "mechanism_id": best["mechanism"],
                "n_overlap": len(best["overlap"]),
                "gene_set_fraction": round(best["score"], 3),
                "overlap_genes": ";".join(best["overlap"][:20]),
                "supporting_reference": best["mechanism_edge"].get("references", ""),
                "priority": "alta" if len(best["overlap"]) >= 4 else ("média" if len(best["overlap"]) == 3 else "baixa"),
                "missing_link": f"Nenhuma aresta documentada de {best['mechanism']} para um processo/fenótipo específico; a sobreposição gênica é apenas priorização.",
            })

    candidates.sort(key=lambda c: (-c["n_overlap"], -c["gene_set_fraction"]))
    candidates = candidates[:MAX_CANDIDATES]

    for c in candidates:
        ev = build.make_evidence(
            c["exposure_id"], "Exposure", c["phenotype_id"], "Phenotype",
            "HYPOTHESIS_CANDIDATE",
            layer="hypothesis",
            evidence_type="hypothesis",
            study_design="in_silico",
            species="",
            population_or_model="gene-set overlap with HPO phenotype annotations",
            context=f"mechanism={c['mechanism_id']}; overlap={c['n_overlap']} genes ({c['gene_set_fraction']:.2f} of the seed set)",
            reference="GraphAmbiCardio gene-overlap rule",
            reference_type="rule",
            source_database="GraphAmbiCardio",
            notes=c["missing_link"] + f" Supporting documented edge references: {c['supporting_reference']}",
        )
        evidence_rows.append(ev)

    # candidate paths that reach a process but lack a process -> phenotype edge
    observed = [r for r in relations if r["layer"] == "observed"]
    G = nx.DiGraph()
    for r in observed:
        if r["source_type"] in {"Exposure", "Mechanism", "Process", "Phenotype"} and r["target_type"] in {"Exposure", "Mechanism", "Process", "Phenotype"}:
            G.add_edge(r["source_id"], r["target_id"], **r)
    has_pheno = {e["source_id"] for e in observed if e["relation"] == "ALTERATION_ASSOCIATED_WITH_PHENOTYPE"}
    path_rows = []
    for exp in [e["id"] for e in config.EXPOSURES]:
        if exp not in G:
            continue
        for proc in [p for p, _ in config.PROCESSES]:
            if proc not in G or proc in has_pheno:
                continue
            if nx.has_path(G, exp, proc):
                for path in nx.all_simple_paths(G, exp, proc, cutoff=5):
                    path_rows.append({
                        "exposure_id": exp,
                        "process_id": proc,
                        "path": " -> ".join(path),
                        "n_steps": len(path) - 1,
                        "missing_link": f"{proc} -> fenótipo específico (não demonstrado)",
                    })
    write_csv(config.GRAPH_OUT / "hypotheses.csv", evidence_rows, fieldnames=build.EVIDENCE_FIELDS)
    write_csv(config.TABLES / "hypothesis_candidates.csv", candidates)
    write_csv(config.TABLES / "candidate_paths_missing_link.csv", path_rows)
    write_json(config.REPORTS / "hypothesis_summary.json", {
        "n_candidates": len(candidates),
        "n_candidate_paths": len(path_rows),
        "rule": "gene-set overlap >= 5 genes between a canonical mechanism set and HPO phenotype genes; composition of observed edges for candidate paths",
        "warning": "Hypotheses are not evidence. They are excluded from all path and centrality analyses.",
    })
    log.info("hypothesis candidates: %s; candidate paths with missing link: %s", len(candidates), len(path_rows))
    return evidence_rows, candidates, path_rows
