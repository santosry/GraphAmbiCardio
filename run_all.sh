#!/usr/bin/env bash
# Reproduce the full GraphAmbiCardio pipeline (Python 3.12 venv expected).
set -euo pipefail
PY="${PY:-.venv/Scripts/python.exe}"
[ -x "$PY" ] || PY=".venv/bin/python"

$PY scripts/collection/01_literature.py
Rscript R/collection/scielo.R
Rscript R/collection/capes.R
Rscript R/collection/pm25_vigiar.R
$PY scripts/collection/02_databases.py
$PY scripts/collection/03_clinvar_enrichr.py
Rscript R/collection/inmet.R
$PY scripts/env/01_climate.py
$PY scripts/epi/01_sinasc.py
$PY scripts/epi/02_sih.py
$PY scripts/epi/03_exposure_models.py
$PY scripts/epi/04_tabnet_supplement.py
JULIA_REPS="${JULIA_REPS:-500}" julia --project=julia julia/gestational_window_simulation.jl
$PY scripts/epi/05_pysus_audit.py
$PY scripts/integration/01_build_graph.py
$PY scripts/cleaning/01_normalize_identifiers.py
$PY scripts/graph/01_export_core.py
$PY scripts/analysis/01_network.py
$PY scripts/analysis/02_figures.py
$PY scripts/analysis/03_enrichment_and_low_evidence.py
$PY scripts/analysis/04_prisma_flow.py
$PY scripts/app/01_prepare_data.py
$PY scripts/app/02_fair_metadata.py
$PY scripts/benchmark/01_benchmark.py
$PY scripts/compliance/01_check.py
$PY scripts/validation/01_validate.py
$PY scripts/validation/02_schema.py
$PY -m pytest -q
