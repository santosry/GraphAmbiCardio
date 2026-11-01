"""Tests for FDR helpers, model schema and published aggregates."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from graphambicardio.epi import models  # noqa: E402
from graphambicardio.stats.fdr import bh_fdr  # noqa: E402


def test_bh_fdr_known_values():
    p = [0.01, 0.02, 0.03, 0.04, 0.05]
    q = bh_fdr(p)
    assert len(q) == len(p)
    assert all(0 <= x <= 1 for x in q)
    assert all(qi >= pi - 1e-12 for qi, pi in zip(q, p))
    assert q == sorted(q)


def test_bh_fdr_empty_and_singleton():
    assert bh_fdr([]) == []
    assert bh_fdr([0.05]) == pytest.approx([0.05])


def test_add_fdr_attaches_q_values():
    results = [
        {"model": "a", "p_value": 0.01},
        {"model": "b", "p_value": 0.04},
        {"model": "c", "exposure_1_p": 0.02, "exposure_2_p": 0.03},
        {"model": "d"},
    ]
    out = models.add_fdr(results)
    assert out[0]["q_value"] >= out[0]["p_value"] - 1e-12
    assert "exposure_1_q" in out[2] and "exposure_2_q" in out[2]
    assert "q_value" not in out[3]


def test_male_indicator_accepts_string_and_numeric():
    out_str = models._male(pd.Series(["1", "2", None]))
    out_num = models._male(pd.Series([1, 2, None]))
    assert out_str.iloc[0] == 1 and out_str.iloc[1] == 0 and pd.isna(out_str.iloc[2])
    assert out_num.iloc[0] == 1 and out_num.iloc[1] == 0 and pd.isna(out_num.iloc[2])


def test_male_indicator_unknown_is_missing_not_female():
    out = models._male(pd.Series(["1", "2", "9", "", None, "0"]))
    assert out.iloc[0] == 1
    assert out.iloc[1] == 0
    assert out.iloc[2:].isna().all()


def test_model_frame_rejects_missing_exposure():
    df = pd.DataFrame({
        "win_temperature_2m_max_mean": [1.0, np.nan],
        "idademae": [20, 30],
        "year": [2020, 2021],
        "sexo": ["1", "2"],
        "is_chd": [True, False],
        "conception_date_est": ["2020-01-01", "2021-01-01"],
    })
    d = models._model_frame(df, "win_temperature_2m_max_mean")
    assert len(d) == 1


def test_exposure_diagnostics_shapes():
    rng = np.random.default_rng(7)
    df = pd.DataFrame({name: rng.normal(size=40) for name in [
        "win_temperature_2m_max_mean",
        "win_temperature_2m_min_mean",
        "win_heat_days_35_pct",
        "win_relative_humidity_2m_mean_mean",
        "win_pm25_mean",
    ]})
    corr, vif = models.exposure_diagnostics(df)
    assert corr.shape == (5, 5)
    assert list(vif.columns) == ["exposure", "vif"]
    assert len(vif) == 5


def test_published_pm25_series_complete():
    monthly = pd.read_csv(ROOT / "data_processed" / "pm25_campos_mensal.csv")
    annual = pd.read_csv(ROOT / "data_processed" / "pm25_campos_anual.csv")
    assert len(monthly) == 192
    assert not monthly.duplicated(["ano", "mes"]).any()
    assert monthly["pm25_ug_m3"].between(0, 500).all()
    assert set(annual["ano"]) == set(range(2010, 2026))


def test_individual_data_not_in_app_bundle():
    names = {p.name for p in (ROOT / "app" / "data").glob("*")}
    forbidden = {"sinasc_campos_births.csv", "sinasc_campos_with_exposure.csv", "sih_campos_chd_admissions.csv"}
    assert not (names & forbidden)


def test_fair_checksums_match():
    dp = json.loads((ROOT / "fair" / "datapackage.json").read_text(encoding="utf-8"))
    import hashlib

    for r in dp["resources"]:
        p = ROOT / r["path"]
        assert p.exists(), r["path"]
        digest = hashlib.sha256(p.read_bytes().replace(bytes((13, 10)), bytes((10)))).hexdigest()
        assert digest == r["hash"].replace("sha256:", ""), r["path"]
