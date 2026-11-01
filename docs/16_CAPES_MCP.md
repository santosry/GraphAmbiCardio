# 16 — CAPES, Portal de Periódicos e servidores MCP

## 1. O que foi efetivamente usado

O GraphAmbiCardio usa o **Catálogo de Teses e Dissertações da CAPES**, por meio do endpoint público:

```text
https://catalogodeteses.capes.gov.br/catalogo-teses/rest/busca
```

- Coletor: `R/collection/capes.R`.
- Resultado: **552 teses/dissertações** para “cardiopatias congênitas”; 1 para agrotóxicos; 7 para temperatura; 0 para poluição do ar + cardiopatia.
- Natureza: metadados de teses/dissertações, **não** o texto completo do Portal de Periódicos.

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

Enquanto esse fluxo não for implementado e validado, o site deve mostrar apenas o que funcionou: **CAPES — Catálogo de Teses e Dissertações**.
