# GraphAmbiCardio

**GraphAmbiCardio** — grafo de conhecimento com proveniência sobre exposições ambientais, mecanismos moleculares, cardiogênese e cardiopatias congênitas.
**Campos dos Goytacazes, RJ, 2010–2025.**

[![status](https://img.shields.io/badge/status-v0.4.0-blue)]()
[![Python](https://img.shields.io/badge/python-3.12-blue)]()
[![R](https://img.shields.io/badge/R-%E2%89%A54.4-276DC3)]()
[![CI](https://github.com/santosry/GraphAmbiCardio/actions/workflows/ci.yml/badge.svg)](https://github.com/santosry/GraphAmbiCardio/actions/workflows/ci.yml)

> **Em uma frase:** o GraphAmbiCardio organiza, em um só lugar, o que a ciência sabe sobre como o ambiente (calor, poluição do ar, umidade) pode influenciar o desenvolvimento do coração do bebê — e mostra onde ainda faltam evidências.

> **Este estudo não é uma revisão sistemática.** É uma busca organizada, com curadoria feita por pessoas, bases biológicas públicas e análise de dados de saúde de Campos dos Goytacazes. Não prova causalidade.

---

## Em linguagem simples

- **O problema:** cardiopatias congênitas são alterações no coração que aparecem antes do nascimento. Fatores ambientais podem contribuir, mas a ciência ainda tem muitas lacunas.
- **O que o projeto faz:** junta estudos científicos, genes, fenótipos (sinais clínicos), dados de nascimentos e dados de clima/poluição em um mapa visual chamado **grafo**. Cada ligação mostra de onde veio a informação e quão forte ela é.
- **O que ele não faz:** não diz que uma exposição “causa” cardiopatia em uma pessoa; não substitui avaliação médica; não usa dados individuais no site.
- **Para que serve:** ajudar pesquisadores, gestores e o público a ver o que está bem sustentado, o que é apenas hipótese e onde faltam estudos.
- **Ciência aberta:** código, metadados, figuras, tabelas e instruções de reprodução são públicos. Dados individuais de saúde não são redistribuídos; o site mostra apenas agregados.

---

## Ciência aberta — compromisso verificável

O GraphAmbiCardio adota **ciência aberta por padrão**, com um limite explícito: dados individuais de saúde não são redistribuídos.

| Artefato | Onde está | Verificação |
|---|---|---|
| Código e pipeline | repositório público, licença MIT | `LICENSE`, `Makefile`, `.github/workflows/ci.yml` |
| Dados derivados e agregados | `data_processed/`, `outputs/`, `app/data/` | schemas em `scripts/validation/02_schema.py` |
| Metadados FAIR | `fair/metadata.json`, `fair/datapackage.json` | SHA-256 por recurso; `scripts/compliance/01_check.py` |
| Figuras e tabelas | `outputs/figures/site/`, `outputs/tables/` | `manifest.json` com fonte, período e SHA-256 |
| Documentação | `docs/` | protocolo, métodos, limitações, governança e declaração de IA |
| Privacidade | `docs/15_DATA_GOVERNANCE.md` | microdados individuais fora do Git; app só com agregados |
| Reprodutibilidade | `uv.lock`, `renv.lock`, `run_all.sh` | versões fixadas, cache HTTP, testes e validação |

**Como verificar localmente:**

```bash
.venv/Scripts/python.exe scripts/validation/02_schema.py
.venv/Scripts/python.exe scripts/compliance/01_check.py
.venv/Scripts/python.exe -m pytest -q
```

Os resultados ficam em `reports/schema_validation.md`, `reports/compliance_report.md` e `reports/validation_report.md`. Nenhum resultado é apresentado como causal; hipóteses permanecem separadas das evidências.

---

## 1. O que é o projeto

O GraphAmbiCardio integra cinco camadas:

1. **Literatura** — PubMed/MEDLINE, Europe PMC, SciELO (metadados via Crossref, prefixo DOI 10.1590) e CAPES (Catálogo de Teses e Dissertações).
2. **Bases biológicas curadas** — HPO, ClinVar, NCBI Gene, Reactome e Enrichr.
3. **Dados epidemiológicos locais** — SINASC (nascidos vivos) e SIH/SUS (internações), 2010–2025.
4. **Exposição ambiental de área** — ERA5-Land via Open-Meteo com **modelo fixado em `era5_land`**, **INMET estação A607** (temperatura e umidade) e **PM2,5 municipal do VIGIAR/Ministério da Saúde via pacote `vigiar`** (2010–2025). Séries de área, não exposição individual.
5. **Grafo com proveniência** — cada relação carrega tipo de evidência, espécie, desenho, janela de exposição, referência, confiança, limitações e **nível de evidência** (bem sustentada / plausível experimental / não demonstrada / contextual).

Há duas camadas integradas e **nunca misturadas**:

- **Camada de evidências** — relações documentadas e anotadas em bases curadas.
- **Camada de hipóteses** — caminhos candidatos gerados por composição de arestas e sobreposição gênica, com o **elo ausente explicitado**. Hipóteses não entram em análises de caminhos, centralidade ou conclusões.

---

## 2. Resultados principais (v0.4.0)

### Base de evidências

| Domínio | PubMed | Europe PMC |
|---|---:|---:|
| Exposição → CHD | 1,512 | 1,599 |
| Exposição → mecanismo | 8,520 | 171 |
| Mecanismo → cardiogênese | 6,736 | 39 |
| Cardiogênese → fenótipo | 7,681 | 593 |
| Gene → fenótipo | 992 | 2,387 |

- **196 pares exposição × fenótipo**: 73 sem literatura direta, 66 esparsos, 36 limitados, 19 moderados, 2 de alto volume.
- **1.978 registros brutos → 529 duplicatas → 1.449 únicos** (1.003 com resumo no subconjunto PubMed/Europe PMC).
- **33 estudos-âncora** lidos manualmente; **54 arestas curadas** com citações verbatim verificadas contra o PubMed.
- SciELO: 100 registros por consulta via Crossref; 42–60 com termos de CHD. CAPES: 552 teses/dissertações para “cardiopatias congênitas”.

### Grafo

- **2.238 nós**, **4.117 relações**, **4.613 linhas de evidência**.
- Camadas: **observada 54**, **estruturada 4.040**, **inferida 4**, **hipótese 14**, **ecológica 3**.
- **27 caminhos exposição→fenótipo** (17 diretos, 10 mecanísticos) e **20 lacunas explícitas**.
- **Hipóteses por sobreposição gênica:** família completa de **89 testes** (exposição × mecanismo × fenótipo), **5 com sobreposição ≥2 genes** e **nenhuma significativa após BH-FDR**; universo HPO de **978 genes**; permutação pareada por tamanho como sensibilidade. **7 caminhos candidatos com elo ausente**.
- Exportações: `outputs/graph/graph.graphml`, `graph.json`, `nodes.csv`, `relations.csv`, `evidence.csv`.

### Dados locais

- SINASC: **98.598 nascimentos** (microdados 2010–2022 e 2025; **2023–2024 apenas agregados do TabNet**). **52 casos de CHD core (Q20–Q26; 5,27/10.000)** e **8 registros Q27–Q28** (não CHD; 1 também tinha código Q20–Q26) — subnotificação grave. TabNet 2023 e 2024: **5 e 5 casos no grupo amplo Q20–Q28**, mantidos em colunas separadas e **não imputados como CHD core**.
- SIH/SUS: **474 internações** por diagnóstico principal **Q20–Q26** (**75 Q27–Q28** em série separada; 12 apenas secundárias), **30 óbitos**, **51,9% fora do município**, 16 hospitais. AIH não são pessoas.
- Clima: **5.844 dias** ERA5-Land com modelo **fixado em `era5_land`** (resolução ~9 km; célula retornada −21,800/−41,300; elevação 12 m); limiar de onda de calor **33,3 °C**; **68 ondas / 353 dias**. Validação com **INMET A607** (2010–2025): Tmax r=0,937 (viés +1,20 °C; RMSE 1,78); Tmin r=0,942 (−0,77; 1,20); Tmean r=0,972 (−0,23; 0,67); umidade r=0,787 (+1,61; 4,77). Série de estação, distinta da reanálise.
- Sensibilidade Julia (Monte Carlo da janela gestacional, 500 réplicas): mediana OR **1,157**; intervalo 95% **1,116–1,202**; cenários fixos de −7 a +7 dias: **1,075–1,224**. O erro individual médio tende a se cancelar; o deslocamento sistemático da janela é o que mais altera a estimativa.
- Modelo exploratório (52 casos core; **47 eventos** nos modelos completos): temperatura OR **1,155/SD** (0,87–1,535; p = 0,318; q = 0,509); Firth **1,159** (0,869–1,532; p = 0,304); cluster mensal **1,155** (0,829–1,611; p = 0,394); ajuste socioeconômico Firth **1,187** (0,889–1,571; p = 0,236); ajuste sazonal **1,357** (0,914–2,013; p = 0,130); modelo mensal **RR 1,211** (0,918–1,599; p = 0,176). Sensibilidade da janela gestacional: principal **1,155**; −7 dias **1,221** (0,922–1,618; p = 0,164); +7 dias **1,071** (0,803–1,428; p = 0,641). PM2,5 municipal **0,842** (0,625–1,134; p = 0,257) e ajuste mútuo PM2,5 **0,872** / temperatura **1,106**. **Nenhum modelo sobrevive ao FDR (q < 0,05); não é achado causal.**

### Hierarquia de exposições

| Exposição | Papel | Evidência epidemiológica | Evidência molecular |
|---|---|---|---|
| PM2,5 | **Eixo principal** | Moderada | Relativamente consistente (AHR, ROS, mitocôndria, Wnt) |
| Temperatura | **Eixo secundário** | Crescente, inclusive no Brasil | Parcial (neural crest/TRPV) |
| PM10, NO₂, CO, O₃ | Condicional | Específica por fenótipo | Limitada |
| Umidade | **Contextual** | Muito limitada | Sem conexão estabelecida |

---

## 3. GraphAmbiCardio: aplicativo Shiny

**Site publicado:** **https://ryansantospaulo.shinyapps.io/graphambicardio/**

O plano gratuito do shinyapps.io coloca o aplicativo em repouso após inatividade; a primeira abertura pode levar ~30 segundos.

```r
# execução local
shiny::runApp("app")
```

Aplicativo em português brasileiro com oito abas:

1. **Início** — visão geral, KPIs e hierarquia.
2. **Grafo interativo** — filtros por tipo, nível de evidência, exposição e fenótipo; clique para ver evidências.
3. **Painel epidemiológico** — SINASC, SIH, clima e modelos, com avisos de interpretação.
4. **Evidências** — tabela filtrável; seleção mostra todas as evidências, trechos e referências.
5. **Hipóteses e lacunas** — caminhos candidatos, hipóteses por genes e lacunas.
6. **Consulta científica** — pergunta por exposição e recupera mecanismos, fenótipos, genes, caminhos e referências.
7. **Métodos** — desenho, buscas, bases, gradação e limitações.
8. **Transparência e equipe** — metadados FAIR, licenças, autores com Lattes e declaração de IA (Portaria CNPq 2.664/2026).

Publicação: `Rscript scripts/deploy/deploy_shinyapps.R` (requer conta configurada no `rsconnect`).

Detalhes: `docs/14_APP.md`.

**Figuras exportadas:** `outputs/figures/site/` contém PNGs de todas as figuras do site, os dados usados (`data/`), `manifest.json` com fonte/período/SHA-256 e `README.md` com as legendas.

---

## 4. Reprodutibilidade

### Requisitos

- Python **3.12** (decodificador DBC do DATASUS).
- R **≥ 4.4** com `shiny`, `bslib`, `DT`, `visNetwork`, `plotly`, `dplyr`, `tidyr`, `readr`, `jsonlite`, `stringr`, `scales`, `htmltools`, `igraph`, `commonmark`, `viridisLite`, `vigiar` e `rsconnect`. As versões exatas estão em `renv.lock`.
- Internet para NCBI, Europe PMC, Crossref, HPO, Reactome, Enrichr, Open-Meteo e DATASUS.
- **Julia ≥ 1.10** para o módulo de simulação Monte Carlo da janela gestacional (`julia/`).

```bash
uv venv .venv --python 3.12
uv sync --extra dev --extra datasus   # usa uv.lock
# ou: uv pip install --python .venv -e ".[dev,datasus]"
# R: renv::restore()   # usa renv.lock

# pipeline Python
.venv/Scripts/python.exe scripts/collection/01_literature.py
.venv/Scripts/python.exe scripts/collection/02_databases.py
.venv/Scripts/python.exe scripts/collection/03_clinvar_enrichr.py
.venv/Scripts/python.exe scripts/env/01_climate.py
Rscript R/collection/inmet.R
.venv/Scripts/python.exe scripts/epi/01_sinasc.py
.venv/Scripts/python.exe scripts/epi/02_sih.py
.venv/Scripts/python.exe scripts/epi/03_exposure_models.py
.venv/Scripts/python.exe scripts/epi/04_tabnet_supplement.py
JULIA_REPS=500 julia --project=julia julia/gestational_window_simulation.jl
.venv/Scripts/python.exe scripts/integration/01_build_graph.py
.venv/Scripts/python.exe scripts/cleaning/01_normalize_identifiers.py
.venv/Scripts/python.exe scripts/graph/01_export_core.py
.venv/Scripts/python.exe scripts/analysis/01_network.py
.venv/Scripts/python.exe scripts/analysis/02_figures.py
.venv/Scripts/python.exe scripts/analysis/03_enrichment_and_low_evidence.py
.venv/Scripts/python.exe scripts/validation/01_validate.py
.venv/Scripts/python.exe scripts/app/01_prepare_data.py
.venv/Scripts/python.exe scripts/app/02_fair_metadata.py
.venv/Scripts/python.exe -m pytest -q

# coletores em R (SciELO via Crossref, CAPES, INMET e VIGIAR)
Rscript R/collection/scielo.R
Rscript R/collection/capes.R
Rscript R/collection/inmet.R
Rscript R/collection/pm25_vigiar.R
```

Ou `make all`. O cache HTTP e os dados brutos ficam em `data_raw/` (ignorado pelo git); toda resposta usada no grafo é rastreável. **Dados individuais de SINASC/SIH não são versionados** — ver `docs/15_DATA_GOVERNANCE.md`.

### Módulo Julia

O único módulo em Julia é a simulação Monte Carlo do erro de medida da janela gestacional:

```bash
JULIA_REPS=500 julia --project=julia julia/gestational_window_simulation.jl
```

Ele usa `julia/Project.toml`/`Manifest.toml`, lê o arquivo individual local, escreve apenas agregados em `outputs/tables/julia_gestational_window_simulation.csv` e `reports/julia_gestational_window_simulation.json`. Resultado com 500 réplicas: mediana OR **1,157**; intervalo de simulação **1,116–1,202**; cenários fixos de −7 a +7 dias: **1,075–1,224**. Não é um modelo bayesiano completo; é uma análise de sensibilidade de erro de medida. Ver `docs/07_EPI_ENV_METHODS.md`.

---

## 5. Auditoria, benchmark e conformidade

```bash
.venv/Scripts/python.exe scripts/validation/01_validate.py   # integridade + citações
.venv/Scripts/python.exe scripts/validation/02_schema.py     # schema, FDR, PM2,5, versão
.venv/Scripts/python.exe scripts/benchmark/01_benchmark.py   # tempo/memória
.venv/Scripts/python.exe scripts/compliance/01_check.py      # higiene, segredos, FAIR, nomes
.venv/Scripts/python.exe -m pytest -q
```

Resultados em `reports/validation_report.md`, `reports/schema_validation.md`, `reports/benchmark.md` e `reports/compliance_report.md`. A conformidade verifica termos proibidos, segredos, checksums FAIR, ausência de `data_raw/` e de dados individuais no git, declaração de IA, compromisso de ciência aberta e bundle do app.

## 6. Docker

```bash
docker compose up --build
# http://localhost:3838
```

`Dockerfile` fixa R 4.6.1 e um snapshot do CRAN; o bundle de dados do app já está incluído. O Docker não estava instalado no ambiente de desenvolvimento, então o build não foi executado localmente — ver `docker/README.md`.

## 7. Estrutura

| Caminho | Conteúdo |
|---|---|
| `src/graphambicardio/` | pacote Python (coleta, limpeza, integração, grafo, análise, validação) |
| `R/collection/` | coletores R para SciELO (Crossref), CAPES, INMET A607 e VIGIAR PM2,5 |
| `julia/` | módulo Julia de simulação Monte Carlo do erro de medida da janela gestacional |
| `app/` | aplicativo Shiny GraphAmbiCardio (PT-BR) e bundle de dados |
| `docs/` | protocolo, viabilidade, busca, catálogo, ontologia, dicionário, gradação, métodos, validação, limitações, fases, manuscrito, FAIR, IA, app, governança de dados e CAPES/MCP |
| `fair/` | metadados DCAT e Frictionless Data Package com checksums |
| `reports/` | matrizes de viabilidade, PRISMA, validação, conformidade, schema e resumos |
| `literature/` | buscas (JSON), triagem, estudos-âncora |
| `data_processed/` | dados harmonizados |
| `outputs/` | grafo, tabelas e figuras |
| `tests/` | testes unitários e de integridade |
| `codemeta.json`, `CITATION.cff` | metadados de citação e software |
| `outputs/figures/site/` | figuras do site em PNG, dados e manifesto com SHA-256 |
| `CHANGELOG.md`, `RELEASE.md` | histórico e checklist de release |

---

## 8. Transparência, FAIR e uso de IA

- **Findable/Accessible/Interoperable/Reusable:** identificadores persistentes por entidade, metadados DCAT/Data Package, CSV/JSON/GraphML, proveniência por evidência, licença MIT para código e licenças de terceiros preservadas. Ver `docs/12_FAIR.md` e `fair/`.
- **Declaração de IA:** em conformidade com a **Portaria CNPq nº 2.664/2026**, em `docs/13_DECLARACAO_IA.md`. A IA apoiou código, triagem e redação; não gerou dados/referências, não decidiu a classificação final e não é autora. Toda citação curada foi verificada contra o PubMed.
- **Curadoria:** todos os trechos citados foram lidos pela equipe e verificados automaticamente contra o PubMed.

---

## 9. Limitações principais

- Busca não sistemática; sem triagem dupla de todos os registros nem texto completo.
- SciELO acessado por metadados Crossref (a interface de busca bloqueou automação); CAPES limitado ao Catálogo de Teses (o Portal de Periódicos não foi usado; servidores MCP comunitários foram avaliados e não adotados — ver `docs/16_CAPES_MCP.md`).
- SINASC com subnotificação grave; 2023–2024 sem microdados (apenas TabNet Q20–Q28, não imputado como CHD core); 2025 preliminar.
- Definição de CHD core = Q20–Q26; Q27–Q28 são reportadas separadamente e não entram no numerador principal.
- SIH: AIH ≠ pessoa; 55% das internações fora do município.
- Exposição de área (clima e PM2,5 do VIGIAR), não individual. A estação INMET A607 é usada para validação da reanálise; não representa exposição pessoal.
- Idade gestacional: concepção estimada como 40 semanas obstétricas menos 14 dias (266 dias para 40 semanas); janelas ±7 dias avaliadas como sensibilidade.
- Maioria das cadeias mecanísticas é experimental, em doses não equivalentes às humanas.
- HPO/ClinVar são orientados a doenças mendelianas/sindrômicas.

Ver `docs/09_LIMITATIONS_AND_GAPS.md`.

---

## 10. Equipe

- **Ryan de Paulo Santos** — [Currículo Lattes](http://lattes.cnpq.br/7503796642571978) · [ORCID](https://orcid.org/0009-0005-6770-2001)
- **Letícia Maria Dias Freitas** — [Currículo Lattes](http://lattes.cnpq.br/4004634244195808) · [ORCID](https://orcid.org/0009-0009-9930-9588)

Nomes completos, formação e produção estão nos currículos Lattes.

---

## 11. Licença e citação

Código: MIT (`LICENSE`). Dados de terceiros mantêm suas licenças. Citação em `CITATION.cff`.
Repositório: https://github.com/santosry/GraphAmbiCardio

**Ciência aberta:** todo o código, metadados, figuras, tabelas e instruções de reprodução estão públicos. Dados individuais de saúde não são redistribuídos.
