mod_query_ui <- function(id) {
  ns <- NS(id)
  tagList(
    div(class = "hero", style = "padding:1.4rem 1.6rem;",
        h1("Consulta científica", style = "font-size:1.5rem;"),
        p("Selecione uma exposição para recuperar mecanismos documentados, fenótipos associados, genes, caminhos e hipóteses — sempre com o nível de evidência e as referências.")
    ),
    layout_columns(
      col_widths = c(4,4,4),
      selectInput(ns("exposure"), "Exposição",
                  choices = setNames(hierarchy$exposicao_id, hierarchy$exposicao),
                  selected = "EXP:PM25"),
      selectInput(ns("phenotype"), "Fenótipo (opcional)",
                  choices = c("Todos" = "", setNames(
                    nodes$node_id[nodes$type == "Phenotype" & nodes$node_id != "CHD:ALL"],
                    nodes$label[nodes$type == "Phenotype" & nodes$node_id != "CHD:ALL"]))),
      textInput(ns("search"), "Busca livre (gene, via, termo)", placeholder = "ex.: Wnt, NKX2-5, septação")
    ),
    uiOutput(ns("cards")),
    br(),
    layout_columns(
      col_widths = c(6,6),
      card(card_header("Evidências diretas exposição → fenótipo"), card_body(DTOutput(ns("direct")), source_note("Fonte: relations.csv + evidence.csv."))),
      card(card_header("Mecanismos documentados"), card_body(DTOutput(ns("mech")), source_note("Fonte: relations.csv + evidence.csv.")))
    ),
    br(),
    layout_columns(
      col_widths = c(7,5),
      card(card_header("Caminhos documentados até fenótipos"), card_body(DTOutput(ns("paths")), source_note("Fonte: outputs/tables/paths_exposure_phenotype.csv."))),
      card(card_header("Hipóteses candidatas (não evidenciais)"), card_body(DTOutput(ns("hyp")), source_note("Fonte: outputs/tables/hypothesis_candidates.csv; não são evidências.")))
    ),
    br(),
    card(card_header("Genes anotados aos fenótipos relacionados"), card_body(DTOutput(ns("genes")), source_note("Fonte: HPO/ClinVar/NCBI Gene via outputs/graph/relations.csv."))),
    br(),
    card(card_header("Referências que sustentam as relações recuperadas"), card_body(uiOutput(ns("refs")))),
    br(),
    card(card_header("Resultados da busca livre"), card_body(DTOutput(ns("search_results")), source_note("Fonte: outputs/graph/nodes.csv, relations.csv e evidence.csv.")))
  )
}

mod_query_server <- function(id) {
  moduleServer(id, function(input, output, session) {
    relevant <- reactive({
      exp <- input$exposure
      ph <- input$phenotype
      rel <- relations %>% filter(source_id == exp | target_id == exp)
      if (nzchar(ph)) rel <- rel %>% filter(source_id == ph | target_id == ph | grepl(ph, edge_key))
      rel
    })

    output$cards <- renderUI({
      rel <- relevant()
      direct <- rel %>% filter(relation == "EXPOSURE_ASSOCIATED_WITH_PHENOTYPE")
      mech <- rel %>% filter(relation == "EXPOSURE_MODULATES_MECHANISM")
      hyp <- hyp_candidates %>% filter(exposure_id == input$exposure)
      layout_columns(
        col_widths = c(3,3,3,3),
        kpi_card("Fenótipos com evidência direta", fmt_int(nrow(direct)), "arestas curadas", "#1B7837", source = "Fonte: outputs/graph/relations.csv."),
        kpi_card("Mecanismos documentados", fmt_int(nrow(mech)), "exposição → mecanismo", "#7570B3", source = "Fonte: outputs/graph/relations.csv."),
        kpi_card("Hipóteses candidatas", fmt_int(nrow(hyp)), "priorização por genes", "#E6A100", source = "Fonte: outputs/tables/hypothesis_candidates.csv."),
        kpi_card("Nível máximo", {
          tiers <- direct$evidence_tier_label
          if (length(tiers) == 0) "—" else tiers[1]
        }, "para este eixo", "#0B3C5D", source = "Fonte: outputs/graph/relations.csv e evidence.csv.")
      )
    })

    output$direct <- renderDT({
      d <- relevant() %>% filter(relation == "EXPOSURE_ASSOCIATED_WITH_PHENOTYPE") %>%
        transmute(Fenótipo = node_label(target_id), Nível = evidence_tier_label,
                  Confiança = round(confidence, 2), Grau = grade,
                  Referências = references, `Direção` = "")
      if (nrow(d) == 0) return(datatable(data.frame(Mensagem = "Nenhuma evidência direta curada para esta exposição."), rownames = FALSE, options = list(dom = "t")))
      datatable(d, rownames = FALSE, options = list(dom = "tp", pageLength = 6)) %>%
        formatStyle("Nível", backgroundColor = styleEqual(names(TIER_COLORS), unname(TIER_COLORS)), color = styleEqual(names(TIER_TEXT), unname(TIER_TEXT)))
    }, server = FALSE)

    output$mech <- renderDT({
      d <- relevant() %>% filter(relation == "EXPOSURE_MODULATES_MECHANISM") %>%
        transmute(Mecanismo = node_label(target_id), Nível = evidence_tier_label,
                  Espécie = species, Desenho = study_designs, Confiança = round(confidence, 2),
                  Referências = references)
      datatable(d, rownames = FALSE, options = list(dom = "tp", pageLength = 6))
    }, server = FALSE)

    output$paths <- renderDT({
      d <- paths %>% filter(source == input$exposure)
      if (nzchar(input$phenotype)) d <- d %>% filter(target == input$phenotype)
      d <- d %>% transmute(Fenótipo = node_label(target), Caminho = path, Passos = n_steps,
                           `Confiança mínima` = path_confidence_min, Camadas = layers)
      if (nrow(d) == 0) return(datatable(data.frame(Mensagem = "Nenhum caminho documentado."), rownames = FALSE, options = list(dom = "t")))
      datatable(d, rownames = FALSE, options = list(dom = "tp", pageLength = 6))
    }, server = FALSE)

    output$hyp <- renderDT({
      d <- hyp_candidates %>% filter(exposure_id == input$exposure)
      d <- d %>% transmute(Fenótipo = node_label(phenotype_id), Mecanismo = node_label(mechanism_id),
                           `Genes em comum` = n_overlap, Prioridade = priority,
                           `p (hipergeom.)` = signif(p_hyper, 3), `q FDR` = signif(q_fdr, 3),
                           Genes = overlap_genes)
      if (nrow(d) == 0) return(datatable(data.frame(Mensagem = "Nenhuma hipótese candidata para esta exposição."), rownames = FALSE, options = list(dom = "t")))
      datatable(d, rownames = FALSE, options = list(dom = "tp", pageLength = 6))
    }, server = FALSE)

    output$genes <- renderDT({
      phs <- unique(c(
        relevant()$target_id[relevant()$relation == "EXPOSURE_ASSOCIATED_WITH_PHENOTYPE"],
        hyp_candidates$phenotype_id[hyp_candidates$exposure_id == input$exposure]
      ))
      if (nzchar(input$phenotype)) phs <- intersect(phs, input$phenotype)
      d <- phenotype_genes %>% filter(phenotype_id %in% phs) %>%
        transmute(Fenótipo = node_label(phenotype_id), `Nº de genes` = n_genes,
                  `Genes (amostra)` = substr(genes, 1, 800))
      if (nrow(d) == 0) return(datatable(data.frame(Mensagem = "Sem genes anotados para os fenótipos relacionados."), rownames = FALSE, options = list(dom = "t")))
      datatable(d, rownames = FALSE, options = list(dom = "tp", pageLength = 6))
    }, server = FALSE)

    output$refs <- renderUI({
      rel <- relevant()
      ev <- evidence %>% filter(edge_key %in% rel$edge_key, grepl("^[0-9]+$", reference))
      refs <- unique(ev$reference)
      if (length(refs) == 0) return(div(class = "small-muted", "Sem referências PMID para este recorte."))
      tagList(
        p(class = "small-muted", sprintf("%s referências únicas.", length(refs))),
        HTML(paste(vapply(refs, function(r) {
          sprintf("<a href='https://pubmed.ncbi.nlm.nih.gov/%s/' target='_blank'>PMID %s</a>", r, r)
        }, character(1)), collapse = " · "))
      )
    })

    output$search_results <- renderDT({
      q <- trimws(input$search)
      if (!nzchar(q)) return(datatable(data.frame(Dica = "Digite um termo para buscar em nós e relações."), rownames = FALSE, options = list(dom = "t")))
      n <- nodes %>% filter(grepl(q, label, ignore.case = TRUE) | grepl(q, node_id, ignore.case = TRUE)) %>%
        transmute(Tipo = TYPE_LABELS[type], Rótulo = label, ID = node_id, Identificadores = identifiers)
      r <- relations %>% filter(grepl(q, source_id, ignore.case = TRUE) | grepl(q, target_id, ignore.case = TRUE) |
                                  grepl(q, references, ignore.case = TRUE)) %>%
        transmute(Tipo = "Relação", Rótulo = paste(node_label(source_id), "→", node_label(target_id)),
                  ID = relation, Identificadores = references)
      d <- bind_rows(n, r) %>% head(80)
      datatable(d, rownames = FALSE, options = list(pageLength = 8))
    }, server = FALSE)
  })
}
