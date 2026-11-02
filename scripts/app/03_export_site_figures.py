"""Export all figures from the running Shiny app to outputs/figures/site/.

Usage (with the app running locally):
    python scripts/app/03_export_site_figures.py

Environment:
    APP_URL      default http://127.0.0.1:3850/
    CHROME_PATH  optional path to Chrome/Chromium (defaults to Playwright's browser)
    VIEWPORT     default 1600x1200
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs" / "figures" / "site"
DATA_OUT = OUT / "data"
APP_URL = os.environ.get("APP_URL", "http://127.0.0.1:3850/")
CHROME_PATH = os.environ.get("CHROME_PATH") or r"C:\Program Files\Google\Chrome\Application\chrome.exe"
VIEWPORT_W, VIEWPORT_H = (int(x) for x in os.environ.get("VIEWPORT", "1600x1200").split("x"))

FIGURES = [
    {
        "file": "01_grafo_interativo.png",
        "tab": "Grafo interativo",
        "selector": "#graph-network",
        "title": "Grafo interativo de exposições, mecanismos, processos e fenótipos",
        "source": "outputs/graph/nodes.csv, relations.csv e evidence.csv",
        "period": "2010–2025",
        "note": "Camadas/confiança em docs/04_ONTOLOGY.md e docs/06_EVIDENCE_GRADING.md.",
        "data": ["nodes.csv", "relations.csv", "evidence.csv"],
    },
    {
        "file": "02_sinasc.png",
        "tab": "Painel epidemiológico",
        "selector": "[id$='sinasc_plot']",
        "title": "SINASC: casos e taxa por 1.000 nascidos vivos",
        "source": "SINASC/DATASUS (microdados 2010–2022 e 2025; TabNet 2023–2024 em série separada)",
        "period": "2010–2025",
        "note": "Casos = Q20–Q28 (malformações congênitas do aparelho circulatório, incluindo Q27–Q28); TabNet Q20–Q28 em colunas separadas; ver docs/07_EPI_ENV_METHODS.md.",
        "data": ["sinasc_annual.csv"],
    },
    {
        "file": "03_sih.png",
        "tab": "Painel epidemiológico",
        "selector": "[id$='sih_plot']",
        "title": "SIH/SUS: internações e óbitos",
        "source": "SIH/SUS (AIH com diagnóstico principal Q20–Q28)",
        "period": "2010–2025",
        "note": "AIH não são pessoas; ver docs/07 e docs/09.",
        "data": ["sih_annual.csv"],
    },
    {
        "file": "04_clima.png",
        "tab": "Painel epidemiológico",
        "selector": "[id$='climate_plot']",
        "title": "Clima: temperatura máxima mensal (ERA5-Land)",
        "source": "ERA5-Land via Open-Meteo, modelo fixado era5_land, célula −21,800/−41,300",
        "period": "2010–2025",
        "note": "Série de área; não é estação local. Ver docs/03_DATABASE_CATALOG.md.",
        "data": ["climate_monthly.csv"],
    },
    {
        "file": "05_calor.png",
        "tab": "Painel epidemiológico",
        "selector": "[id$='heat_plot']",
        "title": "Dias de calor e ondas de calor por ano",
        "source": "ERA5-Land via Open-Meteo (era5_land); limiar P90 recalculado na série fixada",
        "period": "2010–2025",
        "note": "Ver docs/07_EPI_ENV_METHODS.md.",
        "data": ["climate_annual.csv"],
    },
    {
        "file": "06_pm25.png",
        "tab": "Painel epidemiológico",
        "selector": "[id$='pm25_plot']",
        "title": "PM2,5: série municipal do VIGIAR (Ministério da Saúde)",
        "source": "VIGIAR/MS via pacote vigiar 0.7.2, filtro municipal 330100",
        "period": "2010–2025",
        "note": "Série de área; não é estação local nem exposição individual. Ver docs/07.",
        "data": ["pm25_monthly.csv", "pm25_annual.csv"],
    },
    {
        "file": "07_inmet_validacao.png",
        "tab": "Painel epidemiológico",
        "selector": "[id$='inmet_plot']",
        "title": "Validação da exposição climática: INMET A607 vs ERA5-Land",
        "source": "INMET estação A607 (lat −21,7167; lon −41,3500; alt 25 m) via BrazilMet 0.5.0; ERA5-Land via Open-Meteo",
        "period": "2010–2025",
        "note": "Dispersão diária; latitude, longitude, altitude, correlação, viés e RMSE nas tabelas do site. Ver docs/07.",
        "data": ["inmet_daily.csv", "climate_daily.csv", "inmet_comparison.csv"],
    },
]

APP_DATA = {
    "nodes.csv": "app/data/nodes.csv",
    "relations.csv": "app/data/relations.csv",
    "evidence.csv": "app/data/evidence.csv",
    "sinasc_annual.csv": "app/data/sinasc_annual.csv",
    "sih_annual.csv": "app/data/sih_annual.csv",
    "climate_monthly.csv": "app/data/climate_monthly.csv",
    "climate_annual.csv": "app/data/climate_annual.csv",
    "pm25_monthly.csv": "app/data/pm25_monthly.csv",
    "pm25_annual.csv": "app/data/pm25_annual.csv",
    "inmet_daily.csv": "app/data/inmet_daily.csv",
    "inmet_comparison.csv": "app/data/inmet_comparison.csv",
    "climate_daily.csv": "app/data/climate_daily.csv",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


PARENT_TABS = {
    "Grafo interativo": "Grafo e painel",
    "Painel epidemiológico": "Grafo e painel",
    "Evidências": "Evidências e métodos",
    "Hipóteses e lacunas": "Evidências e métodos",
    "Consulta científica": "Evidências e métodos",
    "Métodos": "Evidências e métodos",
}


def click_link(page, name: str) -> None:
    link = page.locator(f"a[data-value='{name}']").first
    link.wait_for(state="visible", timeout=20000)
    link.click()


def click_tab(page, name: str) -> None:
    parent = PARENT_TABS.get(name)
    if parent:
        click_link(page, parent)
        page.wait_for_timeout(2500)
    click_link(page, name)
    page.wait_for_timeout(2500)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    DATA_OUT.mkdir(parents=True, exist_ok=True)
    for dst, src in APP_DATA.items():
        p = ROOT / src
        if p.exists():
            shutil.copy2(p, DATA_OUT / dst)

    manifest = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "app_url": APP_URL,
        "viewport": [VIEWPORT_W, VIEWPORT_H],
        "figures": [],
    }

    with sync_playwright() as p:
        launch = {"headless": True, "args": ["--no-sandbox"]}
        if CHROME_PATH and Path(CHROME_PATH).exists():
            launch["executable_path"] = CHROME_PATH
        browser = p.chromium.launch(**launch)
        page = browser.new_page(
            viewport={"width": VIEWPORT_W, "height": VIEWPORT_H},
            device_scale_factor=2,
        )
        page.goto(APP_URL, wait_until="domcontentloaded", timeout=90000)
        page.wait_for_timeout(6000)

        current_tab = None
        for fig in FIGURES:
            if fig["tab"] != current_tab:
                click_tab(page, fig["tab"])
                page.wait_for_timeout(6500)
                current_tab = fig["tab"]
            out = page.locator(fig["selector"]).first
            out.wait_for(state="visible", timeout=30000)
            block = out.locator("xpath=ancestor::div[contains(@class,'figure-block')]").first
            target = block if block.count() else out
            path = OUT / fig["file"]
            target.screenshot(path=str(path))
            manifest["figures"].append(
                {
                    **{k: fig[k] for k in ("file", "title", "source", "period", "note", "data")},
                    "path": str(path.relative_to(ROOT)),
                    "sha256": sha256(path),
                }
            )
            print("saved", path)
        browser.close()

    (OUT / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    lines = ["# Figuras do site GraphAmbiCardio", "",
             f"Gerado: {manifest['generated_at']}", "",
             "Cada figura abaixo traz a fonte, o período e a nota de interpretação. "
             "Os dados usados estão em `data/`; o manifesto com SHA-256 está em `manifest.json`.", ""]
    for f in manifest["figures"]:
        lines += [
            f"## {f['title']}",
            "",
            f"![{f['title']}]({f['file']})",
            "",
            f"**Fonte:** {f['source']}  ",
            f"**Período:** {f['period']}  ",
            f"**Nota:** {f['note']}  ",
            f"**Dados:** {', '.join('data/' + d for d in f['data'])}  ",
            f"**SHA-256:** `{f['sha256']}`",
            "",
        ]
    (OUT / "README.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"manifest: {OUT / 'manifest.json'}")


if __name__ == "__main__":
    main()
