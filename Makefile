JULIA_REPS ?= 500
# Windows virtualenvs use Scripts/, Unix virtualenvs use bin/. Detect by path so
# the Makefile works whether or not OS is exported to make.
PY ?= $(if $(wildcard .venv/Scripts/python.exe),.venv/Scripts/python.exe,.venv/bin/python)

.PHONY: setup literature databases inmet epi env graph analysis julia julia-test validate schema test audit all clean clean-local lock figures exhaustive screened curation

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

julia:
	JULIA_REPS=$(JULIA_REPS) julia --project=julia julia/gestational_window_simulation.jl

inmet:
	Rscript R/collection/inmet.R

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
	$(PY) scripts/analysis/05_retrieval_coverage.py
	$(PY) scripts/app/01_prepare_data.py
	$(PY) scripts/app/02_fair_metadata.py
	$(PY) scripts/benchmark/01_benchmark.py
	$(PY) scripts/compliance/01_check.py

app:
	Rscript -e 'shiny::runApp("app", port = 3838, launch.browser = TRUE)'

validate:
	$(PY) scripts/validation/01_validate.py
	$(PY) scripts/validation/02_schema.py

schema:
	$(PY) scripts/validation/02_schema.py

figures:
	$(PY) scripts/app/03_export_site_figures.py

screened:
	$(PY) scripts/integration/02_build_screened_graph.py

curation:
	$(PY) scripts/curation/01_batch_chd_promotion.py
	$(PY) scripts/curation/02_export_review_packet.py
	$(PY) scripts/curation/03_propose_ambiguous.py
	$(PY) scripts/curation/04_triage_remaining.py

exhaustive:
	$(PY) scripts/collection/04_exhaustive_literature.py
	$(PY) scripts/analysis/06_rescreen_exhaustive.py
	$(PY) scripts/integration/02_build_screened_graph.py

clean-local:
	$(PY) scripts/maintenance/clean_local.py --yes

lock:
	uv lock

test:
	$(PY) -m pytest -q

julia-test:
	julia --project=julia julia/test/runtests.jl

audit: test julia-test validate schema
	$(PY) scripts/compliance/01_check.py
	Rscript -e 'files <- c(list.files("app", pattern="[.]R$$", recursive=TRUE, full.names=TRUE), list.files("R", pattern="[.]R$$", recursive=TRUE, full.names=TRUE)); for (f in files) { parse(f); cat("OK", f, sep=" ") }'

all: literature databases inmet env epi julia graph validate test
