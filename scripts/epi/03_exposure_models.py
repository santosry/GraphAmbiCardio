"""Attach gestational-window climate exposure and fit exploratory models."""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from graphambicardio.epi import exposure_link, models  # noqa: E402
from graphambicardio.io_utils import get_logger, utc_now  # noqa: E402


def main() -> None:
    log = get_logger("run_exposure_models")
    log.info("start %s", utc_now())
    births = pd.read_csv("data_processed/sinasc_campos_births.csv")
    daily = pd.read_csv("data_processed/climate_daily_campos.csv")
    pm = pd.read_csv("data_processed/pm25_campos_mensal.csv")
    daily["year"] = pd.to_datetime(daily["date"]).dt.year
    daily["month"] = pd.to_datetime(daily["date"]).dt.month
    daily = daily.merge(
        pm.rename(columns={"ano": "year", "mes": "month", "pm25_ug_m3": "pm25"}),
        on=["year", "month"], how="left"
    )
    pm.to_csv("outputs/tables/pm25_monthly_campos.csv", index=False)
    pd.read_csv("data_processed/pm25_campos_anual.csv").to_csv("outputs/tables/pm25_annual_campos.csv", index=False)
    with_exp = exposure_link.attach(daily, births)
    with_exp.to_csv("data_processed/sinasc_campos_with_exposure.csv", index=False)
    exposure_link.summarise(with_exp)
    models.run(with_exp)
    log.info("done %s", utc_now())


if __name__ == "__main__":
    main()
