mod_hypotheses_ui <- function(id) {
  ns <- NS(id)
  tagList(
    note_box("<b>Hipóteses não são evidências.</b> Esta camada é gerada por duas regras explícitas: ",
             "(1) composição de arestas observadas (exposição → mecanismo → processo) e ",
             "(2) sobreposição entre conjuntos gênicos canônicos de mecanismos e genes anotados a fenótipos. ",
             "Nenhuma hipótese entra nas análises de caminhos, centralidade ou nas conclusões. ",
             "Cada linha declara o elo ausente que precisaria ser testado.", "danger"),
    layout_columns(
      col_widths = c(3,3,3,3),
      kpi_card("Caminhos candidatos", textOutput(ns("kpi_paths")), "com elo processo→fenótipo ausente", "#7570B3"),
      kpi_card("Hipóteses por genes", textOutput(ns("kpi_cand")), "sobreposição gênica", "#E6A100"),
      kpi_card("Lacunas explícitas", textOutput(ns("kpi_gaps")), "exposições, mecanismos e processos", "#B2182B"),
      kpi_card("Regra de inclusão", "≥ 2 genes", "sobreposição mínima; prioridade por nº de genes", "#4A6FA5")
    ),
    br(),
    card(
      card_header("Caminhos candidatos com elo ausente"),
      card_body(
        p("Cadeias documentadas até um processo de desenvolvimento que ainda não possui aresta curada para um fenótipo específico."),
        DTOutput(ns("paths")),
        div(style = "margin-top:.5rem;", downloadButton(ns("dl_paths"), "Baixar caminhos (CSV)", class = "btn-sm btn-outline-primary"))
      )
    ),
    br(),
    card(
      card_header("Hipóteses por sobreposição gênica"),
      card_body(
        p("A sobreposição indica prioridade de investigação, não mecanismo. O elo entre o mecanismo e o processo/fenótipo permanece não demonstrado."),
        DTOutput(ns("cands")),
        div(style = "margin-top:.5rem;", downloadButton(ns("dl_cands"), "Baixar hipóteses (CSV)", class = "btn-sm btn-outline-primary"))
      )
    ),
    br(),
    card(
      card_header("Lacunas identificadas pelo grafo"),
      card_body(
        p("Entidades sem aresta curada de saída. As lacunas são resultados, não falhas de busca."),
        DTOutput(ns("gaps"))
      )
    )
  )
}

mod_hypotheses_server <- function(id) {
  moduleServer(id, function(input, output, session) {
    output$kpi_paths <- renderText(fmt_int(nrow(candidate_paths)))
    output$kpi_cand <- renderText(fmt_int(nrow(hyp_candidates)))
    output$kpi_gaps <- renderText(fmt_int(sum(nzchar(gaps$gap_type))))

    output$paths <- renderDT({
      d <- candidate_paths %>%
        transmute(Exposição = node_label(exposure_id), Processo = node_label(process_id),
                  Caminho = path, Passos = n_steps, `Elo ausente` = missing_link)
      datatable(d, rownames = FALSE, options = list(pageLength = 8, scrollX = TRUE))
    }, server = FALSE)

    output$cands <- renderDT({
      d <- hyp_candidates %>%
        transmute(Exposição = node_label(exposure_id), Fenótipo = node_label(phenotype_id),
                  Mecanismo = node_label(mechanism_id), `Genes em comum` = n_overlap,
                  `Fração do conjunto` = round(gene_set_fraction, 2), Prioridade = priority,
                  `Genes` = overlap_genes, `Elo ausente` = missing_link)
      datatable(d, rownames = FALSE, options = list(pageLength = 8, scrollX = TRUE))
    }, server = FALSE)

    output$gaps <- renderDT({
      d <- gaps %>% filter(nzchar(gap_type)) %>%
        transmute(Tipo = entity_type, Entidade = node_label(entity_id),
                  `Arestas curadas` = n_curated_outgoing, Lacuna = gap_type)
      datatable(d, rownames = FALSE, options = list(pageLength = 10, scrollX = TRUE))
    }, server = FALSE)

    output$dl_paths <- downloadHandler(
      filename = function() paste0("graphambicardio_caminhos_candidatos_", Sys.Date(), ".csv"),
      content = function(file) readr::write_csv(candidate_paths, file)
    )
    output$dl_cands <- downloadHandler(
      filename = function() paste0("graphambicardio_hipoteses_", Sys.Date(), ".csv"),
      content = function(file) readr::write_csv(hyp_candidates, file)
    )
  })
}
