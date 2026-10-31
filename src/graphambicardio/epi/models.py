"""Exploratory ecological-exposure models for the local dataset.

The number of CHD events in a single municipality is small (tens of cases over
the period).  The models below are therefore explicitly **exploratory**, use a
small number of parameters, and are reported with confidence intervals rather
than as confirmatory tests.

Two complementary specifications are fitted:
  (1) birth-level logistic regression of CHD on the gestational-window
      area-level exposure, adjusted for year and maternal age;
  (2) monthly negative-binomial (or Poisson, if not overdispersed) regression
      of CHD counts by month of conception with log(live births) as offset.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

from .. import config
from ..io_utils import get_logger, write_csv, write_json

log = get_logger("models")


def _z(s: pd.Series) -> pd.Series:
    sd = s.std()
    return (s - s.mean()) / sd if sd and not np.isnan(sd) else s * 0


def logistic(df: pd.DataFrame, exposure: str) -> dict[str, Any]:
    d = df.dropna(subset=[exposure, "idademae", "year"]).copy()
    d["y"] = d["is_chd"].astype(int)
    d["z_exp"] = _z(d[exposure])
    d["year_c"] = d["year"] - d["year"].mean()
    d["age_c"] = d["idademae"] - d["idademae"].mean()
    d["male"] = (d["sexo"] == "1").astype(int)
    try:
        m = smf.logit("y ~ z_exp + year_c + age_c + male", data=d).fit(disp=0, maxiter=200)
        coef = m.params["z_exp"]
        ci = m.conf_int().loc["z_exp"]
        iqr = d[exposure].quantile(0.75) - d[exposure].quantile(0.25)
        or_iqr = float(np.exp(coef * iqr / d[exposure].std()))
        ci_iqr = (float(np.exp(ci[0] * iqr / d[exposure].std())), float(np.exp(ci[1] * iqr / d[exposure].std())))
        return {
            "model": "logistic_birth_level",
            "exposure": exposure,
            "n": int(len(d)),
            "n_events": int(d["y"].sum()),
            "or_per_sd": round(float(np.exp(coef)), 3),
            "or_per_sd_ci95": [round(float(np.exp(ci[0])), 3), round(float(np.exp(ci[1])), 3)],
            "p_value": round(float(m.pvalues["z_exp"]), 4),
            "iqr": round(float(iqr), 3),
            "or_per_iqr": round(or_iqr, 3),
            "or_per_iqr_ci95": [round(ci_iqr[0], 3), round(ci_iqr[1], 3)],
            "converged": bool(m.mle_retvals.get("converged", False)),
            "adjustment": "year (linear) + maternal age (linear) + infant sex",
        }
    except Exception as exc:  # noqa: BLE001
        log.warning("logistic failed (%s): %s", exposure, exc)
        return {"model": "logistic_birth_level", "exposure": exposure, "error": str(exc)}


def logistic_two_exposures(df: pd.DataFrame, exp1: str, exp2: str) -> dict[str, Any]:
    """Mutual-adjustment model for two correlated area-level exposures."""
    d = df.dropna(subset=[exp1, exp2, "idademae", "year"]).copy()
    d["y"] = d["is_chd"].astype(int)
    d["z1"] = _z(d[exp1]); d["z2"] = _z(d[exp2])
    d["year_c"] = d["year"] - d["year"].mean()
    d["age_c"] = d["idademae"] - d["idademae"].mean()
    d["male"] = (d["sexo"] == "1").astype(int)
    try:
        m = smf.logit("y ~ z1 + z2 + year_c + age_c + male", data=d).fit(disp=0, maxiter=200)
        out = {"model": "logistic_two_exposures", "exposure_1": exp1, "exposure_2": exp2,
               "n": int(len(d)), "n_events": int(d["y"].sum()), "adjustment": "mutual + year + age + sex"}
        for key, label in (("z1", "exposure_1"), ("z2", "exposure_2")):
            ci = m.conf_int().loc[key]
            out[f"{label}_or_per_sd"] = round(float(np.exp(m.params[key])), 3)
            out[f"{label}_ci95"] = [round(float(np.exp(ci[0])), 3), round(float(np.exp(ci[1])), 3)]
            out[f"{label}_p"] = round(float(m.pvalues[key]), 4)
        out["converged"] = bool(m.mle_retvals.get("converged", False))
        return out
    except Exception as exc:  # noqa: BLE001
        return {"model": "logistic_two_exposures", "error": str(exc)}


def logistic_season_adjusted(df: pd.DataFrame, exposure: str) -> dict[str, Any]:
    """Sensitivity model adding quarter-of-conception fixed effects."""
    d = df.dropna(subset=[exposure, "idademae", "year", "conception_date_est"]).copy()
    d["y"] = d["is_chd"].astype(int)
    d["z_exp"] = _z(d[exposure])
    d["year_c"] = d["year"] - d["year"].mean()
    d["age_c"] = d["idademae"] - d["idademae"].mean()
    d["male"] = (d["sexo"] == "1").astype(int)
    month = pd.to_datetime(d["conception_date_est"]).dt.month
    d["quarter"] = ((month - 1) // 3 + 1).astype(str)
    try:
        m = smf.logit("y ~ z_exp + year_c + age_c + male + C(quarter)", data=d).fit(disp=0, maxiter=200)
        coef = m.params["z_exp"]
        ci = m.conf_int().loc["z_exp"]
        iqr = d[exposure].quantile(0.75) - d[exposure].quantile(0.25)
        return {
            "model": "logistic_season_adjusted",
            "exposure": exposure,
            "n": int(len(d)),
            "n_events": int(d["y"].sum()),
            "or_per_sd": round(float(np.exp(coef)), 3),
            "or_per_sd_ci95": [round(float(np.exp(ci[0])), 3), round(float(np.exp(ci[1])), 3)],
            "p_value": round(float(m.pvalues["z_exp"]), 4),
            "or_per_iqr": round(float(np.exp(coef * iqr / d[exposure].std())), 3),
            "adjustment": "year + maternal age + sex + quarter of conception",
            "converged": bool(m.mle_retvals.get("converged", False)),
        }
    except Exception as exc:  # noqa: BLE001
        return {"model": "logistic_season_adjusted", "exposure": exposure, "error": str(exc)}


def negative_binomial(births: pd.DataFrame) -> dict[str, Any]:
    """Monthly CHD counts by month of conception vs monthly mean Tmax."""
    d = births.dropna(subset=["win_temperature_2m_max_mean", "conception_date_est"]).copy()
    d["conception_date"] = pd.to_datetime(d["conception_date_est"])
    d["period"] = d["conception_date"].dt.to_period("M").astype(str)
    g = d.groupby("period").agg(
        births=("is_chd", "size"),
        cases=("is_chd", "sum"),
        tmax=("win_temperature_2m_max_mean", "mean"),
    ).reset_index()
    g = g[g["births"] >= 30].copy()
    g["year"] = g["period"].str[:4].astype(int)
    g["month"] = g["period"].str[5:7].astype(int)
    g["z_tmax"] = _z(g["tmax"])
    g["year_c"] = g["year"] - g["year"].mean()
    g["log_births"] = np.log(g["births"])
    out: dict[str, Any] = {
        "model": "monthly_count_conception_month",
        "n_months": int(len(g)),
        "total_cases": int(g["cases"].sum()),
        "exposure": "area-level mean Tmax during the organogenesis window (monthly mean)",
    }
    if g["cases"].sum() < 10:
        out["error"] = "too few events for a monthly model"
        return out
    try:
        pois = smf.glm("cases ~ z_tmax + year_c", data=g, family=sm.families.Poisson(), offset=g["log_births"]).fit()
        dispersion = float(pois.pearson_chi2 / pois.df_resid)
        out["poisson_dispersion"] = round(dispersion, 3)
        if dispersion > 1.5:
            nb = smf.negativebinomial("cases ~ z_tmax + year_c", data=g, offset=g["log_births"]).fit(disp=0, maxiter=200)
            m = nb
            out["family"] = "negative_binomial"
        else:
            m = pois
            out["family"] = "poisson"
        coef = m.params["z_tmax"]
        ci = m.conf_int().loc["z_tmax"]
        iqr = g["tmax"].quantile(0.75) - g["tmax"].quantile(0.25)
        out.update(
            {
                "rr_per_sd": round(float(np.exp(coef)), 3),
                "rr_per_sd_ci95": [round(float(np.exp(ci[0])), 3), round(float(np.exp(ci[1])), 3)],
                "p_value": round(float(m.pvalues["z_tmax"]), 4),
                "iqr": round(float(iqr), 3),
                "rr_per_iqr": round(float(np.exp(coef * iqr / g["tmax"].std())), 3),
            }
        )
        g.to_csv(config.TABLES / "model_monthly_dataset.csv", index=False)
    except Exception as exc:  # noqa: BLE001
        out["error"] = str(exc)
        log.warning("monthly model failed: %s", exc)
    return out


def run(births: pd.DataFrame) -> list[dict[str, Any]]:
    exposures = [
        "win_temperature_2m_max_mean",
        "win_temperature_2m_min_mean",
        "win_heat_days_35_pct",
        "win_relative_humidity_2m_mean_mean",
        "win_pm25_mean",
    ]
    results = [logistic(births, e) for e in exposures]
    results.append(logistic_two_exposures(births, "win_pm25_mean", "win_temperature_2m_max_mean"))
    results.append(logistic_season_adjusted(births, "win_temperature_2m_max_mean"))
    results.append(negative_binomial(births))
    # leave-one-year-out sensitivity for the season-adjusted model
    loo = []
    for y in sorted(births["year"].unique()):
        r = logistic_season_adjusted(births[births["year"] != y], "win_temperature_2m_max_mean")
        loo.append({"excluded_year": int(y), "or_per_sd": r.get("or_per_sd"), "ci_low": (r.get("or_per_sd_ci95") or [None, None])[0], "ci_high": (r.get("or_per_sd_ci95") or [None, None])[1], "p_value": r.get("p_value"), "n_events": r.get("n_events")})
    write_csv(config.TABLES / "sensitivity_leave_one_year_out.csv", loo)
    results.append({"model": "leave_one_year_out", "exposure": "win_temperature_2m_max_mean", "results": loo})
    write_json(config.TABLES / "exploratory_models.json", results)
    write_csv(
        config.TABLES / "exploratory_models.csv",
        [{k: (v if not isinstance(v, list) else ";".join(map(str, v))) for k, v in r.items()} for r in results],
    )
    return results
