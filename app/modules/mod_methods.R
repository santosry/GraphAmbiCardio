mod_methods_ui <- function(id) {
  ns <- NS(id)
  tagList(
    div(class = "hero", style = "padding:1.4rem 1.6rem;",
        h1("Métodos e limites", style = "font-size:1.5rem;"),
        p("Busca estruturada não sistemática, curadoria dirigida e integração de bases públicas. O estudo não é uma revisão sistemática e não estima efeitos causais.")
    ),
    layout_columns(
      col_widths = c(3,3,3,3),
      kpi_card("Registros recuperados", textOutput(ns("n_records")), "PubMed + Europe PMC", "#0B3C5D", source = "Fonte: literature/searches/*.json."),
      kpi_card("Registros únicos", "1.095", "após deduplicação", "#1D7874", source = "Fonte: deduplicação PMID → DOI → título; docs/02."),
      kpi_card("Estudos-âncora", textOutput(ns("n_anchors")), "lidos manualmente", "#D95F02", source = "Fonte: literature/curated/anchor_studies.csv."),
      kpi_card("Arestas curadas", textOutput(ns("n_curated")), "citações verificadas", "#E7298A", source = "Fonte: literature/curated/curated_edges.csv; verificação no PubMed.")
    ),
    br(),
    layout_columns(
      col_widths = c(6,6),
      card(
        card_header("Desenho"),
        card_body(
          p("O estudo combina:"),
          tags$ul(
            tags$li("cinco domínios de busca pré-registrados (exposição→CHD, exposição→mecanismo, mecanismo→cardiogênese, cardiogênese→fenótipo, gene→fenótipo);"),
            tags$li("196 pares exposição × fenótipo para mapear densidade e lacunas;"),
            tags$li("curadoria manual de 33 estudos-âncora, com trechos verbatim verificados contra o PubMed;"),
            tags$li("integração de HPO, ClinVar, NCBI Gene, Reactome e Enrichr;"),
            tags$li("dados locais de SINASC, SIH/SUS e ERA5-Land (2010–2025).")
          ),
          source_note("Referências: docs/00_PROTOCOL.md e docs/02_SEARCH_STRATEGY.md."),
          note_box("<b>Não é revisão sistemática.</b> Não houve triagem dupla de todos os registros, revisão de texto completo ou aplicação de instrumentos formais de risco de viés. É uma busca estruturada com curadoria dirigida.", "warning")
        )
      ),
      card(
        card_header("Buscas e acesso"),
        card_body(
          tags$ul(
            tags$li(tags$b("PubMed/MEDLINE:"), " E-utilities; 1.512 / 8.520 / 6.736 / 7.681 / 992 registros nos cinco domínios."),
            tags$li(tags$b("Europe PMC:"), " 1.599 / 171 / 39 / 593 / 2.387."),
            tags$li(tags$b("SciELO:"), " metadados via Crossref (prefixo DOI 10.1590), pois a interface de busca retornou HTTP 403 a clientes automatizados."),
            tags$li(tags$b("CAPES:"), " Catálogo de Teses e Dissertações (API pública); 552 teses para “cardiopatias congênitas”."),
            tags$li(tags$b("Portal de Periódicos CAPES:"), " sem API oficial aberta; exige autenticação institucional e não foi utilizado. Servidores MCP comunitários foram avaliados e não adotados (ver docs/16_CAPES_MCP.md).")
          ),
          source_note("Fonte: literature/searches/*.json; detalhes em docs/02_SEARCH_STRATEGY.md e docs/03_DATABASE_CATALOG.md.")
        )
      )
    ),
    br(),
    layout_columns(
      col_widths = c(6,6),
      card(
        card_header("Níveis de evidência"),
        card_body(
          p("A confiança combina tipo de evidência (0,7) e desenho (0,3), com bônus de replicação/concordância e penalidades por estudo único, não significância e contradição."),
          tags$ul(
            tags$li(tags$b("Bem sustentada:"), " evidência humana direta com estimativa clara ou genética humana replicada (A/B)."),
            tags$li(tags$b("Plausível (experimental):"), " experimento humano, animal ou celular (C)."),
            tags$li(tags$b("Não demonstrada:"), " evidência indireta, grau D/E, hipótese ou regra inferida."),
            tags$li(tags$b("Contextual:"), " variáveis ecológicas/indicadores, sem pretensão causal.")
          ),
          source_note("Referência: docs/06_EVIDENCE_GRADING.md. A confiança é heurística, não probabilidade.")
        )
      ),
      card(
        card_header("Limitações principais"),
        card_body(
          tags$ul(
            tags$li("Subnotificação grave no SINASC: 52 casos de CHD core (Q20–Q26) em 98.598 nascimentos (0,53/1.000), além de 8 registros Q27–Q28."),
            tags$li("2023–2024 sem microdados; usados apenas agregados do TabNet."),
            tags$li("SIH: AIH ≠ pessoa; 55% das internações fora do município."),
            tags$li("Exposição de área (ERA5-Land para clima; PM2,5 do VIGIAR), não individual."),
            tags$li("Maioria das cadeias mecanísticas é experimental e em doses não equivalentes às humanas."),
            tags$li("Dados de HPO/ClinVar são orientados a doenças mendelianas/sindrômicas."),
          )
        )
      )
    ),
    br(),
    card(
      card_header("Densidade da literatura por par exposição × fenótipo"),
      card_body(
        DTOutput(ns("feas")),
        source_note("Fonte: reports/feasibility_pair_matrix.csv; contagens PubMed. A contagem é bibliométrica e não mede qualidade."),
        div(class = "small-muted", "Pares com zero registros são lacunas de busca, não ausência de risco.")
      )
    ),
    br(),
    card(
      card_header("Documentação completa"),
      card_body(
        tags$ul(
          tags$li(tags$a(href = "https://github.com/santosry/GraphAmbiCardio/blob/main/docs/00_PROTOCOL.md", target = "_blank", "Protocolo")),
          tags$li(tags$a(href = "https://github.com/santosry/GraphAmbiCardio/blob/main/docs/01_SCIENTIFIC_VIABILITY.md", target = "_blank", "Viabilidade científica (Fase A)")),
          tags$li(tags$a(href = "https://github.com/santosry/GraphAmbiCardio/blob/main/docs/02_SEARCH_STRATEGY.md", target = "_blank", "Estratégia de busca e PRISMA-ScR")),
          tags$li(tags$a(href = "https://github.com/santosry/GraphAmbiCardio/blob/main/docs/06_EVIDENCE_GRADING.md", target = "_blank", "Gradação de evidência")),
          tags$li(tags$a(href = "https://github.com/santosry/GraphAmbiCardio/blob/main/docs/09_LIMITATIONS_AND_GAPS.md", target = "_blank", "Limitações e lacunas")),
          tags$li(tags$a(href = "https://github.com/santosry/GraphAmbiCardio/blob/main/docs/13_DECLARACAO_IA.md", target = "_blank", "Declaração de uso de IA"))
        )
      )
    )
  )
}

mod_methods_server <- function(id) {
  moduleServer(id, function(input, output, session) {
    output$n_records <- renderText("1.450")
    output$n_anchors <- renderText(fmt_int(length(unique(evidence$reference[grepl("^[0-9]+$", evidence$reference)]))))
    output$n_curated <- renderText(fmt_int(sum(relations$layer == "observed")))

    output$feas <- renderDT({
      d <- feasibility %>%
        group_by(Exposição = exposure) %>%
        summarise(Pares = n(), `Com registro` = sum(n_pubmed > 0), `Sem registro` = sum(n_pubmed == 0),
                  `Total de registros` = sum(n_pubmed), .groups = "drop") %>%
        arrange(desc(`Total de registros`))
      datatable(d, rownames = FALSE, options = list(pageLength = 8, dom = "tp"))
    }, server = FALSE)
  })
}
