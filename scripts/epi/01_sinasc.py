"""Build the SINASC birth-level dataset and indicators for Campos dos Goytacazes."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from graphambicardio.epi import sinasc  # noqa: E402
from graphambicardio.io_utils import get_logger, utc_now  # noqa: E402

log = get_logger("run_sinasc")
log.info("start %s", utc_now())
sinasc.download_years()
df = sinasc.build_dataset()
if len(df):
    sinasc.summarise(df)
log.info("done %s", utc_now())
