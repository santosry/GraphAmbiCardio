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
    with_exp = exposure_link.attach(daily, births)
    with_exp.to_csv("data_processed/sinasc_campos_with_exposure.csv", index=False)
    exposure_link.summarise(with_exp)
    models.run(with_exp)
    log.info("done %s", utc_now())


if __name__ == "__main__":
    main()
