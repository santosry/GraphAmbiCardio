# 16: CAPES, Portal de Periódicos e servidores MCP

## 1. O que foi efetivamente usado

O GraphAmbiCardio usa o **Catálogo de Teses e Dissertações da CAPES**, por meio do endpoint público:

```text
https://catalogodeteses.capes.gov.br/catalogo-teses/rest/busca
```

- Coletor: `R/collection/capes.R`.
- Resultado: **552 hits** para “cardiopatias congênitas”; 0 para poluição do ar + cardiopatia; 1 para agrotóxicos; 7 para temperatura: **560 hits no total**.
- A API devolve no máximo 20 itens por página. O coletor percorre todas as páginas: foram recuperados **560 registros** (552 + 0 + 1 + 7), correspondentes a **552 IDs únicos** (8 repetidos entre consultas). Todos entram na deduplicação e na triagem do fluxo PRISMA-ScR.
- Os 552 registros únicos foram triados por título. **1 tese foi incluída** como estudo-âncora e evidência indireta: *Exposição materna aos agrotóxicos e a ocorrência de malformações congênitas: uma revisão sistemática* (Vanessa Gama Freitas de Matos, UNIC, 2019), ligada a `EXP:PEST → CHD:ALL`. As outras **551 foram excluídas** (estudos clínicos, cirúrgicos, diagnósticos, psicossociais, infecciosos ou de “temperatura” não ambiental).
- A tese é uma **revisão sistemática**: entra como evidência indireta, sem estimativa sumária, e **não conta como replicação independente** dos estudos primários.
- Natureza: metadados de teses/dissertações, **não** o texto completo do Portal de Periódicos.

### Rastreabilidade

| Artefato | Conteúdo |
|---|---|
| `literature/searches/capes_cardiopatias_congenitas.json` | consulta, data, total de hits e 20 itens |
| `literature/searches/capes_poluicao_ar.json` | consulta com 0 hits |
| `literature/searches/capes_agrotoxicos.json` | consulta com 1 hit |
| `literature/searches/capes_temperatura.json` | consulta com 7 hits |
| `reports/prisma_flow.csv` | contagem da CAPES no fluxo de triagem (560 registros brutos; 552 IDs únicos) |
| `literature/screening/capes_triage.csv` | decisão e motivo para cada um dos 552 registros únicos |
| `literature/curated/capes_abstracts/7850222.json` | resumo arquivado da tese incluída, com URL e data de recuperação |

Esses arquivos também estão listados no `fair/datapackage.json` e no `fair/metadata.json`, com SHA-256, para que a consulta e a decisão possam ser auditadas sem depender do site da CAPES.

## 2. Portal de Periódicos CAPES

O Portal de Periódicos **não possui API oficial aberta** para busca em tempo real. O acesso ao texto completo depende de autenticação institucional (CAFe/federada) e os resultados podem ser exportados manualmente em **RIS** ou **BibTeX**.

Por isso, o Portal de Periódicos **não foi utilizado** no pipeline atual. A ausência está declarada em:

- `docs/02_SEARCH_STRATEGY.md`;
- `docs/03_DATABASE_CATALOG.md`;
- `docs/09_LIMITATIONS_AND_GAPS.md`;
- aba **Métodos** do aplicativo.

## 3. Servidores MCP comunitários encontrados

Busca realizada em 2026-11-01 no GitHub:

| Repositório | Função | Avaliação |
|---|---|---|
| [`damarals/periodicos-capes-mcp`](https://github.com/damarals/periodicos-capes-mcp) | Busca no Portal CAPES, exportação RIS/BibTeX, métricas OpenAlex/Qualis | Requer **Zyte API** (serviço pago) para contornar proteções do Portal; faz scraping e não usa autenticação institucional. Não adotado. |
| [`nextmarte/periodicos-mcp`](https://github.com/nextmarte/periodicos-mcp) | Classificação de periódicos (Qualis/CAPES, SJR, ABDC, SPELL) | Não busca artigos no Portal; é um classificador de periódicos. Não atende ao objetivo. |

## 4. Decisão

**Não integrar o MCP comunitário ao pipeline principal.** Motivos:

1. **Autenticação e termos de uso:** o Portal exige acesso institucional; contornar a proteção com Zyte não é compatível com um fluxo acadêmico auditável.
2. **Reprodutibilidade:** a dependência de uma chave paga e de scraping instável não é adequada para um pipeline que precisa ser reproduzido por terceiros.
3. **Transparência:** é melhor declarar o Portal como não utilizado do que apresentar uma coleta parcial como se fosse busca completa.

## 5. Alternativa recomendada

Se o grupo tiver acesso institucional ao Portal:

1. fazer a busca manualmente na interface do Portal;
2. exportar os resultados em **RIS** ou **BibTeX**;
3. salvar em `literature/raw/capes_portal/` (diretório local, não versionado);
4. importar os arquivos com um script de conversão e registrar a consulta, a data e o número de registros;
5. manter esses registros em uma camada separada, com a mesma regra de proveniência usada no restante do projeto.

Enquanto esse fluxo não for implementado e validado, o site deve mostrar apenas o que funcionou: **CAPES: Catálogo de Teses e Dissertações**. O site também deve deixar explícito que a CAPES forneceu **uma aresta indireta** (a tese 7850222, `EXP:PEST → CHD:ALL`) e que o Portal de Periódicos não foi utilizado.
