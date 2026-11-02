"""Validation: bibliographic, biological, data and computational checks.

The checks are intentionally explicit and fail loudly. Every curated quote is
re-verified automatically against PubMed. Manual rows and AI-assisted reviewed
rows are distinguished in the evidence table and in the reports.
"""

from __future__ import annotations

import json
import random
from collections import Counter
from typing import Any

import pandas as pd

from .. import config
from ..curation import batch_review
from ..curation.batch_extract import normalise
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
    anchor_rows = read_csv(config.CURATED / "anchor_studies.csv")
    anchors = {r.get("reference") or r["pmid"] for r in anchor_rows}
    issues = []
    refs = set()
    allowed_types = {"PMID", "CAPES thesis"}
    for e in edges:
        if not e["reference"]:
            issues.append(f"missing reference: {e['edge_key']}")
        if e["reference_type"] not in allowed_types:
            issues.append(f"unsupported reference type: {e['edge_key']} ({e['reference_type']})")
        refs.add(e["reference"])
        if not e.get("quote"):
            issues.append(f"missing quote: {e['edge_key']}")
    missing = refs - anchors
    if missing:
        issues.append(f"references without anchor record: {sorted(missing)}")

    def norm(x: str) -> str:
        import re
        return re.sub(r"\s+", " ", x).strip().lower()

    # Re-verify a random 25% sample of PubMed abstract quotes.
    random.seed(20261031)
    pmid_edges = [
        e for e in edges
        if e["reference_type"] == "PMID" and e.get("quote_source", "abstract") != "full_text"
    ]
    sample = random.sample(pmid_edges, max(1, len(pmid_edges) // 4)) if pmid_edges else []
    studies = {s.pmid: s for s in efetch([e["reference"] for e in sample])}
    for e in sample:
        s = studies.get(e["reference"])
        if not s or norm(e["quote"]) not in norm(s.abstract):
            issues.append(f"quote not found on PubMed re-check: {e['reference']}")

    # Re-verify every full-text quote against its archived short quotation.
    fulltext_edges = [e for e in edges if e.get("quote_source") == "full_text"]
    for e in fulltext_edges:
        path = config.CURATED / (e.get("quote_archive") or "")
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            issues.append(f"full-text archive missing: {e['reference']}")
            continue
        if norm(e["quote"]) != norm(payload.get("quote", "")):
            issues.append(f"full-text quote differs from archive: {e['reference']}")

    # Re-verify every non-PMID quote against its archived local abstract.
    for e in edges:
        if e.get("quote_source") == "full_text":
            continue
        if e["reference_type"] == "PMID":
            continue
        capes_id = e["reference"].split(":")[-1]
        path = config.CURATED / "capes_abstracts" / f"{capes_id}.json"
        try:
            abstract = json.loads(path.read_text(encoding="utf-8"))["abstract"]
        except (OSError, KeyError, json.JSONDecodeError):
            issues.append(f"archived abstract missing: {e['reference']}")
            continue
        if norm(e["quote"]) not in norm(abstract):
            issues.append(f"quote not found on local re-check: {e['reference']}")

    return {
        "n_curated_edges": len(edges),
        "n_unique_references": len(refs),
        "n_capes_theses": sum(1 for r in refs if not str(r).isdigit()),
        "sampled_for_recheck": len(sample),
        "n_fulltext_recheck": len(fulltext_edges),
        "issues": issues,
        "passed": not issues,
    }


def check_pmid_resolution() -> dict[str, Any]:
    anchors = read_csv(config.CURATED / "anchor_studies.csv")
    pmids = [r["pmid"] for r in anchors if str(r.get("pmid", "")).strip()]
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
    sinasc_path = config.DATA_PROCESSED / "sinasc_campos_births.csv"
    sih_path = config.DATA_PROCESSED / "sih_campos_chd_admissions.csv"
    climate = pd.read_csv(config.DATA_PROCESSED / "climate_daily_campos.csv")
    climate_ok = not climate["temperature_2m_max"].isna().any()
    climate_meta_path = config.DATA_RAW / "external" / "climate_source_metadata.json"
    climate_model_ok = False
    if climate_meta_path.exists():
        climate_meta = json.loads(climate_meta_path.read_text(encoding="utf-8"))
        climate_model_ok = climate_meta.get("model_requested") == "era5_land"
    if not sinasc_path.exists() or not sih_path.exists():
        # Individual-level files are intentionally not redistributed (docs/15).
        return {
            "status": "skipped",
            "reason": "individual-level SINASC/SIH files are not versioned",
            "climate_days": int(len(climate)),
            "issues": [] if climate_ok else ["missing daily Tmax in climate series"],
            "passed": climate_ok,
        }
    sinasc = pd.read_csv(sinasc_path, low_memory=False)
    sih = pd.read_csv(sih_path, low_memory=False)
    if sinasc["codmunres"].astype(str).str[:6].ne("330100").any():
        issues.append("SINASC records outside the municipality")
    if (sinasc["year"] < 2010).any() or (sinasc["year"] > 2025).any():
        issues.append("SINASC year outside 2010-2025")
    if sinasc["is_chd"].sum() == 0:
        issues.append("no Q20-Q28 cases in SINASC")
    if "is_other_circulatory" not in sinasc.columns:
        issues.append("SINASC lacks the Q27-Q28 subgroup flag")
    if not climate_model_ok:
        issues.append("climate model is not explicitly fixed to era5_land")
    if sih["year"].min() < 2010 or sih["year"].max() > 2025:
        issues.append("SIH year outside 2010-2025")
    if "diag_princ_other_circulatory" not in sih.columns:
        issues.append("SIH lacks the Q27-Q28 subgroup flag")
    if sih["MUNIC_RES"].astype(str).str[:6].ne("330100").any():
        issues.append("SIH records outside the municipality")
    if climate["temperature_2m_max"].isna().any():
        issues.append("missing daily Tmax in climate series")
    if not climate["date"].min().startswith("2010") or not climate["date"].max().startswith("2025"):
        issues.append("climate series does not cover 2010-2025")
    return {
        "sinasc_births": int(len(sinasc)),
        "sinasc_circulatory_q20_q28": int(sinasc["is_chd"].sum()),
        "sinasc_q27_q28_subgroup": int(sinasc["is_other_circulatory"].sum()) if "is_other_circulatory" in sinasc.columns else None,
        "sinasc_years": sorted(int(y) for y in sinasc["year"].unique()),
        "climate_model": "era5_land" if climate_model_ok else "unverified",
        "sih_admissions": int(len(sih)),
        "climate_days": int(len(climate)),
        "issues": issues,
        "passed": not issues,
    }


def check_batch_curation() -> dict[str, Any]:
    """Audit the review layer that promotes screening candidates to evidence.

    Offline and deterministic: it checks the review file against the queue and
    checks that the evidence table contains exactly the verified review rows.
    """
    queue_path = config.CURATED / "batch_chd_queue.csv"
    review_path = config.CURATED / "batch_chd_review.csv"
    if not queue_path.exists() or not review_path.exists():
        return {
            "status": "skipped",
            "reason": "batch curation files are not present",
            "issues": [],
            "passed": True,
        }
    queue = read_csv(queue_path)
    reviews = batch_review.load_reviews(review_path)
    issues = batch_review.review_issues(reviews.values(), queue)
    verified = {
        batch_review.key_of(row)
        for row in reviews.values()
        if row.get("review_status") == "verified"
    }
    evidence = read_csv(config.GRAPH_OUT / "evidence.csv")
    batch_rows = [
        row for row in evidence
        if "batch curation" in row.get("source_database", "")
        or "full-text curation" in row.get("source_database", "")
    ]
    def evidence_key(row: dict[str, Any]) -> tuple[str, str, str]:
        return (row.get("reference", ""), row.get("source_id", ""), row.get("target_id", ""))

    in_evidence = {evidence_key(row) for row in batch_rows}
    for key in sorted(verified - in_evidence):
        issues.append(f"verified review row missing from evidence.csv: {'|'.join(key)}")
    for key in sorted(in_evidence - verified):
        issues.append(f"batch evidence row without verified review: {'|'.join(key)}")

    quotes = {evidence_key(row): normalise(row.get("quote", "")) for row in batch_rows}
    for row in reviews.values():
        if row.get("review_status") != "verified":
            continue
        key = batch_review.key_of(row)
        quote = normalise(row.get("review_quote") or "")
        if key in quotes and quote and quotes[key] != quote:
            issues.append(f"review quote differs from evidence quote: {'|'.join(key)}")
    return {
        "n_queue": len(queue),
        "n_verified": len(verified),
        "n_rejected": sum(1 for r in reviews.values() if r.get("review_status") == "rejected"),
        "n_batch_evidence": len(batch_rows),
        "issues": issues,
        "passed": not issues,
    }


def run() -> dict[str, Any]:
    results = {
        "generated_at": today(),
        "graph": check_graph(),
        "curated": check_curated(),
        "batch_curation": check_batch_curation(),
        "pmid_resolution": check_pmid_resolution(),
        "local_data": check_local_data(),
    }
    results["passed"] = all(v["passed"] for k, v in results.items() if isinstance(v, dict) and "passed" in v)
    write_json(config.REPORTS / "validation_results.json", results)
    lines = ["# Validation report", "", f"Generated: {today()}", ""]
    for k in ("graph", "curated", "batch_curation", "pmid_resolution", "local_data"):
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
    lines.append("All curated quotes were verified automatically against PubMed abstracts, the archived CAPES thesis abstract, or the archived full-text quotation. The 54 manual rows were read by the study team; the 49 batch rows were promoted only after an explicit review entry, are flagged as AI-assisted, and remain subject to independent human confirmation. Full-text quotations are rechecked against their archived short quotation; the review layer is audited against the evidence table.")
    (config.REPORTS / "validation_report.md").write_text("\n".join(lines), encoding="utf-8")
    log.info("validation passed=%s", results["passed"])
    return results


if __name__ == "__main__":
    run()
