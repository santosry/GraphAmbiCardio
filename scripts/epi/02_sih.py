"""Build the SIH/SUS CHD admission dataset and indicators for Campos dos Goytacazes."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from graphambicardio.epi import sih  # noqa: E402
from graphambicardio.io_utils import get_logger, utc_now  # noqa: E402


def main() -> None:
    log = get_logger("run_sih")
    log.info("start %s", utc_now())
    sih.download_all()
    df = sih.build_dataset()
    if len(df):
        sih.summarise(df)
    log.info("done %s", utc_now())


if __name__ == "__main__":
    main()
