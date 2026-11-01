"""SINASC (Live Birth Information System) extraction for Campos dos Goytacazes.

Design notes
------------
* Unit of analysis: live birth record of a mother residing in the municipality
  (``CODMUNRES`` 330100).  Place of birth is kept separately.
* Core CHD case: at least one CID-10 code in Q20-Q26 in ``CODANOMAL``.
  Q27 (peripheral vascular malformations) and Q28 (other circulatory
  malformations) are classified separately and are **not** counted as CHD.
  ``CODANOMAL`` is a concatenation of 4-character codes (e.g. ``Q339Q652``);
  codes are parsed in blocks of four and never truncated to the first code.
* ``IDANOMAL`` is kept for data-quality assessment but is **not** used as the
  inclusion criterion, to avoid losing records with a missing flag.
* Gestational age at birth (``SEMAGESTAC``, weeks; ``GESTACAO`` categories) is
  used to estimate the conception date and the cardiac organogenesis window
  (weeks 3-8 post-conception).  Gestational age is counted from the last
  menstrual period; conception is assumed to occur 14 days later, so the
  conception estimate is gestational age minus 14 days.  Early/late windows
  (plus or minus 7 days) are stored for sensitivity analysis.
* 2025 data are preliminary at the time of extraction and are flagged.
"""

from __future__ import annotations

import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd

from .. import config
from ..io_utils import get_logger, today, write_csv, write_json

log = get_logger("sinasc")

CODE_RE = re.compile(r"^[A-Z]\d{2}")
CHD_PREFIXES = tuple(config.CID10_CHAPTER_CHD)
OTHER_CIRCULATORY_PREFIXES = tuple(config.CID10_OTHER_CIRCULATORY)
CONCEPTION_LAG_DAYS = 14  # conception occurs about two weeks after LMP
GA_UNCERTAINTY_DAYS = 7
GESTACAO_MIDPOINT = {
    "1": 24.0,  # < 22 weeks
    "2": 28.5,  # 22-27
    "3": 33.5,  # 28-31
    "4": 35.5,  # 32-36
    "5": 39.5,  # 37-41
    "6": 42.0,  # 42+
}


def parse_icd_codes(value: str) -> list[str]:
    """Split a CODANOMAL string into 4-character ICD-10 codes."""
    if not value:
        return []
    s = re.sub(r"[^A-Z0-9]", "", str(value).upper())
    codes = [s[i : i + 4] for i in range(0, len(s), 4)]
    return [c for c in codes if len(c) == 4 and CODE_RE.match(c)]


def is_chd_code(code: str) -> bool:
    """True only for the core CHD group Q20-Q26."""
    return code[:3] in CHD_PREFIXES


def is_other_circulatory_code(code: str) -> bool:
    """True for Q27/Q28, kept separate from the CHD case definition."""
    return code[:3] in OTHER_CIRCULATORY_PREFIXES


def chd_codes(value: str) -> list[str]:
    return [c for c in parse_icd_codes(value) if is_chd_code(c)]


def other_circulatory_codes(value: str) -> list[str]:
    return [c for c in parse_icd_codes(value) if is_other_circulatory_code(c)]


def _gestation_weeks(semagestac: float | None, gestacao: str) -> tuple[float | None, str]:
    if semagestac is not None and 20 <= semagestac <= 45:
        return float(semagestac), "semagestac"
    midpoint = GESTACAO_MIDPOINT.get(str(gestacao))
    if midpoint is not None:
        return float(midpoint), "gestacao_categoria"
    return None, "missing"


def dbc_to_dbf(dbc: Path) -> Path:
    dbf = dbc.with_suffix(".dbf")
    if dbf.exists() and dbf.stat().st_mtime >= dbc.stat().st_mtime:
        return dbf
    from pyreaddbc import dbc2dbf

    dbc2dbf(str(dbc), str(dbf))
    return dbf


def download_years(years: list[int] | None = None) -> list[Path]:
    import urllib.request

    years = years or config.SINASC_YEARS_AVAILABLE
    paths = []
    for y in years:
        folder = (
            config.DATASUS_SINASC_PRELIM_FTP
            if y in config.SINASC_PRELIMINARY_YEARS
            else config.DATASUS_SINASC_FTP
        )
        name = f"DNRJ{y}.dbc"
        out = config.DATA_RAW / "sinasc" / name
        if not out.exists() or out.stat().st_size == 0:
            url = f"{folder}/{name}"
            log.info("downloading %s", url)
            urllib.request.urlretrieve(url, out)
        paths.append(out)
    return paths


def _as_float(value: Any) -> float | None:
    try:
        if value is None or str(value).strip() == "":
            return None
        return float(str(value).strip())
    except ValueError:
        return None


def _as_int(value: Any) -> int | None:
    f = _as_float(value)
    return int(f) if f is not None else None


def estimate_conception(dtnasc: datetime, semagestac: float | None, gestacao: str) -> datetime | None:
    """Estimate conception date from gestational age at birth.

    ``SEMAGESTAC`` and ``GESTACAO`` are obstetric gestational ages measured
    from the last menstrual period (LMP).  Conception is approximately 14 days
    after LMP, so a 40-week gestation corresponds to 266 days before birth,
    not 280.
    """
    weeks, _ = _gestation_weeks(semagestac, gestacao)
    if weeks is None:
        return None
    return dtnasc - timedelta(days=round(weeks * 7) - CONCEPTION_LAG_DAYS)


def extract_year(year: int, keep_all_births: bool = True) -> pd.DataFrame:
    dbc = config.DATA_RAW / "sinasc" / f"DNRJ{year}.dbc"
    if not dbc.exists():
        log.warning("missing SINASC file for %s", year)
        return pd.DataFrame()
    dbf = dbc_to_dbf(dbc)
    from dbfread import DBF

    table = DBF(str(dbf), load=False, encoding="latin-1")
    rows = []
    for r in table:
        mun = str(r.get("CODMUNRES", "")).strip()[:6]
        if mun != config.MUNICIPALITY["ibge6"]:
            continue
        cod = str(r.get("CODANOMAL", "")).strip()
        codes = parse_icd_codes(cod)
        chd = [c for c in codes if is_chd_code(c)]
        other = [c for c in codes if is_other_circulatory_code(c)]
        if not keep_all_births and not chd:
            continue
        dtnasc_raw = str(r.get("DTNASC", "")).strip()
        try:
            dtnasc = datetime.strptime(dtnasc_raw, "%d%m%Y") if len(dtnasc_raw) == 8 else None
        except ValueError:
            dtnasc = None
        sem = _as_float(r.get("SEMAGESTAC"))
        gest = str(r.get("GESTACAO", "")).strip()
        weeks, weeks_source = _gestation_weeks(sem, gest)
        conception = estimate_conception(dtnasc, sem, gest) if dtnasc else None

        def _dates(offset_days: int = 0) -> tuple[str, str, str]:
            if conception is None:
                return "", "", ""
            c = conception + timedelta(days=offset_days)
            return (
                c.date().isoformat(),
                (c + timedelta(days=21)).date().isoformat(),
                (c + timedelta(days=56)).date().isoformat(),
            )

        c_main, w_start, w_end = _dates()
        c_early, w_start_early, w_end_early = _dates(-GA_UNCERTAINTY_DAYS)
        c_late, w_start_late, w_end_late = _dates(GA_UNCERTAINTY_DAYS)
        rows.append(
            {
                "year": year,
                "uf": "RJ",
                "codmunres": mun,
                "codmunnasc": str(r.get("CODMUNNASC", "")).strip(),
                "dtnasc": dtnasc.date().isoformat() if dtnasc else "",
                "sexo": str(r.get("SEXO", "")).strip(),
                "idanomal": str(r.get("IDANOMAL", "")).strip(),
                "codanomal": cod,
                "n_icd_codes": len(codes),
                "chd_codes": ";".join(chd),
                "other_circulatory_codes": ";".join(other),
                "is_chd": bool(chd),
                "is_other_circulatory": bool(other),
                "idademae": _as_int(r.get("IDADEMAE")),
                "escmae": str(r.get("ESCMAE", "")).strip(),
                "estcivmae": str(r.get("ESTCIVMAE", "")).strip(),
                "racacor": str(r.get("RACACOR", "")).strip(),
                "gestacao": gest,
                "semagestac": sem,
                "gestation_weeks_used": round(weeks, 2) if weeks is not None else "",
                "gestation_source": weeks_source,
                "peso": _as_int(r.get("PESO")),
                "apgar1": _as_int(r.get("APGAR1")),
                "apgar5": _as_int(r.get("APGAR5")),
                "tipo_gravidez": str(r.get("GRAVIDEZ", "")).strip(),
                "parto": str(r.get("PARTO", "")).strip(),
                "consultas": str(r.get("CONSULTAS", "")).strip(),
                "conception_date_est": c_main,
                "organogenesis_start_est": w_start,
                "organogenesis_end_est": w_end,
                "conception_date_early": c_early,
                "organogenesis_start_early": w_start_early,
                "organogenesis_end_early": w_end_early,
                "conception_date_late": c_late,
                "organogenesis_start_late": w_start_late,
                "organogenesis_end_late": w_end_late,
            }
        )
    df = pd.DataFrame(rows)
    log.info("SINASC %s: %s records for Campos (%s core CHD; %s Q27-Q28)", year, len(df),
                 int(df["is_chd"].sum()) if len(df) else 0,
                 int(df["is_other_circulatory"].sum()) if len(df) else 0)
    return df


def build_dataset() -> pd.DataFrame:
    frames = []
    for y in config.SINASC_YEARS_AVAILABLE:
        df = extract_year(y)
        if len(df):
            frames.append(df)
    full = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    out = config.DATA_PROCESSED / "sinasc_campos_births.csv"
    full.to_csv(out, index=False, encoding="utf-8")
    log.info("SINASC dataset: %s births, %s CHD -> %s", len(full), int(full["is_chd"].sum()) if len(full) else 0, out)
    return full


def summarise(df: pd.DataFrame) -> dict[str, Any]:
    """Annual indicators, phenotype distributions and data quality.

    The primary CHD indicator uses the core Q20-Q26 definition.  Q27/Q28 are
    summarised in separate tables and are never added to the CHD count.
    """
    if df.empty:
        return {}
    df = df.copy()
    df["is_chd"] = df["is_chd"].astype(str).str.lower().isin(["true", "1", "1.0"])
    if "is_other_circulatory" not in df.columns:
        df["is_other_circulatory"] = False
    df["is_other_circulatory"] = (
        df["is_other_circulatory"].astype(str).str.lower().isin(["true", "1", "1.0"])
    )
    for col in ("idanomal", "sexo", "parto", "tipo_gravidez", "escmae", "racacor", "estcivmae"):
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(r"\.0$", "", regex=True)
    df["conception_date_est"] = df["conception_date_est"].fillna("").astype(str)

    rows = []
    for y in sorted(df["year"].unique()):
        sub = df[df["year"] == y]
        n = len(sub)
        cases = int(sub["is_chd"].sum())
        other = int(sub["is_other_circulatory"].sum())
        total = int((sub["is_chd"] | sub["is_other_circulatory"]).sum())
        rows.append(
            {
                "year": int(y),
                "live_births": n,
                "chd_cases": cases,
                "chd_per_10000_lb": round(10000 * cases / n, 2) if n else "",
                "chd_proportion_per_1000_lb": round(1000 * cases / n, 2) if n else "",
                "other_circulatory_cases": other,
                "other_circulatory_per_10000_lb": round(10000 * other / n, 2) if n else "",
                "circulatory_cases_total": total,
                "circulatory_per_10000_lb": round(10000 * total / n, 2) if n else "",
                "anomaly_flag_1": int((sub["idanomal"] == "1").sum()),
                "any_q_code": int(sub["codanomal"].str.startswith("Q").sum()),
                "data_status": "preliminary" if int(y) in config.SINASC_PRELIMINARY_YEARS else "consolidated",
            }
        )
    write_csv(config.TABLES / "sinasc_annual.csv", rows)

    cases = df[df["is_chd"]].copy()
    cases["chd_code"] = cases["chd_codes"].str.split(";")
    exploded = cases.explode("chd_code")
    by_code = (
        exploded.groupby(["year", "chd_code"]).size().reset_index(name="n").sort_values(["year", "chd_code"])
    )
    by_code.to_csv(config.TABLES / "sinasc_chd_by_code_year.csv", index=False)
    overall = exploded.groupby("chd_code").size().reset_index(name="n").sort_values("n", ascending=False)
    overall.to_csv(config.TABLES / "sinasc_chd_by_code.csv", index=False)
    by_group = (
        exploded.assign(group=exploded["chd_code"].str[:3])
        .groupby(["year", "group"])
        .size()
        .reset_index(name="n")
    )
    by_group.to_csv(config.TABLES / "sinasc_chd_by_group_year.csv", index=False)

    other_cases = df[df["is_other_circulatory"]].copy()
    other_cases["other_code"] = other_cases["other_circulatory_codes"].fillna("").str.split(";")
    other_exploded = other_cases.explode("other_code")
    other_by_code = (
        other_exploded.groupby(["year", "other_code"]).size().reset_index(name="n")
        .sort_values(["year", "other_code"])
    )
    other_by_code.to_csv(config.TABLES / "sinasc_other_circulatory_by_code_year.csv", index=False)
    pd.DataFrame(
        columns=["other_code", "n"]
    ).to_csv(config.TABLES / "sinasc_other_circulatory_by_code.csv", index=False)
    if len(other_exploded):
        other_overall = (
            other_exploded.groupby("other_code").size().reset_index(name="n").sort_values("n", ascending=False)
        )
        other_overall.to_csv(config.TABLES / "sinasc_other_circulatory_by_code.csv", index=False)

    # Maternal / neonatal characteristics: core CHD, Q27-Q28, and neither.
    char_rows = []
    groups = [
        ("chd_core", cases),
        ("other_circulatory", other_cases),
        ("non_circulatory", df[~df["is_chd"] & ~df["is_other_circulatory"]]),
    ]
    for label, sub in groups:
        char_rows.append(
            {
                "group": label,
                "n": len(sub),
                "maternal_age_mean": round(sub["idademae"].mean(), 2) if len(sub) else "",
                "maternal_age_missing_pct": round(100 * sub["idademae"].isna().mean(), 2) if len(sub) else "",
                "birthweight_mean_g": round(sub["peso"].mean(), 1) if len(sub) else "",
                "birthweight_missing_pct": round(100 * sub["peso"].isna().mean(), 2) if len(sub) else "",
                "preterm_pct": round(
                    100 * (sub["semagestac"] < 37).sum() / sub["semagestac"].notna().sum(), 2
                )
                if sub["semagestac"].notna().sum()
                else "",
                "male_pct": round(100 * (sub["sexo"] == "1").sum() / len(sub), 2) if len(sub) else "",
                "cesarean_pct": round(100 * (sub["parto"] == "2").sum() / len(sub), 2) if len(sub) else "",
                "multiple_pregnancy_pct": round(100 * (sub["tipo_gravidez"] == "2").sum() / len(sub), 2)
                if len(sub)
                else "",
            }
        )
    write_csv(config.TABLES / "sinasc_maternal_neonatal.csv", char_rows)

    qa = {
        "n_births": int(len(df)),
        "n_chd_core_q20_q26": int(df["is_chd"].sum()),
        "n_other_circulatory_q27_q28": int(df["is_other_circulatory"].sum()),
        "n_circulatory_total_q20_q28": int((df["is_chd"] | df["is_other_circulatory"]).sum()),
        "n_records_in_both_groups": int((df["is_chd"] & df["is_other_circulatory"]).sum()),
        "n_non_circulatory": int((~df["is_chd"] & ~df["is_other_circulatory"]).sum()),
        "n_records_with_any_icd_code": int((df["n_icd_codes"] > 0).sum()),
        "n_chd_with_multiple_chd_codes": int((df["chd_codes"].str.count(";") >= 1).sum()),
        "idanomal_1_but_no_code": int(((df["idanomal"] == "1") & (df["n_icd_codes"] == 0)).sum()),
        "chd_with_idanomal_not_1": int((df["is_chd"] & (df["idanomal"] != "1")).sum()),
        "conception_estimated_pct": round(100 * (df["conception_date_est"] != "").mean(), 2),
        "conception_lag_days": CONCEPTION_LAG_DAYS,
        "ga_uncertainty_days": GA_UNCERTAINTY_DAYS,
        "gestation_source_counts": {
            str(k): int(v) for k, v in df["gestation_source"].value_counts().items()
        } if "gestation_source" in df.columns else {},
        "years_available": sorted(int(y) for y in df["year"].unique()),
        "years_missing": config.SINASC_YEARS_MISSING,
        "retrieved_at": today(),
    }
    write_json(config.DATA_PROCESSED / "sinasc_quality_report.json", qa)
    log.info("SINASC quality: %s", qa)
    return qa
