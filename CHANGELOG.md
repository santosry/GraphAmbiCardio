# Changelog

## v0.3.0 — 2026-10-31

### Validação climática e ciência aberta
- INMET A607 (Campos dos Goytacazes) baixado com `BrazilMet` 0.5.0 e comparado
  ao ERA5-Land: 5.754 dias (2010–2025), Tmax r=0,94, Tmin r=0,94, Tmean
  r=0,97, umidade r=0,81. A estação entra como validação, não como exposição
  individual.
- Latitude, longitude e altitude da estação exibidas no app e nos metadados.
- `fair/` passa a incluir INMET, o relatório de comparação, o dicionário de
  dados e o manifesto de figuras; autores e fontes atualizados.
- Seção de ciência aberta no README e na aba Transparência e equipe, com links
  para código, metadados, figuras, governança e verificação automatizada.
- Grafo interativo ampliado: layout de força por padrão, opção hierárquica, legenda própria, botão de tela cheia, nós e rótulos maiores e exportação em viewport maior.

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
