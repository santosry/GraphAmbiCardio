# 13 — Declaração de uso de inteligência artificial

**Em conformidade com a Portaria CNPq nº 2.664/2026.**

O texto normativo completo e seus anexos devem ser consultados no sítio oficial do CNPq (Legislação). Esta declaração descreve, de forma transparente, como ferramentas de inteligência artificial foram usadas neste estudo, em que extensão, com quais verificações e sob responsabilidade humana.

---

## 1. Ferramentas utilizadas

- **Assistente de IA baseado em modelo de linguagem** (uso conversacional, via ambiente de desenvolvimento), para:
  - apoio à redação e à organização de código (Python e R);
  - apoio à triagem bibliográfica e à sumarização de abstracts;
  - apoio à redação e à tradução de documentação técnica;
  - apoio à estruturação do aplicativo Shiny.

Nenhum modelo foi usado como autor ou coautor. A responsabilidade científica permanece integralmente humana.

## 2. O que a IA não fez

- Não gerou dados, referências, identificadores ou resultados.
- Não inventou citações: todas as citações curadas são trechos verbatim de abstracts indexados no PubMed, verificados automaticamente contra o registro original.
- Não decidiu a classificação final de evidência nem a interpretação científica.
- Não substituiu a leitura humana dos 33 estudos-âncora.
- Não teve acesso a dados individuais identificáveis (não há tais dados no estudo).
- Não emitiu recomendações clínicas.

## 3. Verificação e responsabilidade humana

1. **Verificação bibliográfica automática:** o pipeline falha se um trecho citado não for encontrado no abstract do PMID correspondente (`scripts/integration/01_build_graph.py`).
2. **Revisão manual:** cada aresta curada foi lida e classificada por um pesquisador; as limitações e os elos ausentes foram registrados.
3. **Testes e validação:** integridade do grafo, unicidade de identificadores, resolução de PMIDs, checagens de dados locais e testes automatizados.
4. **Conferência da curadoria:** todos os trechos citados foram verificados automaticamente contra o PubMed e lidos pela equipe.
5. **Responsabilidade final:** integralmente humana. Os autores respondem por todo o conteúdo, incluindo eventuais erros introduzidos com apoio de IA.

## 4. Riscos identificados e mitigação

| Risco | Mitigação adotada |
|---|---|
| Citação fabricada | Verificação verbatim contra o PubMed; o build falha se o trecho não for encontrado |
| Confundir associação com causalidade | Camadas explícitas; linguagem causal proibida nas conclusões |
| Confundir hipótese com evidência | Camada de hipótese separada e excluída de caminhos, centralidade e conclusões |
| Viés de linguagem/região | Limitação declarada para SciELO/CAPES |
| Alucinação em texto | Leitura humana e checagem contra as tabelas geradas pelo pipeline |
| Exposição de dados sensíveis | Dados individuais de SINASC/SIH não são redistribuídos; o site publica apenas agregados e o código de reprodução |

## 5. Como citar esta declaração

> Ryan de Paulo Santos; Letícia Maria Dias Freitas; GraphAmbiCardio study team. *Declaração de uso de inteligência artificial*. In: GraphAmbiCardio, v0.3.0, 2026. Em conformidade com a Portaria CNPq nº 2.664/2026.

**Data:** 2026-10-31
**Versão:** 0.3.0
**Contato:** ryan.paulo@gsuite.iff.edu.br
