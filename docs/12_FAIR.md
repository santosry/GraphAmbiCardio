# 12 — Princípios FAIR no GraphAmbiCardio

O GraphAmbiCardio foi desenhado para ser **Findable, Accessible, Interoperable and Reusable**. Este documento descreve o que foi efetivamente implementado e o que permanece como limitação.

---

## F — Findable (localizável)

- **Identificadores persistentes por entidade:** PMID e DOI para estudos; HPO IDs para fenótipos; CID-10 para a camada epidemiológica; ClinVar VCV para variantes; Reactome stable IDs (`R-HSA-…`) para vias; NCBI Gene IDs para genes.
- **Metadados descritivos:** `fair/metadata.json` (perfil DCAT) e `fair/datapackage.json` (Frictionless Data Package), com título, descrição, palavras-chave, cobertura espacial (IBGE 330100) e temporal (2010–2025), fontes e licenças.
- **Aplicativo de descoberta:** o GraphAmbiCardio (Shiny, PT-BR; https://ryansantospaulo.shinyapps.io/graphambicardio/) permite busca por exposição, fenótipo, gene, via e termo livre, com recuperação das referências; inclui painel epidemiológico, camada de hipóteses e downloads em CSV.
- **Identificador do conjunto:** URL do repositório + versão (`https://github.com/santosry/GraphAmbiCardio#v0.3.0`).

## A — Accessible (acessível)

- Código, dados derivados, metadados e documentação estão em repositório público, sem autenticação.
- O aplicativo Shiny é executável localmente e pode ser publicado em `shinyapps.io`.
- Formatos abertos: CSV, JSON, GraphML, Markdown.
- **Dados de terceiros:** os microdados brutos do DATASUS não são redistribuídos; scripts de download são fornecidos. **Registros individuais de SINASC/SIH não são versionados** (ver `docs/15_DATA_GOVERNANCE.md`); o app usa apenas agregados. PubMed/Europe PMC, HPO, ClinVar, Reactome, Open-Meteo/ERA5-Land e Crossref mantêm suas próprias licenças e termos.
- Credenciais e tokens não são armazenados no repositório.

## I — Interoperable (interoperável)

- Vocabulários e identificadores padronizados (CID-10, HPO, OMIM, Orphanet, Reactome, NCBI Gene, UniProt quando disponível, PMID, DOI).
- Esquema de dados explícito (`data_dictionary/data_dictionary.csv`, `docs/04_ONTOLOGY.md`).
- Exportações em GraphML e JSON, adequadas a NetworkX, igraph, Neo4j e ferramentas de visualização.
- Ontologia própria documentada, com tipos de nó, tipos de relação, camadas e regras de inferência.

## R — Reusable (reutilizável)

- **Proveniência por evidência:** cada linha de `evidence.csv` tem referência, tipo de evidência, espécie, desenho, janela de exposição, direção do efeito, contexto, citação e limitações.
- **Camadas separadas:** observada, estruturada, inferida, hipótese e ecológica. Hipóteses nunca são misturadas às evidências.
- **Documentação:** protocolo, estratégia de busca, catálogo de bases, ontologia, dicionário, gradação, métodos, validação, limitações e manuscrito.
- **Reprodutibilidade:** pipeline modular, cache de respostas HTTP, logs, testes automatizados, versões de dados e data de extração; coletores R para SciELO (Crossref), CAPES e VIGIAR PM2.5; bundle autocontido do app; Dockerfile com R e snapshot do CRAN.
- **Licença:** código MIT; dados de terceiros sob suas licenças. Citação em `CITATION.cff`.
- **Controle de qualidade:** validação de integridade, verificação de citações e análise de sensibilidade.

---

## O que ainda falta para FAIR pleno

1. **Hashes de release** para HPO, ClinVar e Reactome (atualmente registra-se a data de extração, não o release exato).
2. **Metadados por campo** no datapackage (o esquema atual traz nome e tipo, não descrição semântica completa).
3. **Publicação do aplicativo** em servidor institucional com URL persistente.

Essas lacunas estão registradas em `docs/09_LIMITATIONS_AND_GAPS.md` e não são apresentadas como resolvidas.
