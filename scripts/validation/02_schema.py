"""Lightweight schema checks for the published outputs.

These checks are intentionally dependency-light (pandas + stdlib) so that they
run in CI and in local environments without extra services. They complement
`01_validate.py` (integrity) and `compliance/01_check.py` (privacy/FAIR).
"""

from __future__ import annotations

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
REPORT_JSON = ROOT / "reports" / "schema_validation.json"
REPORT_MD = ROOT / "reports" / "schema_validation.md"

REQUIRED = {
    "outputs/graph/nodes.csv": ["node_id", "label", "type"],
    "outputs/graph/relations.csv": ["edge_id", "source_id", "target_id", "relation", "confidence", "evidence_tier_label"],
    "outputs/graph/evidence.csv": ["evidence_id", "edge_key", "reference"],
    "outputs/tables/exploratory_models.csv": ["model", "p_value", "q_value"],
    "outputs/tables/hypothesis_candidates.csv": ["exposure_id", "phenotype_id", "mechanism_id", "p_hyper", "q_fdr"],
    "data_processed/pm25_campos_anual.csv": ["cod_municipio", "uf", "ano", "pm25_ug_m3"],
    "data_processed/pm25_campos_mensal.csv": ["cod_municipio", "uf", "ano", "mes", "pm25_ug_m3"],
    "app/data/models.csv": ["model", "p_value", "q_value"],
    "outputs/tables/sensitivity_leave_one_year_out.csv": ["excluded_year", "p_value", "q_value"],
    "outputs/tables/exposure_correlation.csv": ["exposure"],
    "outputs/tables/exposure_vif.csv": ["exposure", "vif"],
}

INDIVIDUAL_DATA = {
    "data_processed/sinasc_campos_births.csv",
    "data_processed/sinasc_campos_with_exposure.csv",
    "data_processed/sih_campos_chd_admissions.csv",
}


def add(checks: list[dict], name: str, ok: bool, detail: str = "") -> None:
    checks.append({"check": name, "ok": bool(ok), "detail": detail})


def main() -> None:
    checks: list[dict] = []

    for rel, cols in REQUIRED.items():
        path = ROOT / rel
        if not path.exists():
            add(checks, f"exists:{rel}", False, "missing")
            continue
        df = pd.read_csv(path)
        missing = [c for c in cols if c not in df.columns]
        add(checks, f"columns:{rel}", not missing, f"missing={missing}" if missing else f"{len(df)} rows")

    # FDR sanity: q must be >= p and in [0, 1].
    for rel, pcols, qcols in [
        ("outputs/tables/exploratory_models.csv", ["p_value", "exposure_1_p", "exposure_2_p"],
         ["q_value", "exposure_1_q", "exposure_2_q"]),
        ("outputs/tables/hypothesis_candidates.csv", ["p_hyper"], ["q_fdr"]),
    ]:
        path = ROOT / rel
        if not path.exists():
            continue
        df = pd.read_csv(path)
        bad = []
        for pcol, qcol in zip(pcols, qcols):
            if pcol not in df.columns or qcol not in df.columns:
                bad.append(f"missing {pcol}/{qcol}")
                continue
            sub = df[[pcol, qcol]].dropna()
            if ((sub[qcol] < 0) | (sub[qcol] > 1)).any():
                bad.append(f"{qcol} outside [0,1]")
            if (sub[qcol] + 1e-6 < sub[pcol]).any():
                bad.append(f"{qcol} < {pcol}")
        add(checks, f"fdr:{rel}", not bad, "; ".join(bad) if bad else "ok")

    # PM2.5 completeness.
    monthly = ROOT / "data_processed/pm25_campos_mensal.csv"
    if monthly.exists():
        df = pd.read_csv(monthly)
        add(checks, "pm25:monthly_rows", len(df) == 192, f"{len(df)} rows")
        add(checks, "pm25:monthly_unique", not df.duplicated(["ano", "mes"]).any(),
            "duplicates" if df.duplicated(["ano", "mes"]).any() else "ok")
        add(checks, "pm25:monthly_range", bool(df["pm25_ug_m3"].between(0, 500).all()), "0-500 µg/m3")
        expected = pd.MultiIndex.from_product([range(2010, 2026), range(1, 13)], names=["ano", "mes"])
        missing = expected.difference(pd.MultiIndex.from_frame(df[["ano", "mes"]]))
        add(checks, "pm25:monthly_complete", len(missing) == 0, f"{len(missing)} missing")

    annual = ROOT / "data_processed/pm25_campos_anual.csv"
    if annual.exists():
        df = pd.read_csv(annual)
        add(checks, "pm25:annual_years", len(df) == 16 and set(df["ano"]) == set(range(2010, 2026)),
            f"{len(df)} rows")

    # The app bundle must never contain individual-level records.
    app = ROOT / "app" / "data"
    found = [p.name for p in app.glob("*") if p.name in {Path(x).name for x in INDIVIDUAL_DATA}]
    add(checks, "app:no_individual_data", not found, ",".join(found) if found else "ok")

    # Machine-readable metadata must agree on the version.
    versions = {}
    for rel in ["fair/metadata.json", "fair/datapackage.json", "app/data/metadata.json", "codemeta.json"]:
        path = ROOT / rel
        if path.exists():
            versions[rel] = json.loads(path.read_text(encoding="utf-8")).get("version") or \
                json.loads(path.read_text(encoding="utf-8")).get("versao")
    unique = {v for v in versions.values() if v}
    add(checks, "metadata:version_consistent", len(unique) <= 1, f"{versions}")
    add(checks, "lockfiles:present", (ROOT / "uv.lock").exists() and (ROOT / "renv.lock").exists(), "uv.lock + renv.lock")
    add(checks, "release:changelog", "0.3.0" in (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"), "CHANGELOG has 0.3.0")

    passed = all(c["ok"] for c in checks)
    out = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "passed": passed,
        "checks": checks,
    }
    REPORT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = ["# Schema validation", "", f"Generated: {out['generated_at']}", "",
             f"**Result: {'PASSED' if passed else 'FAILED'}**", ""]
    lines += [f"- {'OK' if c['ok'] else 'FAIL'} — `{c['check']}` — {c['detail']}" for c in checks]
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    if not passed:
        sys.exit(1)


if __name__ == "__main__":
    main()
