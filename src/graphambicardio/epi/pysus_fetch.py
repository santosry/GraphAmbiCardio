"""pySUS probe for SINASC microdata availability.

The study uses pySUS (pysus 2.x) as the official Python client for DATASUS.
Some years are not exposed by the pySUS origins; this module records exactly
what pySUS can see so that any fallback (e.g. TabNet aggregate) is explicit.
"""

from __future__ import annotations

import json
from typing import Any

from .. import config
from ..io_utils import today, write_json


def probe_sinasc(years: list[int] | None = None) -> list[dict[str, Any]]:
    years = years or [2023, 2024]
    rows = []
    try:
        import pysus  # noqa: F401

        pysus.set_cache(str(config.DATA_RAW / "cache"))
    except Exception as exc:  # noqa: BLE001
        return [{"year": y, "error": f"pysus import/cache: {exc}"} for y in years]
    for y in years:
        row: dict[str, Any] = {"year": y, "source": "pysus.ftp.sinasc (origin FTP)"}
        try:
            files = pysus.ftp.sinasc("RJ", y, source="origin", download=False)
            files = [str(f) for f in files]
            row["n_files"] = len(files)
            row["files"] = files[:5]
            row["available"] = len(files) > 0
        except Exception as exc:  # noqa: BLE001
            row["available"] = False
            row["error"] = str(exc)[:300]
        rows.append(row)
    write_json(config.REPORTS / "pysus_sinasc_audit.json", {"retrieved_at": today(), "years": rows})
    return rows
