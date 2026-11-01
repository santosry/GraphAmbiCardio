"""Supplement the core SINASC series with TabNet aggregates without mixing definitions.

TabNet reports the broad group "malformações congênitas do aparelho
circulatório" (Q20-Q28).  The microdata case definition used here is the core
CHD group Q20-Q26; Q27-Q28 are analysed separately.  Therefore TabNet values
are stored in dedicated columns and are **never** copied into ``chd_cases``.
For 2023-2024, where microdata are unavailable, the core CHD series is left
missing rather than filled with a non-comparable aggregate.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from graphambicardio import config  # noqa: E402
from graphambicardio.epi import tabnet  # noqa: E402
from graphambicardio.io_utils import get_logger  # noqa: E402


def main() -> None:
    log = get_logger("tabnet_supplement")
    rows = tabnet.build([2022, 2023, 2024, 2025])
    agg = pd.DataFrame(rows).rename(
        columns={
            "live_births": "live_births_tabnet",
            "circulatory_cases": "tabnet_circulatory_cases",
            "per_10000_lb": "tabnet_circulatory_per_10000_lb",
            "data_status": "tabnet_data_status",
            "case_definition": "tabnet_case_definition",
            "source": "tabnet_source",
        }
    )
    annual = pd.read_csv(config.TABLES / "sinasc_annual.csv")
    annual["source"] = "SINASC microdata (core CHD Q20-Q26)"
    out = annual.merge(agg, on="year", how="outer").sort_values("year")

    # Years without microdata: keep the core CHD outcome missing and expose the
    # broad TabNet aggregate only in its own columns.
    missing_microdata = out["chd_cases"].isna()
    out.loc[missing_microdata, "live_births"] = out.loc[missing_microdata, "live_births_tabnet"]
    out.loc[missing_microdata, "data_status"] = "aggregate only (broad Q20-Q28)"
    out.loc[missing_microdata, "source"] = "SINASC via TabNet (broad Q20-Q28; not CHD core)"
    out.loc[missing_microdata, "chd_cases"] = pd.NA
    out.loc[missing_microdata, "chd_per_10000_lb"] = pd.NA
    out.loc[missing_microdata, "chd_proportion_per_1000_lb"] = pd.NA
    out.loc[missing_microdata, "other_circulatory_cases"] = pd.NA
    out.loc[missing_microdata, "other_circulatory_per_10000_lb"] = pd.NA
    out.loc[missing_microdata, "circulatory_cases_total"] = pd.NA
    out.loc[missing_microdata, "circulatory_per_10000_lb"] = pd.NA

    out = out.sort_values("year")
    out.to_csv(config.TABLES / "sinasc_annual_complete.csv", index=False)
    coverage = out[
        [
            "year", "live_births", "chd_cases", "chd_per_10000_lb",
            "other_circulatory_cases", "tabnet_circulatory_cases",
            "tabnet_circulatory_per_10000_lb", "data_status", "source",
        ]
    ].copy()
    coverage.to_csv(config.REPORTS / "sinasc_coverage.csv", index=False)
    log.info("annual series: %s rows -> %s", len(out), config.TABLES / "sinasc_annual_complete.csv")


if __name__ == "__main__":
    main()
