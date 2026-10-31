"""Record what pySUS exposes for SINASC, including 2023-2024."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from graphambicardio.epi import pysus_fetch  # noqa: E402

if __name__ == "__main__":
    for row in pysus_fetch.probe_sinasc([2020, 2023, 2024, 2025]):
        print(row)
