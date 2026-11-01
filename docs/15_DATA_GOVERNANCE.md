# 15: Governança de dados e privacidade

O GraphAmbiCardio não redistribui registros individuais de saúde. Apenas
agregados e produtos derivados (grafo, tabelas e metadados) são versionados.

## 1. O que não é versionado

Os arquivos abaixo são gerados localmente pelos scripts de coleta e ficam no
`.gitignore`:

| Arquivo | Conteúdo | Motivo |
|---|---|---|
| `data_processed/sinasc_campos_births.csv` | um registro por nascimento (data, idade materna, raça, escolaridade, peso, sexo, códigos CID) | risco de reidentificação, especialmente dos casos raros de CHD |
| `data_processed/sinasc_campos_with_exposure.csv` | o arquivo acima + exposição gestacional estimada | combina atributos individuais e exposição |
| `data_processed/sih_campos_chd_admissions.csv` | uma linha por AIH de residente | registro individual de internação |

Os microdados brutos ficam em `data_raw/` (também ignorado) e são obtidos do
DATASUS/SINASC, SIH e das demais fontes públicas descritas em
`docs/03_DATABASE_CATALOG.md`.

## 2. Como reproduzir localmente

```bash
python scripts/epi/01_sinasc.py       # baixa e processa SINASC
python scripts/epi/02_sih.py          # baixa e processa SIH
python scripts/epi/03_exposure_models.py
```

Os scripts exigem acesso à internet e às fontes públicas. O resultado
individual permanece na máquina do pesquisador. O aplicativo Shiny usa somente
agregados (`app/data/sinasc_annual.csv`, `app/data/sih_annual.csv`,
`app/data/window_exposure.csv` etc.).

## 3. Dados agregados publicados

- `app/data/`, agregados anuais, mensais e por código usados pelo app.
- `outputs/tables/`, resultados analíticos sem identificadores individuais.
- `data_processed/sinasc_tabnet_aggregates.csv`, agregados do TabNet.
- `data_processed/pm25_campos_anual.csv` e `pm25_campos_mensal.csv`, série
  municipal de PM2,5, sem informação individual.
- `data_processed/inmet_campos_daily.csv`, série diária da estação automática
  INMET A607 (latitude −21,7167; longitude −41,3500; altitude 25 m), usada para
  validar o ERA5-Land; não é exposição individual.
- `data_processed/inmet_campos_metadata.json`, metadados, período, versão do
  pacote e checksum MD5 da série INMET.

## 4. Controles automáticos

`scripts/compliance/01_check.py` falha se qualquer arquivo da lista
`INDIVIDUAL_DATA` estiver versionado no Git. O mesmo script verifica segredos,
termos proibidos, checksums FAIR e o bundle do aplicativo.

## 5. Bases legais e limitações

- Os microdados do DATASUS são públicos, mas seu uso e republicação devem
  respeitar os termos do Ministério da Saúde e a LGPD (Lei 13.709/2018).
- A agregação reduz, mas não elimina, o risco de reidentificação em
  municípios pequenos e para desfechos raros.
- O estudo não faz linkage nominal nem contato com participantes.
- Em caso de dúvida ética, o pesquisador responsável deve consultar o CEP da
  instituição antes de publicar novos produtos derivados.
