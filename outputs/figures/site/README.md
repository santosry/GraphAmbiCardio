# Figuras do site GraphAmbiCardio

Gerado: 2026-11-01T02:29:19Z

Cada figura abaixo traz a fonte, o período e a nota de interpretação. Os dados usados estão em `data/`; o manifesto com SHA-256 está em `manifest.json`.

## Grafo interativo de exposições, mecanismos, processos e fenótipos

![Grafo interativo de exposições, mecanismos, processos e fenótipos](01_grafo_interativo.png)

**Fonte:** outputs/graph/nodes.csv, relations.csv e evidence.csv  
**Período:** 2010–2025  
**Nota:** Camadas/confiança em docs/04_ONTOLOGY.md e docs/06_EVIDENCE_GRADING.md.  
**Dados:** data/nodes.csv, data/relations.csv, data/evidence.csv  
**SHA-256:** `9879c6638a29f4ff2d4c5b6e1454797ba8cca91a277bfb7b29375e99fe98650d`

## SINASC — casos e taxa por 10.000 nascidos vivos

![SINASC — casos e taxa por 10.000 nascidos vivos](02_sinasc.png)

**Fonte:** SINASC/DATASUS (microdados 2010–2022 e 2025; TabNet 2023–2024)  
**Período:** 2010–2025  
**Nota:** Casos = CID-10 Q20–Q28; ver docs/07_EPI_ENV_METHODS.md.  
**Dados:** data/sinasc_annual.csv  
**SHA-256:** `7b7e819051cbc8e11b3ec519b3a3cfd7686d72a8154d4533c1431d4e68ea4d1f`

## SIH/SUS — internações e óbitos

![SIH/SUS — internações e óbitos](03_sih.png)

**Fonte:** SIH/SUS (AIH com diagnóstico principal Q20–Q28)  
**Período:** 2010–2025  
**Nota:** AIH não são pessoas; ver docs/07 e docs/09.  
**Dados:** data/sih_annual.csv  
**SHA-256:** `850735dba1b207f0f47a11bd177ca964c9035635bcdc29016c4feaabae37da7d`

## Clima — temperatura máxima mensal (ERA5-Land)

![Clima — temperatura máxima mensal (ERA5-Land)](04_clima.png)

**Fonte:** ERA5-Land via Open-Meteo, célula −21,757/−41,354  
**Período:** 2010–2025  
**Nota:** Série de área; não é estação local. Ver docs/03_DATABASE_CATALOG.md.  
**Dados:** data/climate_monthly.csv  
**SHA-256:** `24193b139f8e923b57abd0d9ca88518856305cb53c8c60759a0ecd2093ffb264`

## Dias de calor e ondas de calor por ano

![Dias de calor e ondas de calor por ano](05_calor.png)

**Fonte:** ERA5-Land via Open-Meteo; limiar P90 34,2 °C  
**Período:** 2010–2025  
**Nota:** Ver docs/07_EPI_ENV_METHODS.md.  
**Dados:** data/climate_annual.csv  
**SHA-256:** `662f8c60feda1f336d3b15c46e2ad81688083df29a1c703fb34a5eab7fc7baec`

## PM2,5 — série municipal do VIGIAR (Ministério da Saúde)

![PM2,5 — série municipal do VIGIAR (Ministério da Saúde)](06_pm25.png)

**Fonte:** VIGIAR/MS via pacote vigiar 0.7.2, filtro municipal 330100  
**Período:** 2010–2025  
**Nota:** Série de área; não é estação local nem exposição individual. Ver docs/07.  
**Dados:** data/pm25_monthly.csv, data/pm25_annual.csv  
**SHA-256:** `b718138cad72a529e51ed5f76bbdef68ce38df4d9f14c6a2958b624de0e48abe`

## Validação da exposição climática — INMET A607 vs ERA5-Land

![Validação da exposição climática — INMET A607 vs ERA5-Land](07_inmet_validacao.png)

**Fonte:** INMET estação A607 (lat −21,7167; lon −41,3500; alt 25 m) via BrazilMet 0.5.0; ERA5-Land via Open-Meteo  
**Período:** 2010–2025  
**Nota:** Dispersão diária; latitude, longitude, altitude, correlação, viés e RMSE nas tabelas do site. Ver docs/07.  
**Dados:** data/inmet_daily.csv, data/climate_daily.csv, data/inmet_comparison.csv  
**SHA-256:** `f0db765d89e50af93b9811800825cd1364f3a7ad15cd44396ff003813495deba`
