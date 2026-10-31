#!/usr/bin/env bash
# Reproduce the full GraphAmbiCardio pipeline (Python 3.12 venv expected).
set -euo pipefail
PY="${PY:-.venv/Scripts/python.exe}"
[ -x "$PY" ] || PY=".venv/bin/python"

$PY scripts/collection/01_literature.py
$PY scripts/collection/02_databases.py
$PY scripts/collection/03_clinvar_enrichr.py
$PY scripts/env/01_climate.py
$PY scripts/epi/01_sinasc.py
$PY scripts/epi/02_sih.py
$PY scripts/epi/03_exposure_models.py
$PY scripts/integration/01_build_graph.py
$PY scripts/cleaning/01_normalize_identifiers.py
$PY scripts/graph/01_export_core.py
$PY scripts/analysis/01_network.py
$PY scripts/analysis/02_figures.py
$PY scripts/validation/01_validate.py
$PY -m pytest -q
