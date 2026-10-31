"""SIH/SUS (hospital admissions) extraction for Campos dos Goytacazes.

Important interpretative limits (enforced here and in the reports):
* The unit is an AIH (authorisation of hospital admission), **not a person**.
  SIH does not expose a stable patient identifier, so readmissions cannot be
  reliably linked; the study never reports "number of children".
* SIH admissions are not incidence: they depend on access, referral flow and
  diagnostic coding.
* Residence (``MUNIC_RES``) and place of admission (``MUNIC_MOV``) are kept
  separately so that referral flow can be described.
* ``DIAG_SECUN``/``CID_ASSO`` are searched for Q20-Q28 but reported separately
  from the primary-diagnosis analysis.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pandas as pd

from .. import config
from ..io_utils import get_logger, today, write_csv, write_json

log = get_logger("sih")

CHD_PREFIXES = tuple(config.CID10_CHAPTER_CHD)
KEEP = [
    "ANO_CMPT", "MES_CMPT", "N_AIH", "MUNIC_RES", "MUNIC_MOV", "CNES", "DIAG_PRINC",
    "DIAG_SECUN", "CID_ASSO", "CID_MORTE", "DT_INTER", "DT_SAIDA", "DIAS_PERM",
    "MORTE", "VAL_TOT", "VAL_UTI", "CAR_INT", "IDADE", "COD_IDADE", "SEXO",
    "IDENT", "PROC_REA", "UTI_MES_TO",
]


def dbc_to_dbf(dbc: Path) -> Path:
    dbf = dbc.with_suffix(".dbf")
    if dbf.exists() and dbf.stat().st_mtime >= dbc.stat().st_mtime:
        return dbf
    from pyreaddbc import dbc2dbf

    dbc2dbf(str(dbc), str(dbf))
    return dbf


def is_chd(code: str) -> bool:
    return bool(code) and str(code).strip()[:3] in CHD_PREFIXES


def download_all(years: list[int] | None = None) -> list[Path]:
    import urllib.request

    years = years or list(range(config.PERIOD_START, config.PERIOD_END + 1))
    paths = []
    for y in years:
        for m in range(1, 13):
            name = f"RDRJ{str(y)[2:]}{m:02d}.dbc"
            out = config.DATA_RAW / "sih" / name
            if not out.exists() or out.stat().st_size == 0:
                url = f"{config.DATASUS_SIH_FTP}/{name}"
                try:
                    log.info("downloading %s", name)
                    urllib.request.urlretrieve(url, out)
                except Exception as exc:  # noqa: BLE001
                    log.warning("failed %s: %s", name, exc)
                    continue
            paths.append(out)
    return paths


def extract_file(dbc: Path, include_secondary: bool = True) -> list[dict[str, Any]]:
    from dbfread import DBF

    dbf = dbc_to_dbf(dbc)
    table = DBF(str(dbf), load=False, encoding="latin-1")
    out = []
    for r in table:
        res = str(r.get("MUNIC_RES", "")).strip()[:6]
        if res != config.MUNICIPALITY["ibge6"]:
            continue
        diag = str(r.get("DIAG_PRINC", "")).strip().upper()
        sec = str(r.get("DIAG_SECUN", "")).strip().upper()
        assoc = str(r.get("CID_ASSO", "")).strip().upper()
        prim_chd = is_chd(diag)
        sec_chd = include_secondary and (is_chd(sec) or is_chd(assoc))
        if not (prim_chd or sec_chd):
            continue
        rec = {k: r.get(k, "") for k in KEEP}
        rec["source_file"] = dbc.name
        rec["diag_princ_chd"] = prim_chd
        rec["diag_sec_chd"] = sec_chd
        rec["chd_group"] = diag[:3] if prim_chd else (sec[:3] if is_chd(sec) else assoc[:3])
        rec["year"] = int(str(r.get("ANO_CMPT", "")).strip() or 0)
        rec["age_years"] = _age_years(r.get("IDADE"), str(r.get("COD_IDADE", "")).strip())
        out.append(rec)
    return out


def _age_years(idade: Any, cod: str) -> float | None:
    try:
        v = float(str(idade).strip())
    except (TypeError, ValueError):
        return None
    if cod == "4":  # years
        return v
    if cod == "3":  # months
        return v / 12
    if cod == "2":  # days
        return v / 365.25
    return None


def age_group(age: float | None) -> str:
    if age is None:
        return "unknown"
    if age < 1:
        return "<1y"
    if age < 5:
        return "1-4y"
    if age < 10:
        return "5-9y"
    if age < 15:
        return "10-14y"
    if age < 18:
        return "15-17y"
    return "18y+"


def _worker(path_str: str) -> list[dict[str, Any]]:
    from pathlib import Path

    try:
        recs = extract_file(Path(path_str), include_secondary=True)
    except Exception as exc:  # noqa: BLE001
        log.warning("failed %s: %s", path_str, exc)
        return []
    dbf = Path(path_str).with_suffix(".dbf")
    try:
        if dbf.exists():
            dbf.unlink()
    except OSError:
        pass
    return recs


def build_dataset(workers: int = 10) -> pd.DataFrame:
    from concurrent.futures import ProcessPoolExecutor, as_completed

    files = sorted((config.DATA_RAW / "sih").glob("RDRJ*.dbc"))
    if not files:
        log.error("no SIH files found")
        return pd.DataFrame()
    rows: list[dict[str, Any]] = []
    done = 0
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(_worker, str(f)): f for f in files}
        for fut in as_completed(futures):
            rows.extend(fut.result())
            done += 1
            if done % 20 == 0:
                log.info("processed %s/%s files, %s CHD admissions", done, len(files), len(rows))
    df = pd.DataFrame(rows)
    if len(df):
        df["age_group"] = df["age_years"].map(age_group)
    out = config.DATA_PROCESSED / "sih_campos_chd_admissions.csv"
    df.to_csv(out, index=False, encoding="utf-8")
    log.info("SIH: %s CHD admissions from %s files -> %s", len(df), len(files), out)
    return df


def summarise(df: pd.DataFrame) -> dict[str, Any]:
    if df.empty:
        return {}
    prim = df[df["diag_princ_chd"]].copy()
    prim["year"] = prim["year"].astype(int)
    prim["MORTE"] = pd.to_numeric(prim["MORTE"], errors="coerce").fillna(0).astype(int)
    prim["DIAS_PERM"] = pd.to_numeric(prim["DIAS_PERM"], errors="coerce")
    prim["VAL_TOT"] = pd.to_numeric(prim["VAL_TOT"], errors="coerce")
    prim["CAR_INT"] = prim["CAR_INT"].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(2)

    annual = []
    for y, sub in prim.groupby("year"):
        annual.append(
            {
                "year": y,
                "admissions_primary_chd": len(sub),
                "deaths": int(sub["MORTE"].sum()),
                "hospital_mortality_pct": round(100 * sub["MORTE"].sum() / len(sub), 2) if len(sub) else "",
                "mean_length_of_stay_days": round(sub["DIAS_PERM"].mean(), 2) if len(sub) else "",
                "total_cost_brl": round(sub["VAL_TOT"].sum(), 2),
                "mean_cost_brl": round(sub["VAL_TOT"].mean(), 2) if len(sub) else "",
                "hospitals": sub["CNES"].nunique(),
                "elective_pct": round(100 * (sub["CAR_INT"] == "02").sum() / len(sub), 2) if len(sub) else "",
            }
        )
    write_csv(config.TABLES / "sih_annual.csv", annual)

    by_age = prim.groupby(["year", "age_group"]).size().reset_index(name="admissions")
    by_age.to_csv(config.TABLES / "sih_by_age_group.csv", index=False)

    by_group = prim.groupby(["year", "chd_group"]).size().reset_index(name="admissions")
    by_group.to_csv(config.TABLES / "sih_by_chd_group_year.csv", index=False)

    # referral flow: municipality of admission for Campos residents
    flow = prim.groupby("MUNIC_MOV").size().reset_index(name="admissions").sort_values("admissions", ascending=False)
    flow.to_csv(config.TABLES / "sih_admission_municipality_flow.csv", index=False)

    # residents admitted outside the municipality of residence, and diagnoses
    outside = prim[prim["MUNIC_MOV"].astype(str).str[:6] != config.MUNICIPALITY["ibge6"]]
    qa = {
        "n_admissions_with_primary_chd": int(len(prim)),
        "n_admissions_secondary_only_chd": int(len(df) - len(prim)),
        "n_unique_hospitals": int(prim["CNES"].nunique()),
        "years": sorted(int(y) for y in prim["year"].unique()),
        "pct_admitted_outside_residence": round(100 * len(outside) / len(prim), 2) if len(prim) else "",
        "n_deaths": int(prim["MORTE"].sum()),
        "mean_age_years": round(prim["age_years"].mean(), 2) if prim["age_years"].notna().any() else "",
        "age_unknown_pct": round(100 * prim["age_years"].isna().mean(), 2),
        "n_with_secondary_chd_only": int((~df["diag_princ_chd"] & df["diag_sec_chd"]).sum()),
        "readmission_analysis": "not performed: SIH/AIH has no stable patient identifier",
        "retrieved_at": today(),
    }
    write_json(config.DATA_PROCESSED / "sih_quality_report.json", qa)
    log.info("SIH quality: %s", qa)
    return qa
