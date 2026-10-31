"""Supplement the SINASC annual series with 2023-2024 TabNet aggregates."""
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
    agg = pd.DataFrame(rows)
    annual = pd.read_csv(config.TABLES / "sinasc_annual.csv")
    annual["source"] = "SINASC microdata (any Q20-Q28 code)"
    extra = []
    for _, r in agg.iterrows():
        y = int(r["year"])
        if y in set(annual["year"].astype(int)):
            continue
        extra.append({
            "year": y,
            "live_births": int(r["live_births"]),
            "chd_cases": int(r["circulatory_cases"]),
            "chd_per_10000_lb": r["per_10000_lb"],
            "chd_proportion_per_1000_lb": round(1000 * r["circulatory_cases"] / r["live_births"], 2),
            "anomaly_flag_1": "",
            "any_q_code": "",
            "data_status": "aggregate only (microdata unavailable)",
            "source": "SINASC via DATASUS TabNet (group Q20-Q28)",
        })
    out = pd.concat([annual, pd.DataFrame(extra)], ignore_index=True).sort_values("year")
    out.to_csv(config.TABLES / "sinasc_annual_complete.csv", index=False)
    coverage = out[["year", "live_births", "chd_cases", "data_status", "source"]].copy()
    coverage.to_csv(config.REPORTS / "sinasc_coverage.csv", index=False)
    log.info("annual series: %s rows -> %s", len(out), config.TABLES / "sinasc_annual_complete.csv")


if __name__ == "__main__":
    main()
