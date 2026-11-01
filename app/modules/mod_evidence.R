mod_evidence_ui <- function(id) {
  ns <- NS(id)
  tagList(
    note_box("Cada linha é uma relação agregada. Clique em uma linha para ver <b>todas</b> as evidências que a sustentam, ",
             "com espécie, desenho, janela de exposição, trecho verificado e referência. ",
             "A confiança é uma heurística pré-registrada, não uma probabilidade.", "info"),
    layout_columns(
      col_widths = c(3,3,3,3),
      selectInput(ns("tier"), "Nível", choices = c("Todos" = "", TIER_ORDER)),
      selectInput(ns("relation"), "Tipo de relação", choices = c("Todas" = "", sort(unique(relations$relation)))),
      selectInput(ns("exposure"), "Exposição", choices = c("Todas" = "", setNames(
        nodes$node_id[nodes$type == "Exposure"], nodes$label[nodes$type == "Exposure"]))),
      selectInput(ns("phenotype"), "Fenótipo", choices = c("Todos" = "", setNames(
        nodes$node_id[nodes$type == "Phenotype"], nodes$label[nodes$type == "Phenotype"])))
    ),
    card(
      card_header(textOutput(ns("caption"))),
      card_body(
        DTOutput(ns("table")),
        source_note("Fonte: outputs/graph/relations.csv; 54 arestas curadas + bases estruturadas. Confiança e gradação em docs/06."),
        div(style = "margin-top:.6rem;", downloadButton(ns("download"), "Baixar relações filtradas (CSV)", class = "btn-sm btn-outline-primary"))
      )
    ),
    br(),
    card(
      card_header("Evidências da relação selecionada"),
      card_body(uiOutput(ns("detail")),
                source_note("Fonte: outputs/graph/evidence.csv; trechos verificados contra o PubMed."))
    )
  )
}

mod_evidence_server <- function(id) {
  moduleServer(id, function(input, output, session) {
    filtered <- reactive({
      d <- relations
      if (nzchar(input$tier)) d <- d %>% filter(evidence_tier_label == input$tier)
      if (nzchar(input$relation)) d <- d %>% filter(relation == input$relation)
      if (nzchar(input$exposure)) d <- d %>% filter(source_id == input$exposure | target_id == input$exposure)
      if (nzchar(input$phenotype)) d <- d %>% filter(source_id == input$phenotype | target_id == input$phenotype)
      d %>% arrange(desc(confidence))
    })

    output$caption <- renderText(sprintf("%s relações exibidas", fmt_int(nrow(filtered()))))

    output$table <- renderDT({
      d <- filtered() %>%
        transmute(Origem = node_label(source_id), Relação = edge_label(relation),
                  Destino = node_label(target_id), Camada = layer, Nível = evidence_tier_label,
                  Confiança = round(confidence, 2), Grau = grade, `n evidências` = n_evidence,
                  Referências = references)
      datatable(d, rownames = FALSE, selection = "single",
                options = list(pageLength = 12, order = list(list(5, "desc")))) %>%
        formatStyle("Nível", backgroundColor = styleEqual(names(TIER_COLORS), unname(TIER_COLORS)), color = styleEqual(names(TIER_TEXT), unname(TIER_TEXT)))
    }, server = FALSE)

    output$download <- downloadHandler(
      filename = function() paste0("graphambicardio_relacoes_", Sys.Date(), ".csv"),
      content = function(file) readr::write_csv(filtered(), file)
    )

    output$detail <- renderUI({
      idx <- input$table_rows_selected
      if (length(idx) == 0) return(div(class = "small-muted", "Selecione uma relação na tabela acima."))
      r <- filtered()[idx, ]
      ev <- evidence %>% filter(edge_key == r$edge_key)
      if (nrow(ev) == 0) return(div(class = "small-muted", "Sem linhas de evidência para esta relação."))
      rows <- lapply(seq_len(nrow(ev)), function(i) {
        e <- ev[i, ]
        div(class = "detail-box", style = "margin-bottom:.7rem;",
            p(tags$b(node_label(r$source_id), " → ", node_label(r$target_id)), " · ", tier_badge(r$evidence_tier_label)),
            p(tags$b("Evidência: "), e$evidence_type, " · ", tags$b("Desenho: "), e$study_design,
              " · ", tags$b("Espécie: "), e$species),
            p(tags$b("População/modelo: "), e$population_or_model),
            p(tags$b("Janela: "), e$exposure_window, " · ", tags$b("Direção: "), e$effect_direction),
            if (nzchar(e$quote)) tags$blockquote(style = "font-size:.85rem; color:#444;", e$quote),
            p(tags$b("Referência: "), HTML(ref_link(e$reference, e$reference_type)),
              if (nzchar(e$source_database)) paste0(" · ", e$source_database)),
            if (nzchar(e$notes)) p(class = "small-muted", tags$b("Limitações/notas: "), e$notes)
        )
      })
      tagList(rows)
    })
  })
}
