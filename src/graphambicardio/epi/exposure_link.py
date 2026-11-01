"""Link area-level climate exposures to the individual gestational window.

Each birth has an estimated conception date (from gestational age) and an
estimated cardiac organogenesis window (weeks 3-8 post-conception).  Daily
gridded temperature for the municipality is averaged over that window.

The resulting exposure is still **area-level**: every birth in the same window
receives the same value.  It is not personal exposure, and the analysis is
therefore an ecological-exposure design with individual outcome data.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from .. import config
from ..io_utils import get_logger, write_csv, write_json

log = get_logger("exposure_link")

COLS = ["temperature_2m_max", "temperature_2m_mean", "temperature_2m_min", "relative_humidity_2m_mean", "pm25"]


def _cum(arr: np.ndarray) -> np.ndarray:
    out = np.zeros(len(arr) + 1, dtype=float)
    out[1:] = np.nancumsum(arr)
    return out


def _attach_window(
    births: pd.DataFrame,
    daily: pd.DataFrame,
    dates: np.ndarray,
    start_col: str,
    end_col: str,
    suffix: str = "",
) -> pd.DataFrame:
    starts = pd.to_datetime(births[start_col], errors="coerce")
    ends = pd.to_datetime(births[end_col], errors="coerce")
    valid_window = starts.notna() & ends.notna()
    starts_np = starts.to_numpy(dtype="datetime64[D]")
    ends_np = ends.to_numpy(dtype="datetime64[D]")
    idx_s = np.searchsorted(dates, starts_np, side="left")
    idx_e = np.searchsorted(dates, ends_np, side="right")
    n = np.where(valid_window, idx_e - idx_s, 0).astype(float)
    lo = np.clip(idx_s, 0, len(dates))
    hi = np.clip(idx_e, 0, len(dates))

    for col in COLS:
        vals = daily[col].to_numpy(dtype=float)
        cs = _cum(vals)
        valid = (~np.isnan(vals)).astype(float)
        csv = _cum(valid)
        with np.errstate(invalid="ignore", divide="ignore"):
            mean = np.where(n > 0, (cs[hi] - cs[lo]) / np.maximum(n, 1), np.nan)
            frac_valid = np.where(n > 0, (csv[hi] - csv[lo]) / np.maximum(n, 1), np.nan)
        births[f"win_{col}_mean{suffix}"] = mean
        if col == "temperature_2m_max":
            hot = (vals >= 35).astype(float)
            hot[np.isnan(vals)] = np.nan
            ch = _cum(hot)
            births[f"win_heat_days_35_pct{suffix}"] = np.where(
                n > 0, (ch[hi] - ch[lo]) / np.maximum(n, 1), np.nan
            )
            births[f"win_covariate_completeness{suffix}"] = frac_valid
    return births


def attach(daily: pd.DataFrame, births: pd.DataFrame) -> pd.DataFrame:
    daily = daily.sort_values("date").reset_index(drop=True)
    dates = pd.to_datetime(daily["date"]).to_numpy(dtype="datetime64[D]")
    births = births.copy()
    births = _attach_window(
        births, daily, dates, "organogenesis_start_est", "organogenesis_end_est", ""
    )
    # Sensitivity windows: gestational age uncertainty of +/- 7 days.
    for suffix, start_col, end_col in (
        ("_early", "organogenesis_start_early", "organogenesis_end_early"),
        ("_late", "organogenesis_start_late", "organogenesis_end_late"),
    ):
        if start_col in births.columns and end_col in births.columns:
            births = _attach_window(births, daily, dates, start_col, end_col, suffix)
    log.info(
        "exposure attached to %s births (%s with main window; %s early; %s late)",
        len(births),
        int(births["win_temperature_2m_max_mean"].notna().sum()),
        int(births.get("win_temperature_2m_max_mean_early", pd.Series(dtype=float)).notna().sum()),
        int(births.get("win_temperature_2m_max_mean_late", pd.Series(dtype=float)).notna().sum()),
    )
    return births


def summarise(births: pd.DataFrame) -> dict[str, Any]:
    rows = []
    for label, sub in (("all", births), ("chd", births[births["is_chd"]]), ("non_chd", births[~births["is_chd"]])):
        rows.append(
            {
                "group": label,
                "n": len(sub),
                "tmax_window_mean": round(sub["win_temperature_2m_max_mean"].mean(), 3),
                "tmax_window_sd": round(sub["win_temperature_2m_max_mean"].std(), 3),
                "tmin_window_mean": round(sub["win_temperature_2m_min_mean"].mean(), 3),
                "rh_window_mean": round(sub["win_relative_humidity_2m_mean_mean"].mean(), 3),
                "heat_days_35_pct_window": round(sub["win_heat_days_35_pct"].mean(), 4),
                "pm25_window_mean": round(sub["win_pm25_mean"].mean(), 3),
                "window_coverage_mean": round(sub["win_covariate_completeness"].mean(), 3),
            }
        )
    write_csv(config.TABLES / "gestational_window_exposure_summary.csv", rows)
    qa = {
        "n_births": len(births),
        "n_with_window": int(births["win_temperature_2m_max_mean"].notna().sum()),
        "window_coverage_mean": round(float(births["win_covariate_completeness"].mean()), 4)
        if births["win_covariate_completeness"].notna().any()
        else None,
        "note": "Area-level ERA5-Land exposure assigned to an individual gestational window; not personal exposure.",
    }
    write_json(config.DATA_PROCESSED / "exposure_link_quality.json", qa)
    return qa
