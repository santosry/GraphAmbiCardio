"""Fase A/C collection step 1: literature searches (PubMed + Europe PMC).

Run:  .venv/Scripts/python.exe scripts/collection/01_literature.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from graphambicardio.io_utils import get_logger, utc_now  # noqa: E402
from graphambicardio.literature import europepmc  # noqa: E402
from graphambicardio.literature.feasibility import (  # noqa: E402
    build_pair_matrix,
    domain_counts,
    exposure_mechanism_counts,
    exposure_summary,
)
from graphambicardio.literature.pubmed import domain_queries  # noqa: E402

log = get_logger("collect_literature")


def main() -> None:
    log.info("start %s", utc_now())
    log.info("== domain counts (Fase A, 5 connection domains)")
    domain_counts()

    log.info("== exposure x phenotype matrix")
    build_pair_matrix(retmax=15)

    log.info("== exposure x mechanism counts")
    exposure_mechanism_counts()

    log.info("== exposure summary")
    exposure_summary()

    log.info("== Europe PMC")
    for name, q in domain_queries().items():
        europepmc.run_search(name, q, page_size=100)

    log.info("done %s", utc_now())


if __name__ == "__main__":
    main()
