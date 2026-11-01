# Release 0.4.0

Checklist para publicar uma versão reproduzível.

## 1. Antes da tag

```bash
uv lock
uv pip install --python .venv -e ".[dev]"
python scripts/epi/03_exposure_models.py
python scripts/integration/01_build_graph.py
python scripts/cleaning/01_normalize_identifiers.py
python scripts/graph/01_export_core.py
python scripts/analysis/01_network.py
python scripts/analysis/02_figures.py
python scripts/analysis/03_enrichment_and_low_evidence.py
python scripts/analysis/04_prisma_flow.py
python scripts/app/01_prepare_data.py
python scripts/app/02_fair_metadata.py
python scripts/benchmark/01_benchmark.py
python scripts/compliance/01_check.py
python scripts/validation/01_validate.py
python scripts/validation/02_schema.py
python -m pytest -q
```

## 2. Verificações obrigatórias

- `compliance` aprovado, incluindo `Dados individuais versionados: 0`.
- `validation` e `schema` aprovados.
- `pytest` verde.
- App R carrega: `cd app && Rscript -e 'source("global.R"); source("ui.R"); source("server.R")'`.
- Nenhum arquivo individual de SINASC/SIH no `git ls-files`.
- `fair/datapackage.json` com checksums atualizados.

## 3. Tag e GitHub

```bash
git tag -a v0.4.0 -m "GraphAmbiCardio 0.4.0"
git push origin main --tags
```

## 4. Deploy do app

```bash
Rscript scripts/deploy/deploy_shinyapps.R
curl -I https://ryansantospaulo.shinyapps.io/graphambicardio/
```

O app usa apenas agregados; os dados individuais permanecem locais.
