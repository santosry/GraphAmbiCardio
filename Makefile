PY ?= .venv/Scripts/python.exe
ifeq ($(OS),)
PY := .venv/bin/python
endif

.PHONY: setup literature databases epi env graph analysis validate test all clean

setup:
	uv venv .venv --python 3.12
	uv pip install --python .venv -e ".[dev,datasus]"

literature:
	$(PY) scripts/collection/01_literature.py
	Rscript R/collection/scielo.R
	Rscript R/collection/capes.R
	Rscript R/collection/pm25_vigiar.R

databases:
	$(PY) scripts/collection/02_databases.py
	$(PY) scripts/collection/03_clinvar_enrichr.py

epi:
	$(PY) scripts/epi/01_sinasc.py
	$(PY) scripts/epi/02_sih.py
	$(PY) scripts/epi/03_exposure_models.py
	$(PY) scripts/epi/04_tabnet_supplement.py
	$(PY) scripts/epi/05_pysus_audit.py

env:
	$(PY) scripts/env/01_climate.py

graph:
	$(PY) scripts/integration/01_build_graph.py
	$(PY) scripts/cleaning/01_normalize_identifiers.py
	$(PY) scripts/graph/01_export_core.py
	$(PY) scripts/analysis/01_network.py
	$(PY) scripts/analysis/02_figures.py
	$(PY) scripts/analysis/03_enrichment_and_low_evidence.py
	$(PY) scripts/analysis/04_prisma_flow.py
	$(PY) scripts/app/01_prepare_data.py
	$(PY) scripts/app/02_fair_metadata.py
	$(PY) scripts/benchmark/01_benchmark.py
	$(PY) scripts/compliance/01_check.py

app:
	Rscript -e 'shiny::runApp("app", port = 3838, launch.browser = TRUE)'

validate:
	$(PY) scripts/validation/01_validate.py

test:
	$(PY) -m pytest -q

all: literature databases env epi graph validate test
