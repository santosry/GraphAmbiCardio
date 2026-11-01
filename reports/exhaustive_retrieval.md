# Recuperação exaustiva por base

Todos os hits das consultas pré-registradas foram recuperados. Os registros brutos ficam em `data_raw/literature/full/` (não versionado); a tabela de candidatos e o resumo com SHA-256 são versionados.

| Base | Buscas | Hits totais | Recuperados | Candidatos (antes de dedup) |
|---|---:|---:|---:|---:|
| Europe PMC | 5 | 4,789 | 4,789 | 477 |
| PubMed/MEDLINE (domínios) | 5 | 25,442 | 25,406 | 4,181 |
| PubMed/MEDLINE (pares) | 238 | 666 | 663 | 485 |
| SciELO (Crossref 10.1590) | 5 | 83,157 | 83,157 | 2 |

Candidatos únicos após deduplicação por PMID/DOI/título: **3,963**.

Critério de candidato: resumo disponível + espécie humana/animal/célula + pelo menos um termo de exposição + fenótipo CHD ou mecanismo com contexto cardíaco/embrionário. Isso é **triagem automática**, não curadoria: um candidato não é uma aresta de evidência.

A curadoria manual continua sendo a única porta de entrada para `evidence.csv`; ver `docs/06_EVIDENCE_GRADING.md`.
