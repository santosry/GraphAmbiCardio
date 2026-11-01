# Cobertura de recuperação e triagem por base

Este relatório separa **o que foi recuperado** de **o que foi usado como evidência**.
A busca é estruturada e não sistemática; a cobertura é assimétrica e declarada.

| Base | Buscas | Hits totais | Registros recuperados |
|---|---:|---:|---:|
| CAPES Teses | 4 | 560 | 560 |
| Europe PMC | 5 | 4,789 | 439 |
| PubMed (domínios) | 5 | 25,441 | 498 |
| PubMed (pares) | 123 | 546 | 513 |
| SciELO (Crossref 10.1590) | 5 | 83,157 | 500 |

## Status dos registros recuperados (inclui repetições entre buscas)

| Status | Registros |
|---|---:|
| anchor | 135 |
| excluded | 558 |
| included | 2 |
| triaged_not_selected | 1,815 |

**Estudos-âncora no grafo:** 66 PMIDs + 1 tese CAPES = 67.
**Desses, aparecem nos registros top-N recuperados:** 40 PMIDs + 1 tese CAPES. Os outros **26 PMIDs** foram incluídos por busca dirigida/referências e não estão no top-N.
**CAPES:** 1 ID incluído, 551 IDs excluídos; os 560 registros incluem 8 repetições entre consultas.

## Política de recuperação

- **PubMed:** top 100 por domínio e top 15 por par exposição × fenótipo.
- **Europe PMC:** top 100 por domínio.
- **SciELO via Crossref:** top 100 por consulta.
- **CAPES:** todas as páginas (560 registros; 552 IDs únicos), com triagem manual de título e leitura de resumo dos candidatos.

Os registros recuperados das bases top-N foram triados automaticamente (`src/graphambicardio/literature/screen.py`); apenas uma parte se tornou estudo-âncora. Além disso, 23 PMIDs-âncora vieram de busca dirigida/referências e não do top-N. Isso **não** é uma revisão sistemática e não há triagem dupla de todos os hits.

Arquivos: `reports/retrieval_coverage.csv` e `literature/screening/all_records_triage.csv`.
