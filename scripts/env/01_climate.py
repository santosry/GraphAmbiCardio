"""Download and aggregate the ERA5-Land meteorological series for Campos."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from graphambicardio.env import openmeteo  # noqa: E402
from graphambicardio.io_utils import get_logger, utc_now  # noqa: E402

log = get_logger("run_climate")
log.info("start %s", utc_now())
openmeteo.build()
log.info("done %s", utc_now())
