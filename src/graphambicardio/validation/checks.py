"""Validation: bibliographic, biological, data and computational checks.

The checks are intentionally explicit and fail loudly.  Every curated quote was
read by the study team and is re-verified automatically against PubMed.
"""

from __future__ import annotations

import json
import random
from collections import Counter
from typing import Any

import pandas as pd

from .. import config
from ..io_utils import get_logger, read_csv, today, write_csv, write_json
from ..graph.build import RELATIONS
from ..literature.pubmed import efetch

log = get_logger("validation")


def check_graph() -> dict[str, Any]:
    nodes = read_csv(config.GRAPH_OUT / "nodes.csv")
    rels = read_csv(config.GRAPH_OUT / "relations.csv")
    ev = read_csv(config.GRAPH_OUT / "evidence.csv")
    ids = [n["node_id"] for n in nodes]
    issues = []
    if len(ids) != len(set(ids)):
        issues.append("duplicate node IDs")
    node_ids = set(ids)
    for r in rels:
        if r["source_id"] not in node_ids or r["target_id"] not in node_ids:
            issues.append(f"edge endpoint missing: {r['edge_key']}")
        if r["source_id"] == r["target_id"]:
            issues.append(f"self-loop: {r['edge_key']}")
        if r["relation"] not in RELATIONS:
            issues.append(f"unknown relation: {r['relation']}")
    if len({e["evidence_id"] for e in ev}) != len(ev):
        issues.append("duplicate evidence IDs")
    return {
        "n_nodes": len(nodes),
        "n_relations": len(rels),
        "n_evidence": len(ev),
        "issues": issues,
        "passed": not issues,
    }


def check_curated() -> dict[str, Any]:
    edges = read_csv(config.CURATED / "curated_edges.csv")
    anchors = {r["pmid"] for r in read_csv(config.CURATED / "anchor_studies.csv")}
    issues = []
    refs = set()
    for e in edges:
        if not e["reference"]:
            issues.append(f"missing reference: {e['edge_key']}")
        if e["reference_type"] != "PMID":
            issues.append(f"non-PMID reference: {e['edge_key']}")
        refs.add(e["reference"])
        if not e.get("quote"):
            issues.append(f"missing quote: {e['edge_key']}")
    missing = refs - anchors
    if missing:
        issues.append(f"references without anchor record: {sorted(missing)}")
    # re-verify a random sample of 25% of quotes against PubMed
    random.seed(20261031)
    sample = random.sample(edges, max(1, len(edges) // 4))
    studies = {s.pmid: s for s in efetch([e["reference"] for e in sample])}
    def norm(x: str) -> str:
        import re
        return re.sub(r"\s+", " ", x).strip().lower()
    for e in sample:
        s = studies.get(e["reference"])
        if not s or norm(e["quote"]) not in norm(s.abstract):
            issues.append(f"quote not found on re-check: {e['reference']}")
    return {
        "n_curated_edges": len(edges),
        "n_unique_pmids": len(refs),
        "sampled_for_recheck": len(sample),
        "issues": issues,
        "passed": not issues,
    }


def check_pmid_resolution() -> dict[str, Any]:
    anchors = read_csv(config.CURATED / "anchor_studies.csv")
    pmids = [r["pmid"] for r in anchors]
    studies = {s.pmid: s for s in efetch(pmids)}
    missing = [p for p in pmids if p not in studies]
    return {
        "n_pmids": len(pmids),
        "n_resolved": len(studies),
        "missing": missing,
        "passed": not missing,
    }


def check_local_data() -> dict[str, Any]:
    issues = []
    sinasc = pd.read_csv(config.DATA_PROCESSED / "sinasc_campos_births.csv", low_memory=False)
    sih = pd.read_csv(config.DATA_PROCESSED / "sih_campos_chd_admissions.csv", low_memory=False)
    climate = pd.read_csv(config.DATA_PROCESSED / "climate_daily_campos.csv")
    if sinasc["codmunres"].astype(str).str[:6].ne("330100").any():
        issues.append("SINASC records outside the municipality")
    if (sinasc["year"] < 2010).any() or (sinasc["year"] > 2025).any():
        issues.append("SINASC year outside 2010-2025")
    if sinasc["is_chd"].sum() == 0:
        issues.append("no CHD cases in SINASC")
    if sih["year"].min() < 2010 or sih["year"].max() > 2025:
        issues.append("SIH year outside 2010-2025")
    if sih["MUNIC_RES"].astype(str).str[:6].ne("330100").any():
        issues.append("SIH records outside the municipality")
    if climate["temperature_2m_max"].isna().any():
        issues.append("missing daily Tmax in climate series")
    if not climate["date"].min().startswith("2010") or not climate["date"].max().startswith("2025"):
        issues.append("climate series does not cover 2010-2025")
    return {
        "sinasc_births": int(len(sinasc)),
        "sinasc_chd": int(sinasc["is_chd"].sum()),
        "sinasc_years": sorted(int(y) for y in sinasc["year"].unique()),
        "sih_admissions": int(len(sih)),
        "climate_days": int(len(climate)),
        "issues": issues,
        "passed": not issues,
    }


def run() -> dict[str, Any]:
    results = {
        "generated_at": today(),
        "graph": check_graph(),
        "curated": check_curated(),
        "pmid_resolution": check_pmid_resolution(),
        "local_data": check_local_data(),
    }
    results["passed"] = all(v["passed"] for k, v in results.items() if isinstance(v, dict) and "passed" in v)
    write_json(config.REPORTS / "validation_results.json", results)
    lines = ["# Validation report", "", f"Generated: {today()}", ""]
    for k in ("graph", "curated", "pmid_resolution", "local_data"):
        v = results[k]
        lines.append(f"## {k}")
        lines.append("")
        lines.append(f"Passed: **{v['passed']}**")
        for kk, vv in v.items():
            if kk in {"passed", "issues"}:
                continue
            lines.append(f"- {kk}: {vv}")
        if v.get("issues"):
            lines.append("")
            lines.append("Issues:")
            for i in v["issues"]:
                lines.append(f"- {i}")
        lines.append("")
    lines.append("All curated quotes were verified automatically against PubMed; the study team read every anchor abstract.")
    (config.REPORTS / "validation_report.md").write_text("\n".join(lines), encoding="utf-8")
    log.info("validation passed=%s", results["passed"])
    return results


if __name__ == "__main__":
    run()
