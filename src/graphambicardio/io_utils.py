"""HTTP, caching, logging and file helpers.

Every network response is cached on disk under ``data_raw/http_cache`` so that
the pipeline can be re-run offline and so that retrieval dates remain auditable.
"""

from __future__ import annotations

import hashlib
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

from . import config

# --------------------------------------------------------------------------
# Logging
# --------------------------------------------------------------------------
LOG_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter(LOG_FORMAT)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(sh)
    config.LOGS.mkdir(parents=True, exist_ok=True)
    fh = logging.FileHandler(config.LOGS / "pipeline.log", encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    return logger


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


# --------------------------------------------------------------------------
# Cached HTTP
# --------------------------------------------------------------------------
_SESSION: requests.Session | None = None


def session() -> requests.Session:
    global _SESSION
    if _SESSION is None:
        _SESSION = requests.Session()
        _SESSION.headers.update({"User-Agent": config.USER_AGENT})
    return _SESSION


def _cache_path(key: str) -> Path:
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:32]
    return config.DATA_RAW / "http_cache" / f"{digest}.txt"


def http_get(
    url: str,
    params: dict[str, Any] | None = None,
    *,
    cache: bool = True,
    timeout: int = config.HTTP_TIMEOUT,
    headers: dict[str, str] | None = None,
    retries: int = config.HTTP_RETRIES,
) -> str:
    """GET with on-disk cache and retries. Returns response text."""
    key = url + "?" + json.dumps(params or {}, sort_keys=True, ensure_ascii=False)
    path = _cache_path(key)
    if cache and path.exists():
        return path.read_text(encoding="utf-8")
    last_exc: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            r = session().get(url, params=params, timeout=timeout, headers=headers)
            if r.status_code >= 500:
                raise requests.HTTPError(f"HTTP {r.status_code}")
            r.raise_for_status()
            text = r.text
            if cache:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
            return text
        except Exception as exc:  # noqa: BLE001 - retry any transport error
            last_exc = exc
            time.sleep(min(2 ** attempt, 15))
    raise RuntimeError(f"GET failed after {retries} attempts: {url} params={params}: {last_exc}")


def http_post(
    url: str,
    *,
    data: str | None = None,
    params: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    cache: bool = True,
    timeout: int = config.HTTP_TIMEOUT,
    retries: int = config.HTTP_RETRIES,
) -> str:
    key = f"POST {url}?" + json.dumps(params or {}, sort_keys=True) + "#" + (data or "")
    path = _cache_path(key)
    if cache and path.exists():
        return path.read_text(encoding="utf-8")
    last_exc: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            r = session().post(url, data=data, params=params, headers=headers, timeout=timeout)
            r.raise_for_status()
            text = r.text
            if cache:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
            return text
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            time.sleep(min(2 ** attempt, 15))
    raise RuntimeError(f"POST failed after {retries} attempts: {url}: {last_exc}")


def get_json(url: str, params: dict[str, Any] | None = None, **kwargs: Any) -> Any:
    return json.loads(http_get(url, params, **kwargs))


# --------------------------------------------------------------------------
# Files
# --------------------------------------------------------------------------
def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False, default=str), encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    import csv

    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    if fieldnames is None:
        fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow(row)


def append_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    import csv

    exists = path.exists() and path.stat().st_size > 0
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        if not exists:
            w.writeheader()
        for row in rows:
            w.writerow(row)


def read_csv(path: Path) -> list[dict[str, str]]:
    import csv

    with path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def read_csv_df(path: Path):
    import pandas as pd

    return pd.read_csv(path)
