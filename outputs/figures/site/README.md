# Figuras do site GraphAmbiCardio

Gerado: 2026-11-01T18:19:41Z

Cada figura abaixo traz a fonte, o período e a nota de interpretação. Os dados usados estão em `data/`; o manifesto com SHA-256 está em `manifest.json`.

## Grafo interativo de exposições, mecanismos, processos e fenótipos

![Grafo interativo de exposições, mecanismos, processos e fenótipos](01_grafo_interativo.png)

**Fonte:** outputs/graph/nodes.csv, relations.csv e evidence.csv  
**Período:** 2010–2025  
**Nota:** Camadas/confiança em docs/04_ONTOLOGY.md e docs/06_EVIDENCE_GRADING.md.  
**Dados:** data/nodes.csv, data/relations.csv, data/evidence.csv  
**SHA-256:** `7d39a4f43048eb4402eb4a076fe8366816db9891e6c39d8eadc893859dd137dd`

## SINASC: casos e taxa por 10.000 nascidos vivos

![SINASC: casos e taxa por 10.000 nascidos vivos](02_sinasc.png)

**Fonte:** SINASC/DATASUS (microdados 2010–2022 e 2025; TabNet 2023–2024 em série separada)  
**Período:** 2010–2025  
**Nota:** Casos = CHD core Q20–Q26; TabNet Q20–Q28 em colunas separadas; ver docs/07_EPI_ENV_METHODS.md.  
**Dados:** data/sinasc_annual.csv  
**SHA-256:** `ed7b84f211a31493dbd970db25bba7af56ea34f2e162215ab4fd70a73db0a1e5`

## SIH/SUS: internações e óbitos

![SIH/SUS: internações e óbitos](03_sih.png)

**Fonte:** SIH/SUS (AIH com diagnóstico principal core CHD Q20–Q26)  
**Período:** 2010–2025  
**Nota:** AIH não são pessoas; ver docs/07 e docs/09.  
**Dados:** data/sih_annual.csv  
**SHA-256:** `432c892b1255b5822bd78b3d0a2b7128b4d9cef2b4549bcac841504a6b03bef2`

## Clima: temperatura máxima mensal (ERA5-Land)

![Clima: temperatura máxima mensal (ERA5-Land)](04_clima.png)

**Fonte:** ERA5-Land via Open-Meteo, modelo fixado era5_land, célula −21,800/−41,300  
**Período:** 2010–2025  
**Nota:** Série de área; não é estação local. Ver docs/03_DATABASE_CATALOG.md.  
**Dados:** data/climate_monthly.csv  
**SHA-256:** `1997491a469bdd202aea32681ab36ef787ab83203869b9ff6ca1f199f14da564`

## Dias de calor e ondas de calor por ano

![Dias de calor e ondas de calor por ano](05_calor.png)

**Fonte:** ERA5-Land via Open-Meteo (era5_land); limiar P90 recalculado na série fixada  
**Período:** 2010–2025  
**Nota:** Ver docs/07_EPI_ENV_METHODS.md.  
**Dados:** data/climate_annual.csv  
**SHA-256:** `86b79ff045a2d4d02e77e39b59584b1d787efbf7ce9359bde678082849fcbfbe`

## PM2,5: série municipal do VIGIAR (Ministério da Saúde)

![PM2,5: série municipal do VIGIAR (Ministério da Saúde)](06_pm25.png)

**Fonte:** VIGIAR/MS via pacote vigiar 0.7.2, filtro municipal 330100  
**Período:** 2010–2025  
**Nota:** Série de área; não é estação local nem exposição individual. Ver docs/07.  
**Dados:** data/pm25_monthly.csv, data/pm25_annual.csv  
**SHA-256:** `70086ca7bdf544e76b7cf4f487a39060264e7d53c57fa8ab5730edb55ca1d632`

## Validação da exposição climática: INMET A607 vs ERA5-Land

![Validação da exposição climática: INMET A607 vs ERA5-Land](07_inmet_validacao.png)

**Fonte:** INMET estação A607 (lat −21,7167; lon −41,3500; alt 25 m) via BrazilMet 0.5.0; ERA5-Land via Open-Meteo  
**Período:** 2010–2025  
**Nota:** Dispersão diária; latitude, longitude, altitude, correlação, viés e RMSE nas tabelas do site. Ver docs/07.  
**Dados:** data/inmet_daily.csv, data/climate_daily.csv, data/inmet_comparison.csv  
**SHA-256:** `357122c3e35520063ac3b7efe12bef465bdcf5e8eed07b36360f680b29bd0c95`
