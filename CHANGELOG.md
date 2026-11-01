# Changelog

## v0.4.0 — 2026-11-01

### Correções metodológicas críticas
- **Janela gestacional:** concepção estimada como data de nascimento menos
  (idade gestacional × 7 − 14 dias), refletindo o intervalo LMP-concepção.
  Para 40 semanas, a estimativa passou de 280 para **266 dias** antes do
  nascimento. Janelas ±7 dias são avaliadas como sensibilidade.
- **Definição de CHD:** o numerador principal passou a ser **Q20–Q26**.
  Q27–Q28 são reportadas separadamente (SINASC e SIH) e nunca somadas ao CHD.
  TabNet 2023–2024 (grupo amplo Q20–Q28) não é imputado no CHD core.
- **Modelo climático:** Open-Meteo passa a requisitar explicitamente
  `models=era5_land`; metadados registram modelo, resolução, célula retornada,
  elevação, unidades e timestamp. Série recalculada: P90 33,3 °C; 68 ondas.
- **Hipóteses gênicas:** família completa de 89 testes definida antes da
  seleção; universo HPO de 978 genes; BH-FDR em toda a família; permutação
  pareada por tamanho como sensibilidade; origem dos conjuntos gênicos
  documentada. Nenhum candidato significativo.
- **Sexo:** códigos diferentes de 1/2 passam a ser ausentes, não feminino.
- **Módulo Julia:** simulação Monte Carlo do erro de medida da janela gestacional, com ambiente `Project.toml`/`Manifest.toml`, job de CI e integração no app; não é um modelo bayesiano completo.

### Resultados atualizados
- SINASC: 98.598 nascimentos; **52 CHD core Q20–Q26** e **8 Q27–Q28**.
- SIH: **474 internações core Q20–Q26**, 75 Q27–Q28, 30 óbitos.
- Modelos: Tmax OR 1,155 (0,87–1,54; p=0,318); nenhum resultado sobrevive ao
  FDR. Sensibilidade gestacional: 1,071–1,221.
- INMET A607 vs ERA5-Land fixado: Tmax r=0,937; RH r=0,787.

### Produto
- App e figuras atualizados para Q20–Q26, TabNet separado, sensibilidade
  gestacional e modelo climático explícito.

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
- Aba Transparência e equipe com cards de apresentação da equipe, descrição do projeto e links Lattes/ORCID.
- Rodapé reposicionado para o fim real das páginas longas; declaração de IA sem as seções de riscos e de citação.

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
