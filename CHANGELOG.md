# Changelog

## v0.4.0: 2026-11-01

### Revisão da CAPES (2026-11-01)
- Coletor da CAPES passa a percorrer todas as páginas: 560 registros recuperados (552 IDs únicos) em vez dos 20 primeiros por consulta. Triagem explícita dos 552 registros: 1 tese incluída, 551 excluídas com motivo em `literature/screening/capes_triage.csv`.
- Tese incluída: revisão sistemática sobre exposição materna a agrotóxicos e malformações congênitas (CAPES 7850222), como evidência **indireta** para `EXP:PEST → CHD:ALL`; resumo arquivado em `literature/curated/capes_abstracts/7850222.json`.
- Curadoria passa a 34 estudos-âncora (33 PMIDs + 1 tese CAPES), 55 linhas de evidência curada (54 relações únicas) e 4.614 linhas de evidência totais.
- Verificação de citações e validação estendidas para referências não-PMID; revisões não contam como replicação independente.
- FAIR Data Package inclui a triagem CAPES, o resumo da tese, `anchor_studies.csv`, `curated_edges.csv`, `reports/retrieval_coverage.csv` e `literature/screening/all_records_triage.csv` com SHA-256.
- Relatório de cobertura explicita a assimetria original; em seguida, uma recuperação **exaustiva** foi aplicada a todas as bases: PubMed domínios 25.406/25.442, PubMed pares 663/666, Europe PMC 4.789, SciELO 83.157 e CAPES 560. A triagem automática gerou **3.963 candidatos únicos** (638 com fenótipo CHD), exportados como camada separada `screened_studies`, não evidência.
- Novos artefatos: `reports/exhaustive_retrieval.csv`, `literature/screening/exhaustive_candidates.csv`, `outputs/graph/screened_studies.graphml/json`, `reports/screened_studies.json`.

### Curadoria em lote com camada de revisão (2026-11-01)
- Fila de promoção dos 635 candidatos CHD com PMID: 23 candidatos automáticos, 11 propostas de segunda passagem e leitura integral em lotes; **49 arestas verificadas**, 15 recusados e 596 registros da fila ainda sem decisão.
- Extração determinística e testável em `src/graphambicardio/curation/batch_extract.py`; regra de cláusula única exige uma exposição, um fenótipo e um tamanho de efeito explícito. Frases com múltiplos fenótipos e valores de p são rejeitadas.
- Camada de revisão em `literature/curated/batch_chd_review.csv` (`src/graphambicardio/curation/batch_review.py`). Nenhum candidato entra no grafo sem `review_status=verified`.
- A construção do grafo rejeita linhas verificadas cuja citação não seja verbatim no resumo do PubMed; a validação audita a revisão contra a tabela de evidências.
- Recusados: PMID 2091934 (publicação duplicada de PMID 1397217), PMID 37610216 (exposição combinada PM10 + CO), dois candidatos que já existiam na curadoria manual (PMID 32278917 e PMID 35916623), bloqueados por regra automática de duplicidade, e PMID 11745829 (estimativa de solvente para CoA/VSD, não VSD isolado). Achados condicionais de PMID 28520847 e PMID 32091506 entram com ressalva explícita.
- Grafo atualizado: 2.238 nós, 4.146 relações, 4.659 linhas de evidência, 60 caminhos exposição a fenótipo (50 diretos, 10 mecanísticos) e 20 lacunas.
- Família de hipóteses gênicas atualizada para **66 testes**, 1 com sobreposição ≥2, nenhuma significativa após BH-FDR.
- Novo pacote de leitura humana: `reports/batch_chd_review_packet.md`; segunda passagem por proposta (`reports/batch_chd_proposals.md`) e triagem da fila restante (`reports/batch_chd_triage.md`); novo alvo `make curation`.
- Estilo editorial: travessão removido do README, dos documentos públicos e do texto do app, com verificação automática na conformidade.

### Leitura integral em lotes (2026-11-01)
- Pipeline `scripts/curation/05_read_fulltext_batch.py`: PDF de acesso aberto, XML JATS e resumo, em lotes de 10; o arquivo completo é apagado depois da extração.
- 660 estudos com leitura registrada: 98 com texto completo (43 PDF + 55 XML) e 562 apenas com resumo; 319 estudos não elegíveis foram registrados em nível de metadados; 68 trechos curtos arquivados em `literature/curated/fulltext_quotes/`.
- 20 arestas verificadas adicionais (49 no total) e 15 candidatos recusados, incluindo duplicatas, estimativas nulas, citações de revisão narrativa e atribuições erradas.
- Tabela de metadados em `literature/curated/fulltext_metadata.csv`; log em `reports/fulltext_reading_log.md`; nenhum artigo completo permanece no notebook.
- Esquema de evidência ganhou `quote_source` e `quote_archive`; a validação recheca 100% dos trechos de texto completo contra o trecho arquivado.
- Nova dependência de desenvolvimento: `pypdf`.

### Correções metodológicas críticas
- **Janela gestacional:** concepção estimada como data de nascimento menos
  (idade gestacional × 7 − 14 dias), refletindo o intervalo LMP-concepção.
  Para 40 semanas, a estimativa passou de 280 para **266 dias** antes do
  nascimento. Janelas ±7 dias são avaliadas como sensibilidade.
- **Definição de CHD:** o numerador principal passou a ser **Q20–Q26**.
  Q27–Q28 são reportadas separadamente (SINASC e SIH) e nunca somadas ao CHD.
  TabNet 2023–2024 (grupo amplo Q20–Q28) não é imputado no CHD core.
- **Modelo climático:** Open-Meteo passa a requisitar explicitamente
  `models=era5_land`; metadados registram modelo, resolução, célula retornada,
  elevação, unidades e timestamp. Série recalculada: P90 33,3 °C; 68 ondas.
- **Hipóteses gênicas:** família completa definida antes da seleção (66 testes na versão atual); universo HPO de 978 genes; BH-FDR em toda a família; permutação
  pareada por tamanho como sensibilidade; origem dos conjuntos gênicos
  documentada. Nenhum candidato significativo.
- **Sexo:** códigos diferentes de 1/2 passam a ser ausentes, não feminino.
- **Módulo Julia:** simulação Monte Carlo do erro de medida da janela gestacional, com ambiente `Project.toml`/`Manifest.toml`, job de CI e integração no app; não é um modelo bayesiano completo.

### Resultados atualizados
- SINASC: 98.598 nascimentos; **52 CHD core Q20–Q26** e **8 Q27–Q28**.
- SIH: **474 internações core Q20–Q26**, 75 Q27–Q28, 30 óbitos.
- Modelos: Tmax OR 1,155 (0,87–1,54; p=0,318); nenhum resultado sobrevive ao
  FDR. Sensibilidade gestacional: 1,071–1,221.
- INMET A607 vs ERA5-Land fixado: Tmax r=0,937; RH r=0,787.

### Produto
- App e figuras atualizados para Q20–Q26, TabNet separado, sensibilidade
  gestacional e modelo climático explícito.
- Aba de métodos passa a ler as contagens do PRISMA e a citar a tese CAPES
  incluída; a tabela de evidências mostra o link CAPES quando aplicável.

## v0.3.0: 2026-10-31

### Validação climática e ciência aberta
- INMET A607 (Campos dos Goytacazes) baixado com `BrazilMet` 0.5.0 e comparado
  ao ERA5-Land: 5.754 dias (2010–2025), Tmax r=0,94, Tmin r=0,94, Tmean
  r=0,97, umidade r=0,81. A estação entra como validação, não como exposição
  individual.
- Latitude, longitude e altitude da estação exibidas no app e nos metadados.
- `fair/` passa a incluir INMET, o relatório de comparação, o dicionário de
  dados e o manifesto de figuras; autores e fontes atualizados.
- Seção de ciência aberta no README e na aba Transparência e equipe, com links
  para código, metadados, figuras, governança e verificação automatizada.
- Grafo interativo ampliado: layout de força por padrão, opção hierárquica, legenda própria, botão de tela cheia, nós e rótulos maiores e exportação em viewport maior.
- Aba Transparência e equipe com cards de apresentação da equipe, descrição do projeto e links Lattes/ORCID.
- Rodapé reposicionado para o fim real das páginas longas; declaração de IA sem as seções de riscos e de citação.

### Privacidade e governança
- Remoção dos registros individuais de SINASC e SIH do versionamento e do
  histórico Git. Apenas agregados são publicados.
- `scripts/compliance/01_check.py` passa a falhar se dados individuais forem
  versionados.
- Nova documentação: `docs/15_DATA_GOVERNANCE.md`.

### Estatística
- Correção de múltiplas comparações por Benjamini–Hochberg em todos os modelos
  e nas hipóteses gênicas.
- Regressão logística de Firth e modelo com erros-padrão clusterizados por mês
  de concepção.
- Modelo de sensibilidade com escolaridade, raça, consultas de pré-natal e
  gestação múltipla.
- Diagnósticos de colinearidade (correlação e VIF) das exposições.
- q-values nas tabelas e no app.

### Reprodutibilidade
- `uv.lock` e `renv.lock` para Python e R.
- CI no GitHub Actions: testes, validação, schema, compliance e parse de R.
- `scripts/validation/02_schema.py` para checar schema, FDR e completude.
- Testes adicionais de FDR, modelos, PM2,5, bundle e checksums FAIR.
- `CONTRIBUTING` não incluído; ver README e Makefile.

### Aplicativo e documentação
- Paleta viridis e contraste de texto nos níveis de evidência.
- `viridisLite` adicionado ao Dockerfile.
- Documentação de q-values, PM2,5 e governança de dados.
- Versão 0.3.0 em `pyproject.toml`, `CITATION.cff`, `codemeta.json` e metadados.

### Pendências conhecidas
- Microdados de 2023–2024 do SINASC indisponíveis no DATASUS.
- Desfecho com subnotificação grave; resultados de exposição são
  exploratórios e nenhum sobrevive ao FDR.
