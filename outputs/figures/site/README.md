# Figuras do site GraphAmbiCardio

Gerado: 2026-11-02T13:36:02Z

Cada figura abaixo traz a fonte, o período e a nota de interpretação. Os dados usados estão em `data/`; o manifesto com SHA-256 está em `manifest.json`.

## Grafo interativo de exposições, mecanismos, processos e fenótipos

![Grafo interativo de exposições, mecanismos, processos e fenótipos](01_grafo_interativo.png)

**Fonte:** outputs/graph/nodes.csv, relations.csv e evidence.csv  
**Período:** 2010–2025  
**Nota:** Camadas/confiança em docs/04_ONTOLOGY.md e docs/06_EVIDENCE_GRADING.md.  
**Dados:** data/nodes.csv, data/relations.csv, data/evidence.csv  
**SHA-256:** `f9b7ec0b2185ada3e786b7b907476ae27cbf0db3ee29a841be7040f18d829ee6`

## SINASC: casos e taxa por 1.000 nascidos vivos

![SINASC: casos e taxa por 1.000 nascidos vivos](02_sinasc.png)

**Fonte:** SINASC/DATASUS (microdados 2010–2022 e 2025; TabNet 2023–2024 em série separada)  
**Período:** 2010–2025  
**Nota:** Casos = Q20–Q28 (malformações congênitas do aparelho circulatório, incluindo Q27–Q28); TabNet Q20–Q28 em colunas separadas; ver docs/07_EPI_ENV_METHODS.md.  
**Dados:** data/sinasc_annual.csv  
**SHA-256:** `0166642d0f120b2643f29faf4fa541881be7414c0323350d3f9adf5f95fca61c`

## SIH/SUS: internações e óbitos

![SIH/SUS: internações e óbitos](03_sih.png)

**Fonte:** SIH/SUS (AIH com diagnóstico principal Q20–Q28)  
**Período:** 2010–2025  
**Nota:** AIH não são pessoas; ver docs/07 e docs/09.  
**Dados:** data/sih_annual.csv  
**SHA-256:** `45c4dbde3062ff515839f427787bc4265d08d1f3018662990b4fbf0b2c07e115`

## Clima: temperatura máxima mensal (ERA5-Land)

![Clima: temperatura máxima mensal (ERA5-Land)](04_clima.png)

**Fonte:** ERA5-Land via Open-Meteo, modelo fixado era5_land, célula −21,800/−41,300  
**Período:** 2010–2025  
**Nota:** Série de área; não é estação local. Ver docs/03_DATABASE_CATALOG.md.  
**Dados:** data/climate_monthly.csv  
**SHA-256:** `face042638454d2366ec5442e5896e73e1011f8213afb7fe7a21408936bddc96`

## Dias de calor e ondas de calor por ano

![Dias de calor e ondas de calor por ano](05_calor.png)

**Fonte:** ERA5-Land via Open-Meteo (era5_land); limiar P90 recalculado na série fixada  
**Período:** 2010–2025  
**Nota:** Ver docs/07_EPI_ENV_METHODS.md.  
**Dados:** data/climate_annual.csv  
**SHA-256:** `f86aa53fa0ef98aadb2989c5eba13c1545a2d44a09fb01fc5bc92f6576d0c404`

## PM2,5: série municipal do VIGIAR (Ministério da Saúde)

![PM2,5: série municipal do VIGIAR (Ministério da Saúde)](06_pm25.png)

**Fonte:** VIGIAR/MS via pacote vigiar 0.7.2, filtro municipal 330100  
**Período:** 2010–2025  
**Nota:** Série de área; não é estação local nem exposição individual. Ver docs/07.  
**Dados:** data/pm25_monthly.csv, data/pm25_annual.csv  
**SHA-256:** `1e5e497667f3678952b04e9b5a14ed7afd8dff22edbf20df7f1cdd2fd6f3d4c1`

## Validação da exposição climática: INMET A607 vs ERA5-Land

![Validação da exposição climática: INMET A607 vs ERA5-Land](07_inmet_validacao.png)

**Fonte:** INMET estação A607 (lat −21,7167; lon −41,3500; alt 25 m) via BrazilMet 0.5.0; ERA5-Land via Open-Meteo  
**Período:** 2010–2025  
**Nota:** Dispersão diária; latitude, longitude, altitude, correlação, viés e RMSE nas tabelas do site. Ver docs/07.  
**Dados:** data/inmet_daily.csv, data/climate_daily.csv, data/inmet_comparison.csv  
**SHA-256:** `45455fb8429f13e467dab7a52b13d53407ea5cd123d18311a2d637a12241661a`
