# Figuras do site GraphAmbiCardio

Gerado: 2026-11-01T01:44:27Z

Cada figura abaixo traz a fonte, o período e a nota de interpretação. Os dados usados estão em `data/`; o manifesto com SHA-256 está em `manifest.json`.

## Grafo interativo de exposições, mecanismos, processos e fenótipos

![Grafo interativo de exposições, mecanismos, processos e fenótipos](01_grafo_interativo.png)

**Fonte:** outputs/graph/nodes.csv, relations.csv e evidence.csv  
**Período:** 2010–2025  
**Nota:** Camadas/confiança em docs/04_ONTOLOGY.md e docs/06_EVIDENCE_GRADING.md.  
**Dados:** data/nodes.csv, data/relations.csv, data/evidence.csv  
**SHA-256:** `b7474bc7ecdb5fcd106d9d86c9c83bcd3e848483ac58305031bb887d95275bac`

## SINASC — casos e taxa por 10.000 nascidos vivos

![SINASC — casos e taxa por 10.000 nascidos vivos](02_sinasc.png)

**Fonte:** SINASC/DATASUS (microdados 2010–2022 e 2025; TabNet 2023–2024)  
**Período:** 2010–2025  
**Nota:** Casos = CID-10 Q20–Q28; ver docs/07_EPI_ENV_METHODS.md.  
**Dados:** data/sinasc_annual.csv  
**SHA-256:** `f37e382a8e289375fb49ffbd6cefa0be5f749e876ea5b76c2b453950f542646e`

## SIH/SUS — internações e óbitos

![SIH/SUS — internações e óbitos](03_sih.png)

**Fonte:** SIH/SUS (AIH com diagnóstico principal Q20–Q28)  
**Período:** 2010–2025  
**Nota:** AIH não são pessoas; ver docs/07 e docs/09.  
**Dados:** data/sih_annual.csv  
**SHA-256:** `c29fcb0bdb31801c711e763798ee927503a0b0c471f8304fded204054da8d76f`

## Clima — temperatura máxima mensal (ERA5-Land)

![Clima — temperatura máxima mensal (ERA5-Land)](04_clima.png)

**Fonte:** ERA5-Land via Open-Meteo, célula −21,757/−41,354  
**Período:** 2010–2025  
**Nota:** Série de área; não é estação local. Ver docs/03_DATABASE_CATALOG.md.  
**Dados:** data/climate_monthly.csv  
**SHA-256:** `9b5a6b7043015cb98a213e0b1ccc993938738fee59ebc818c06837ad0fc89c09`

## Dias de calor e ondas de calor por ano

![Dias de calor e ondas de calor por ano](05_calor.png)

**Fonte:** ERA5-Land via Open-Meteo; limiar P90 34,2 °C  
**Período:** 2010–2025  
**Nota:** Ver docs/07_EPI_ENV_METHODS.md.  
**Dados:** data/climate_annual.csv  
**SHA-256:** `82be3434b20a249717d3ebb028b0b95da3c93462d3a8f034daeddbfcd4c0e0ef`

## PM2,5 — série municipal do VIGIAR (Ministério da Saúde)

![PM2,5 — série municipal do VIGIAR (Ministério da Saúde)](06_pm25.png)

**Fonte:** VIGIAR/MS via pacote vigiar 0.7.2, filtro municipal 330100  
**Período:** 2010–2025  
**Nota:** Série de área; não é estação local nem exposição individual. Ver docs/07.  
**Dados:** data/pm25_monthly.csv, data/pm25_annual.csv  
**SHA-256:** `b35219cdf96fc6ca11825db772cc746891b2867b0533b3234c0154d2a3cbd43a`
