"""Run network analyses and write tables."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from graphambicardio.graph import analysis  # noqa: E402

if __name__ == "__main__":
    analysis.main()
