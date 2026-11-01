# 14 — GraphAmbiCardio: aplicativo Shiny

O **GraphAmbiCardio** é a interface interativa do estudo. Ele não substitui a documentação metodológica; é uma ferramenta de exploração, auditoria e geração de perguntas.

---

## 0. Site publicado

**https://ryansantospaulo.shinyapps.io/graphambicardio/**

Hospedado no shinyapps.io (conta `ryansantospaulo`). O plano gratuito suspende a instância após inatividade; a primeira requisição pode levar ~30 s.

## 1. Como executar

Requisitos: R ≥ 4.4 com `shiny`, `bslib`, `DT`, `visNetwork`, `plotly`, `dplyr`, `readr`, `jsonlite`, `stringr`, `scales`, `htmltools`, `igraph`.

```r
# na raiz do repositório
shiny::runApp("app")
```

Ou:

```bash
Rscript -e 'shiny::runApp("app", port = 3838, launch.browser = TRUE)'
```

Os dados usados pelo app estão em `app/data/` (bundle autocontido, ~4 MB). Para atualizar após mudanças no pipeline:

```bash
python scripts/app/01_prepare_data.py
python scripts/app/02_fair_metadata.py
```

## 2. Módulos

| Aba | Função |
|---|---|
| **Início** | visão geral, KPIs, hierarquia de evidências e eixos de exposição |
| **Grafo interativo** | exploração por tipo de nó, nível de evidência, exposição e fenótipo; clique para ver evidências |
| **Painel epidemiológico** | SINASC (microdados + TabNet 2023–2024), SIH/SUS, clima ERA5-Land, PM2,5 VIGIAR e modelos exploratórios (logístico, Firth, cluster-robusto) com p e q (BH-FDR) |
| **Evidências** | tabela filtrável de relações; seleção mostra todas as evidências, trechos e referências |
| **Hipóteses e lacunas** | caminhos candidatos, hipóteses por sobreposição gênica e lacunas explícitas |
| **Consulta científica** | pergunta por exposição: mecanismos, fenótipos, genes, caminhos, hipóteses e referências |
| **Métodos** | desenho, buscas, bases, gradação e limitações |
| **FAIR e uso de IA** | princípios FAIR, metadados, licenças e declaração de IA (Portaria CNPq 2.664/2026) |

## 3. Legendas de fonte e figuras exportadas

Cada card com dado e cada figura exibe uma legenda de fonte, período e caminho do arquivo/documento de referência. As figuras também são exportadas para `outputs/figures/site/` (PNG, dados e `manifest.json` com SHA-256) por `scripts/app/03_export_site_figures.py`.

## 4. Decisões de design

- **Nada é escondido:** toda relação exibe nível, confiança, grau, referências e limitações.
- **Hipóteses são visualmente distintas:** arestas tracejadas e aviso explícito; não entram nas análises.
- **Contexto local é separado:** o painel epidemiológico tem avisos sobre subnotificação, AIH ≠ pessoa e exposição de área.
- **Acessibilidade:** navegação por teclado, contraste alto, textos em português brasileiro.
- **FAIR:** downloads em CSV, metadados DCAT/Data Package e identificadores persistentes.

## 4. Publicação

O app é autocontido e pode ser publicado em `shinyapps.io`, Shiny Server ou Posit Connect. Para publicar:

```r
rsconnect::deployApp("app", appName = "graphambicardio", account = "ryansantospaulo", server = "shinyapps.io")
```

ou `Rscript scripts/deploy/deploy_shinyapps.R`.

Antes de publicar, verifique:
1. licenças dos dados de terceiros;
2. tamanho do bundle (limite do plano);
3. ausência de credenciais;
4. versão dos metadados FAIR.

## 5. Limitações do app

- Não é um sistema de apoio à decisão clínica.
- Não faz inferência causal.
- Não atualiza automaticamente as bases; a atualização exige rodar o pipeline.
- O grafo é uma fotografia de 2026-10-31; HPO/ClinVar/Reactome mudam continuamente.
