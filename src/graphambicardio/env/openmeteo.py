"""Meteorological series for Campos dos Goytacazes.

Source: ERA5-Land reanalysis distributed by the Open-Meteo Historical Weather
API (open, no credential).  The model is requested explicitly
(``models=era5_land``); the API default "best match" is not used.  Reanalysis
is **not** a local weather station: it represents a ~9 km grid cell and is used
as an area-level exposure proxy.  INMET A607 is used separately for validation.

PM2.5 has no local monitoring series in the municipality; no series is
fabricated.  See docs/09_LIMITATIONS_AND_GAPS.md.
"""

from __future__ import annotations

from datetime import date
from typing import Any

import numpy as np
import pandas as pd

from .. import config
from ..io_utils import get_json, get_logger, today, utc_now, write_csv, write_json

log = get_logger("climate")

DAILY_VARS = [
    "temperature_2m_mean",
    "temperature_2m_max",
    "temperature_2m_min",
    "relative_humidity_2m_mean",
    "precipitation_sum",
    "wind_speed_10m_max",
]


def fetch_daily(start: str = "2010-01-01", end: str = "2025-12-31") -> pd.DataFrame:
    params = {
        "latitude": config.MUNICIPALITY["latitude"],
        "longitude": config.MUNICIPALITY["longitude"],
        "start_date": start,
        "end_date": end,
        "daily": ",".join(DAILY_VARS),
        "timezone": config.MUNICIPALITY["timezone"],
        # Explicit model: do not rely on the API's "best_match" default.
        "models": config.OPEN_METEO_MODEL,
    }
    data = get_json(config.OPEN_METEO_ARCHIVE, params)
    daily = data.get("daily", {})
    df = pd.DataFrame(daily)
    df["date"] = pd.to_datetime(df["time"])
    df = df.drop(columns=["time"])
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    meta = {
        "source": f"Open-Meteo Historical Weather API — {config.OPEN_METEO_MODEL_LABEL}",
        "api_url": config.OPEN_METEO_ARCHIVE,
        "model_requested": config.OPEN_METEO_MODEL,
        "model_label": config.OPEN_METEO_MODEL_LABEL,
        "model_resolution_km": config.OPEN_METEO_RESOLUTION_KM,
        "latitude_requested": config.MUNICIPALITY["latitude"],
        "longitude_requested": config.MUNICIPALITY["longitude"],
        "latitude_returned": data.get("latitude"),
        "longitude_returned": data.get("longitude"),
        "elevation_m": data.get("elevation"),
        "timezone": data.get("timezone"),
        "utc_offset_seconds": data.get("utc_offset_seconds"),
        "timezone_abbreviation": data.get("timezone_abbreviation"),
        "start": start,
        "end": end,
        "n_days": len(df),
        "daily_units": data.get("daily_units", {}),
        "retrieved_at": utc_now(),
        "documentation": "https://open-meteo.com/en/docs/historical-weather-api",
        "note": "Model fixed explicitly to era5_land; returned grid cell may differ from the requested coordinates.",
    }
    write_json(config.DATA_RAW / "external" / "climate_source_metadata.json", meta)
    log.info(
        "climate: %s days, %s..%s, model=%s, returned cell=(%s,%s), elevation=%s m",
        len(df), df["date"].min().date(), df["date"].max().date(),
        config.OPEN_METEO_MODEL, data.get("latitude"), data.get("longitude"), data.get("elevation"),
    )
    return df


def add_heatwave_flags(df: pd.DataFrame) -> pd.DataFrame:
    """Heat wave: >=3 consecutive days with Tmax above the 90th percentile (2010-2025)."""
    thr = float(np.nanpercentile(df["temperature_2m_max"], 90))
    df = df.copy()
    df["tmax_p90"] = thr
    hot = (df["temperature_2m_max"] >= thr).to_numpy()
    in_wave = np.zeros(len(df), dtype=int)
    i = 0
    wave_id = 0
    while i < len(df):
        if hot[i]:
            j = i
            while j < len(df) and hot[j]:
                j += 1
            if j - i >= 3:
                wave_id += 1
                in_wave[i:j] = wave_id
            i = j
        else:
            i += 1
    df["heatwave_id"] = in_wave
    df["heat_day_35"] = (df["temperature_2m_max"] >= 35).astype(int)
    df["cold_day_15"] = (df["temperature_2m_min"] <= 15).astype(int)
    df["diurnal_range"] = df["temperature_2m_max"] - df["temperature_2m_min"]
    df.attrs["heatwave_threshold_p90"] = thr
    return df


def monthly(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby(["year", "month"])
    out = g.agg(
        tmean=("temperature_2m_mean", "mean"),
        tmax_mean=("temperature_2m_max", "mean"),
        tmax_max=("temperature_2m_max", "max"),
        tmin_mean=("temperature_2m_min", "mean"),
        tmin_min=("temperature_2m_min", "min"),
        rh_mean=("relative_humidity_2m_mean", "mean"),
        precip_total=("precipitation_sum", "sum"),
        heat_days_35=("heat_day_35", "sum"),
        cold_days_15=("cold_day_15", "sum"),
        heatwave_days=("heatwave_id", lambda s: int((s > 0).sum())),
        diurnal_range_mean=("diurnal_range", "mean"),
    ).reset_index()
    out["period"] = out["year"].astype(str) + "-" + out["month"].astype(str).str.zfill(2)
    return out


def annual(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby("year")
    out = g.agg(
        tmean=("temperature_2m_mean", "mean"),
        tmax_mean=("temperature_2m_max", "mean"),
        tmax_max=("temperature_2m_max", "max"),
        tmin_mean=("temperature_2m_min", "mean"),
        rh_mean=("relative_humidity_2m_mean", "mean"),
        precip_total=("precipitation_sum", "sum"),
        heat_days_35=("heat_day_35", "sum"),
        cold_days_15=("cold_day_15", "sum"),
        heatwave_days=("heatwave_id", lambda s: int((s > 0).sum())),
        n_heatwaves=("heatwave_id", lambda s: int(s[s > 0].nunique())),
    ).reset_index()
    return out


def build() -> tuple[pd.DataFrame, pd.DataFrame]:
    daily = fetch_daily()
    daily = add_heatwave_flags(daily)
    daily.to_csv(config.DATA_PROCESSED / "climate_daily_campos.csv", index=False)
    mon = monthly(daily)
    mon.to_csv(config.DATA_PROCESSED / "climate_monthly_campos.csv", index=False)
    ann = annual(daily)
    ann.to_csv(config.TABLES / "climate_annual_campos.csv", index=False)
    qa: dict[str, Any] = {
        "model": config.OPEN_METEO_MODEL,
        "model_label": config.OPEN_METEO_MODEL_LABEL,
        "model_resolution_km": config.OPEN_METEO_RESOLUTION_KM,
        "n_days": int(len(daily)),
        "n_missing_tmax": int(daily["temperature_2m_max"].isna().sum()),
        "heatwave_threshold_p90_tmax": daily.attrs.get("heatwave_threshold_p90"),
        "n_heatwave_days": int((daily["heatwave_id"] > 0).sum()),
        "n_heatwaves": int(daily["heatwave_id"].nunique()),
        "years": [int(y) for y in sorted(daily["year"].unique())],
        "retrieved_at": today(),
    }
    write_json(config.DATA_PROCESSED / "climate_quality_report.json", qa)
    log.info("climate QA: %s", qa)
    return daily, mon
