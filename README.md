# GraphAmbiCardio

**GraphAmbiCardio** — grafo de conhecimento com proveniência sobre exposições ambientais, mecanismos moleculares, cardiogênese e cardiopatias congênitas.
**Campos dos Goytacazes, RJ, 2010–2025.**

[![status](https://img.shields.io/badge/status-v0.2.0-blue)]()
[![Python](https://img.shields.io/badge/python-3.12-blue)]()
[![R](https://img.shields.io/badge/R-%E2%89%A54.4-276DC3)]()

> **Este estudo não é uma revisão sistemática.** É uma busca estruturada com curadoria dirigida, bases biológicas curadas e análise ecológica de dados secundários. Não estima efeitos causais.

---

## 1. O que é o projeto

O GraphAmbiCardio integra cinco camadas:

1. **Literatura** — PubMed/MEDLINE, Europe PMC, SciELO (metadados via Crossref, prefixo DOI 10.1590) e CAPES (Catálogo de Teses e Dissertações).
2. **Bases biológicas curadas** — HPO, ClinVar, NCBI Gene, Reactome e Enrichr.
3. **Dados epidemiológicos locais** — SINASC (nascidos vivos) e SIH/SUS (internações), 2010–2025.
4. **Exposição ambiental de área** — ERA5-Land via Open-Meteo para clima e **PM2,5 municipal do VIGIAR/Ministério da Saúde via pacote `vigiar`** (2010–2025). Séries de área, não exposição individual.
5. **Grafo com proveniência** — cada relação carrega tipo de evidência, espécie, desenho, janela de exposição, referência, confiança, limitações e **nível de evidência** (bem sustentada / plausível experimental / não demonstrada / contextual).

Há duas camadas integradas e **nunca misturadas**:

- **Camada de evidências** — relações documentadas e anotadas em bases curadas.
- **Camada de hipóteses** — caminhos candidatos gerados por composição de arestas e sobreposição gênica, com o **elo ausente explicitado**. Hipóteses não entram em análises de caminhos, centralidade ou conclusões.

---

## 2. Resultados principais (v0.2.0)

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
- **5 hipóteses por sobreposição gênica** (nenhuma significativa após BH-FDR) e **7 caminhos candidatos com elo ausente**.
- Exportações: `outputs/graph/graph.graphml`, `graph.json`, `nodes.csv`, `relations.csv`, `evidence.csv`.

### Dados locais

- SINASC: **98.598 nascimentos** (microdados 2010–2022 e 2025; **2023–2024 apenas agregados do TabNet**). **59 casos** nos microdados (5,98/10.000) — subnotificação grave. TabNet: 5 casos em 2023 e 5 em 2024; 2025 = 9 casos, compatível com os microdados.
- SIH/SUS: **549 internações** por diagnóstico principal Q20–Q28 (**561 no total**, 12 apenas secundárias), **33 óbitos**, **55% fora do município**, 18 hospitais.
- Clima: **5.844 dias** ERA5-Land; limiar de onda de calor 34,2 °C; **73 ondas / 363 dias**.
- Modelo exploratório (56–59 eventos): temperatura OR **1,30/SD** (1,00–1,69; p = 0,049, q = 0,214); ajustado por estação **1,65** (1,13–2,42; p = 0,010, q = 0,087); modelo mensal **nulo** (RR 1,22; 0,94–1,60). PM2,5 municipal do VIGIAR foi **nulo** (OR 0,91/SD; 0,70–1,18) e permaneceu nulo no ajuste mútuo com temperatura (OR 1,01; 0,77–1,32). **Nenhum modelo sobrevive ao FDR (q < 0,05); não é achado causal.**

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
8. **FAIR e uso de IA** — metadados, licenças e declaração de IA (Portaria CNPq 2.664/2026).

Publicação: `Rscript scripts/deploy/deploy_shinyapps.R` (requer conta configurada no `rsconnect`).

Detalhes: `docs/14_APP.md`.

---

## 4. Reprodutibilidade

### Requisitos

- Python **3.12** (decodificador DBC do DATASUS).
- R **≥ 4.4** com `shiny`, `bslib`, `DT`, `visNetwork`, `plotly`, `dplyr`, `readr`, `jsonlite`, `stringr`, `scales`, `htmltools`, `igraph`, `commonmark`.
- Internet para NCBI, Europe PMC, Crossref, HPO, Reactome, Enrichr, Open-Meteo e DATASUS.

```bash
uv venv .venv --python 3.12
uv pip install --python .venv -e ".[dev,datasus]"

# pipeline Python
.venv/Scripts/python.exe scripts/collection/01_literature.py
.venv/Scripts/python.exe scripts/collection/02_databases.py
.venv/Scripts/python.exe scripts/collection/03_clinvar_enrichr.py
.venv/Scripts/python.exe scripts/env/01_climate.py
.venv/Scripts/python.exe scripts/epi/01_sinasc.py
.venv/Scripts/python.exe scripts/epi/02_sih.py
.venv/Scripts/python.exe scripts/epi/03_exposure_models.py
.venv/Scripts/python.exe scripts/epi/04_tabnet_supplement.py
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

# buscas em R (SciELO via Crossref e CAPES Catálogo de Teses)
Rscript R/collection/scielo.R
Rscript R/collection/capes.R
```

Ou `make all`. O cache HTTP e os dados brutos ficam em `data_raw/` (ignorado pelo git); toda resposta usada no grafo é rastreável.

---

## 5. Auditoria, benchmark e conformidade

```bash
.venv/Scripts/python.exe scripts/validation/01_validate.py   # integridade + citações
.venv/Scripts/python.exe scripts/benchmark/01_benchmark.py   # tempo/memória
.venv/Scripts/python.exe scripts/compliance/01_check.py      # higiene, segredos, FAIR, nomes
.venv/Scripts/python.exe -m pytest -q
```

Resultados em `reports/validation_report.md`, `reports/benchmark.md` e `reports/compliance_report.md`. A conformidade verifica termos proibidos, segredos, checksums FAIR, ausência de `data_raw/` no git, declaração de IA e bundle do app.

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
| `R/collection/` | coletores R para SciELO (Crossref) e CAPES |
| `app/` | aplicativo Shiny GraphAmbiCardio (PT-BR) e bundle de dados |
| `docs/` | protocolo, viabilidade, busca, catálogo, ontologia, dicionário, gradação, métodos, validação, limitações, fases, manuscrito, FAIR, IA e app |
| `fair/` | metadados DCAT e Frictionless Data Package com checksums |
| `reports/` | matrizes de viabilidade, PRISMA, validação, auditoria, resumos |
| `literature/` | buscas (JSON), triagem, estudos-âncora |
| `data_processed/` | dados harmonizados |
| `outputs/` | grafo, tabelas e figuras |
| `tests/` | testes unitários e de integridade |

---

## 8. FAIR e uso de IA

- **Findable/Accessible/Interoperable/Reusable:** identificadores persistentes por entidade, metadados DCAT/Data Package, CSV/JSON/GraphML, proveniência por evidência, licença MIT para código e licenças de terceiros preservadas. Ver `docs/12_FAIR.md` e `fair/`.
- **Declaração de IA:** em conformidade com a **Portaria CNPq nº 2.664/2026**, em `docs/13_DECLARACAO_IA.md`. A IA apoiou código, triagem e redação; não gerou dados/referências, não decidiu a classificação final e não é autora. Toda citação curada foi verificada contra o PubMed.
- **Curadoria:** todos os trechos citados foram lidos pela equipe e verificados automaticamente contra o PubMed.

---

## 9. Limitações principais

- Busca não sistemática; sem triagem dupla de todos os registros nem texto completo.
- SciELO acessado por metadados Crossref (a interface de busca bloqueou automação); CAPES limitado ao Catálogo de Teses.
- SINASC com subnotificação grave; 2023–2024 sem microdados (apenas TabNet); 2025 preliminar.
- SIH: AIH ≠ pessoa; 55% das internações fora do município.
- Exposição de área (clima e PM2,5 do VIGIAR), não individual; não há monitoramento de estação local.
- Maioria das cadeias mecanísticas é experimental, em doses não equivalentes às humanas.
- HPO/ClinVar são orientados a doenças mendelianas/sindrômicas.

Ver `docs/09_LIMITATIONS_AND_GAPS.md`.

---

## 10. Licença e citação

Código: MIT (`LICENSE`). Dados de terceiros mantêm suas licenças. Citação em `CITATION.cff`.
Repositório: https://github.com/santosry/GraphAmbiCardio
