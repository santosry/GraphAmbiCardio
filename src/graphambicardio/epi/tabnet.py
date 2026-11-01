"""SINASC aggregates via DATASUS TabNet (2023-2025).

The DBC microdata for 2023 and 2024 are not exposed in the SINASC FTP tree,
but TabNet serves the consolidated files (`nvrj23.dbf`, `nvrj24.dbf`).  TabNet
counts records in the "malformações congênitas do aparelho circulatório" group
(Q20-Q28), which is broader than this study's core CHD definition (Q20-Q26).
The aggregate is therefore stored separately and is never imputed into the core
CHD series.

TabNet requires Latin-1 form encoding and a session handshake; both are
handled here.
"""

from __future__ import annotations

import re
import urllib.parse
from typing import Any

import requests
from bs4 import BeautifulSoup

from .. import config
from ..io_utils import get_logger, today, write_csv, write_json

log = get_logger("tabnet")

URL = "http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sinasc/cnv/nvRJ.def"
HEADERS = {"User-Agent": "Mozilla/5.0 (academic research; GraphAmbiCardio)", "Accept-Language": "pt-BR"}


def _post(arquivo: str, tipo: str) -> BeautifulSoup:
    params = {
        "Linha": "Município",
        "Coluna": "Ano_do_nascimento",
        "Incremento": "Nascim_p/resid.mãe",
        "Arquivos": arquivo,
        "SMunicípio": "18",  # option whose label starts with 330100 CAMPOS DOS GOYTACAZES
        "STipo_anomal_congên": tipo,
        "SAnomalia_congênita": "TODAS_AS_CATEGORIAS__",
        "formato": "table",
        "mostre": "Mostra",
    }
    body = urllib.parse.urlencode(params, encoding="latin-1").encode("latin-1")
    s = requests.Session()
    s.headers.update(HEADERS)
    s.get(URL, timeout=60)
    r = s.post(URL, data=body, timeout=120)
    r.raise_for_status()
    return BeautifulSoup(r.content.decode("latin-1"), "html.parser")


def _value(soup: BeautifulSoup) -> int | None:
    text = soup.get_text(" ", strip=True)
    m = re.search(r"330100 CAMPOS DOS GOYTACAZES\s+([\d.]+)", text)
    if not m:
        return None
    return int(m.group(1).replace(".", ""))


def fetch_year(year: int) -> dict[str, Any]:
    arquivo = f"nvrj{str(year)[2:]}.dbf"
    births = _value(_post(arquivo, "TODAS_AS_CATEGORIAS__"))
    cases = _value(_post(arquivo, "3"))  # malformações congênitas do aparelho circulatório
    status = "preliminary" if year >= 2025 else "consolidated (aggregate only)"
    row = {
        "year": year,
        "live_births": births,
        "circulatory_cases": cases,
        "per_1000_lb": round(1000 * cases / births, 2) if cases is not None and births else "",
        "source": "DATASUS TabNet (SINASC, nvRJ)",
        "data_status": status,
        "case_definition": "anomaly group 'malformações congênitas do aparelho circulatório' (Q20-Q28)",
        "note": "Aggregate only; microdata not available on the DATASUS FTP. Different case definition from the any-code microdata parser.",
        "retrieved_at": today(),
    }
    log.info("TabNet %s: %s births, %s circulatory cases", year, births, cases)
    return row


def build(years: list[int] | None = None) -> list[dict[str, Any]]:
    years = years or [2022, 2023, 2024, 2025]
    rows = [fetch_year(y) for y in years]
    write_csv(config.DATA_PROCESSED / "sinasc_tabnet_aggregates.csv", rows)
    write_json(config.DATA_PROCESSED / "sinasc_tabnet_quality.json", {
        "source": "DATASUS TabNet",
        "years": years,
        "retrieved_at": today(),
        "note": "Dados finais até 2024 (extração 02/12/2025); 2025 preliminar (extração 28/07/2026), conforme nota do TabNet.",
    })
    return rows


if __name__ == "__main__":
    build()
