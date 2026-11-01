# Figuras do site GraphAmbiCardio

Gerado: 2026-11-01T14:49:47Z

Cada figura abaixo traz a fonte, o período e a nota de interpretação. Os dados usados estão em `data/`; o manifesto com SHA-256 está em `manifest.json`.

## Grafo interativo de exposições, mecanismos, processos e fenótipos

![Grafo interativo de exposições, mecanismos, processos e fenótipos](01_grafo_interativo.png)

**Fonte:** outputs/graph/nodes.csv, relations.csv e evidence.csv  
**Período:** 2010–2025  
**Nota:** Camadas/confiança em docs/04_ONTOLOGY.md e docs/06_EVIDENCE_GRADING.md.  
**Dados:** data/nodes.csv, data/relations.csv, data/evidence.csv  
**SHA-256:** `42e56e29be50da713f8d0345f43c8a9bf6a2b3e3296d9134bf50316da6c222db`

## SINASC — casos e taxa por 10.000 nascidos vivos

![SINASC — casos e taxa por 10.000 nascidos vivos](02_sinasc.png)

**Fonte:** SINASC/DATASUS (microdados 2010–2022 e 2025; TabNet 2023–2024 em série separada)  
**Período:** 2010–2025  
**Nota:** Casos = CHD core Q20–Q26; TabNet Q20–Q28 em colunas separadas; ver docs/07_EPI_ENV_METHODS.md.  
**Dados:** data/sinasc_annual.csv  
**SHA-256:** `b859a68bfa428dfe72a8fbf197205a51ff454d1d524eb5639d1d459f74e5bc49`

## SIH/SUS — internações e óbitos

![SIH/SUS — internações e óbitos](03_sih.png)

**Fonte:** SIH/SUS (AIH com diagnóstico principal core CHD Q20–Q26)  
**Período:** 2010–2025  
**Nota:** AIH não são pessoas; ver docs/07 e docs/09.  
**Dados:** data/sih_annual.csv  
**SHA-256:** `0e08286adbe01c12a4a22d4524ec8afd55eb5aa89535494a52814e52f5425c1d`

## Clima — temperatura máxima mensal (ERA5-Land)

![Clima — temperatura máxima mensal (ERA5-Land)](04_clima.png)

**Fonte:** ERA5-Land via Open-Meteo, modelo fixado era5_land, célula −21,800/−41,300  
**Período:** 2010–2025  
**Nota:** Série de área; não é estação local. Ver docs/03_DATABASE_CATALOG.md.  
**Dados:** data/climate_monthly.csv  
**SHA-256:** `7f67538cad96de9c77c3b45347d7634d8943bfd8413e5c58571323c9547b52c9`

## Dias de calor e ondas de calor por ano

![Dias de calor e ondas de calor por ano](05_calor.png)

**Fonte:** ERA5-Land via Open-Meteo (era5_land); limiar P90 recalculado na série fixada  
**Período:** 2010–2025  
**Nota:** Ver docs/07_EPI_ENV_METHODS.md.  
**Dados:** data/climate_annual.csv  
**SHA-256:** `84334f993c1f4ca232bcdbea26b89b5e8453a6dc9ea20c53d03b2f046dbe7fa6`

## PM2,5 — série municipal do VIGIAR (Ministério da Saúde)

![PM2,5 — série municipal do VIGIAR (Ministério da Saúde)](06_pm25.png)

**Fonte:** VIGIAR/MS via pacote vigiar 0.7.2, filtro municipal 330100  
**Período:** 2010–2025  
**Nota:** Série de área; não é estação local nem exposição individual. Ver docs/07.  
**Dados:** data/pm25_monthly.csv, data/pm25_annual.csv  
**SHA-256:** `6815eea636232e9477c26d36c81e059388b82fd6ccd83bcacc6b71f43e2997a5`

## Validação da exposição climática — INMET A607 vs ERA5-Land

![Validação da exposição climática — INMET A607 vs ERA5-Land](07_inmet_validacao.png)

**Fonte:** INMET estação A607 (lat −21,7167; lon −41,3500; alt 25 m) via BrazilMet 0.5.0; ERA5-Land via Open-Meteo  
**Período:** 2010–2025  
**Nota:** Dispersão diária; latitude, longitude, altitude, correlação, viés e RMSE nas tabelas do site. Ver docs/07.  
**Dados:** data/inmet_daily.csv, data/climate_daily.csv, data/inmet_comparison.csv  
**SHA-256:** `b928fad67f181b3d7f7cad34be0b2f7371797a6cfc97c9081d0a9aafde24ee13`
