# Changelog

## v0.3.0 — 2026-10-31

### Privacidade e governança
- Remoção dos registros individuais de SINASC e SIH do versionamento e do
  histórico Git. Apenas agregados são publicados.
- `scripts/compliance/01_check.py` passa a falhar se dados individuais forem
  versionados.
- Nova documentação: `docs/15_DATA_GOVERNANCE.md`.

### Estatística
- Correção de múltiplas comparações por Benjamini–Hochberg em todos os modelos
  e nas hipóteses gênicas.
- Regressão logística de Firth e modelo com erros-padrão clusterizados por mês
  de concepção.
- Modelo de sensibilidade com escolaridade, raça, consultas de pré-natal e
  gestação múltipla.
- Diagnósticos de colinearidade (correlação e VIF) das exposições.
- q-values nas tabelas e no app.

### Reprodutibilidade
- `uv.lock` e `renv.lock` para Python e R.
- CI no GitHub Actions: testes, validação, schema, compliance e parse de R.
- `scripts/validation/02_schema.py` para checar schema, FDR e completude.
- Testes adicionais de FDR, modelos, PM2,5, bundle e checksums FAIR.
- `CONTRIBUTING` não incluído; ver README e Makefile.

### Aplicativo e documentação
- Paleta viridis e contraste de texto nos níveis de evidência.
- `viridisLite` adicionado ao Dockerfile.
- Documentação de q-values, PM2,5 e governança de dados.
- Versão 0.3.0 em `pyproject.toml`, `CITATION.cff`, `codemeta.json` e metadados.

### Pendências conhecidas
- Microdados de 2023–2024 do SINASC indisponíveis no DATASUS.
- Desfecho com subnotificação grave; resultados de exposição são
  exploratórios e nenhum sobrevive ao FDR.
