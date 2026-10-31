mod_graph_ui <- function(id) {
  ns <- NS(id)
  layout_sidebar(
    sidebar = sidebar(
      width = 330,
      radioButtons(ns("mode"), "Modo de visualização",
                   choices = c("Conceitual" = "conceptual", "Molecular (sem variantes)" = "molecular", "Completo" = "full"),
                   selected = "conceptual"),
      checkboxGroupInput(ns("tiers"), "Nível de evidência",
                         choices = TIER_ORDER, selected = TIER_ORDER),
      selectInput(ns("exposure"), "Focar em uma exposição",
                  choices = c("Todas" = "", setNames(hierarchy$exposicao_id, hierarchy$exposicao))),
      selectInput(ns("phenotype"), "Focar em um fenótipo",
                  choices = c("Todos" = "", setNames(
                    nodes$node_id[nodes$type == "Phenotype" & nodes$node_id != "CHD:ALL"],
                    nodes$label[nodes$type == "Phenotype" & nodes$node_id != "CHD:ALL"]))),
      sliderInput(ns("conf"), "Confiança mínima da aresta", min = 0, max = 0.95, value = 0.40, step = 0.05),
      textInput(ns("search"), "Buscar rótulo", placeholder = "ex.: PM2.5, Wnt, septação"),
      actionButton(ns("reset"), "Limpar filtros", class = "btn-outline-secondary btn-sm"),
      hr(),
      div(class = "small-muted",
          "Arraste os nós, use a roda para zoom e clique em um nó para ver as evidências. ",
          "Arestas tracejadas indicam hipótese ou regra inferida; a cor indica o nível de evidência.")
    ),
    card(
      card_header(textOutput(ns("caption"))),
      card_body(visNetworkOutput(ns("network"), height = "640px"))
    ),
    card(
      card_header("Detalhes do nó selecionado"),
      card_body(uiOutput(ns("node_details")))
    )
  )
}

mod_graph_server <- function(id) {
  moduleServer(id, function(input, output, session) {
    observeEvent(input$reset, {
      updateRadioButtons(session, "mode", selected = "conceptual")
      updateCheckboxGroupInput(session, "tiers", selected = TIER_ORDER)
      updateSelectInput(session, "exposure", selected = "")
      updateSelectInput(session, "phenotype", selected = "")
      updateSliderInput(session, "conf", value = 0.40)
      updateTextInput(session, "search", value = "")
    })

    allowed_types <- reactive({
      switch(input$mode,
             conceptual = c("Exposure", "Mechanism", "Process", "Phenotype"),
             molecular = c("Exposure", "Mechanism", "Process", "Phenotype", "Gene", "Pathway"),
             full = c("Exposure", "Mechanism", "Process", "Phenotype", "Gene", "Pathway", "Variant"))
    })

    graph_data <- reactive({
      req(input$tiers)
      nl <- nodes %>% filter(type %in% allowed_types())
      if (nzchar(input$search)) {
        nl <- nl %>% filter(grepl(input$search, label, ignore.case = TRUE) |
                            grepl(input$search, node_id, ignore.case = TRUE))
      }
      rl <- relations %>%
        filter(layer %in% c("observed", "structured", "inferred", "hypothesis"),
               evidence_tier_label %in% input$tiers,
               confidence >= input$conf,
               source_id %in% nl$node_id, target_id %in% nl$node_id)
      focus <- c(input$exposure, input$phenotype)
      focus <- focus[nzchar(focus)]
      if (length(focus) > 0) {
        g <- igraph::graph_from_data_frame(rl[, c("source_id", "target_id")],
                                           directed = FALSE, vertices = nl$node_id)
        keep <- unique(unlist(lapply(focus, function(f) {
          if (f %in% igraph::V(g)$name) {
            igraph::V(g)$name[igraph::neighborhood(g, order = 2, nodes = f)[[1]]]
          } else character(0)
        })))
        keep <- union(keep, focus)
        nl <- nl %>% filter(node_id %in% keep)
        rl <- rl %>% filter(source_id %in% keep, target_id %in% keep)
      }
      list(nodes = nl, edges = rl)
    })

    output$caption <- renderText({
      gd <- graph_data()
      sprintf("%s nós e %s arestas · modo %s · confiança ≥ %.2f",
              fmt_int(nrow(gd$nodes)), fmt_int(nrow(gd$edges)),
              switch(input$mode, conceptual = "conceitual", molecular = "molecular", full = "completo"),
              input$conf)
    })

    output$network <- renderVisNetwork({
      gd <- graph_data()
      if (is.null(gd$nodes) || nrow(gd$nodes) == 0) {
        return(visNetwork(data.frame(id = character(), label = character()),
                          data.frame(from = character(), to = character())))
      }
      deg <- table(c(gd$edges$source_id, gd$edges$target_id))
      nd <- gd$nodes %>%
        mutate(
          group = unname(TYPE_LABELS[type]),
          label = as.character(ifelse(is.na(label), node_id, label)),
          title = as.character(paste0("<b>", label, "</b><br>", TYPE_LABELS[type],
                         "<br><span style='color:#888'>", node_id, "</span>")),
          color = unname(TYPE_COLORS[type]),
          shape = ifelse(type == "Phenotype", "hexagon",
                         ifelse(type == "Exposure", "square",
                                ifelse(type == "Process", "triangle", "dot"))),
          size = as.numeric(12 + 2.4 * sqrt(ifelse(is.na(deg[node_id]), 1, as.numeric(deg[node_id]))))
        ) %>%
        select(id = node_id, label, group, title, color, shape, size)
      ed <- gd$edges %>%
        mutate(
          from = source_id, to = target_id,
          label = as.character(edge_label(relation)),
          label = ifelse(is.na(label), "", label),
          title = as.character(paste0("<b>", edge_label(relation), "</b><br>", evidence_tier_label,
                         "<br>confiança: ", round(confidence, 2), " (", grade, ")",
                         "<br>referências: ", references)),
          color = unname(TIER_COLORS[evidence_tier_label]),
          dashes = layer %in% c("hypothesis", "inferred"),
          width = 0.6 + 3.2 * confidence,
          arrows = ifelse(layer == "hypothesis", "to;from", "to")
        ) %>%
        select(from, to, label, title, color, dashes, width, arrows)
      visNetwork(nd, ed) %>%
        visOptions(highlightNearest = list(enabled = TRUE, degree = 1, hover = TRUE),
                   nodesIdSelection = FALSE) %>%
        visInteraction(navigationButtons = TRUE, tooltipDelay = 120) %>%
        visPhysics(solver = "forceAtlas2Based",
                   stabilization = list(enabled = TRUE, iterations = 200)) %>%
        visLegend(useGroups = TRUE, position = "right", ncol = 1, main = "Tipo de nó") %>%
        visEdges(smooth = list(type = "continuous"))
    })

    output$node_details <- renderUI({
      sel <- input$network_selected
      if (is.null(sel) || !nzchar(sel)) {
        return(div(class = "small-muted", "Clique em um nó do grafo para ver seus dados, relações e evidências."))
      }
      n <- nodes %>% filter(node_id == sel)
      if (nrow(n) == 0) return(div(class = "small-muted", "Nó não encontrado."))
      n <- n[1, ]
      tagList(
        div(class = "detail-box",
            h4(n$label),
            p(class = "small-muted", paste0(TYPE_LABELS[n$type], " · ", n$node_id,
                                            ifelse(nzchar(n$identifiers), paste0(" · ", n$identifiers), ""))),
            if (nzchar(n$description)) p(n$description),
            DTOutput(session$ns("inc_table"))
        ),
        br(),
        card(card_header("Evidências das relações incidentes"),
             card_body(DTOutput(session$ns("ev_table"))))
      )
    })

    output$inc_table <- renderDT({
      sel <- input$network_selected
      req(sel)
      inc <- relations %>% filter(source_id == sel | target_id == sel) %>%
        transmute(Origem = node_label(source_id), Relação = edge_label(relation),
                  Destino = node_label(target_id), Nível = evidence_tier_label,
                  Confiança = round(confidence, 2), Grau = grade, Referências = references) %>%
        arrange(desc(Confiança))
      datatable(inc, rownames = FALSE, options = list(pageLength = 8, scrollX = TRUE, dom = "tp")) %>%
        formatStyle("Nível", backgroundColor = styleEqual(names(TIER_COLORS), unname(TIER_COLORS)), color = "white")
    }, server = FALSE)

    output$ev_table <- renderDT({
      sel <- input$network_selected
      req(sel)
      inc <- relations %>% filter(source_id == sel | target_id == sel)
      ev <- evidence %>% filter(edge_key %in% inc$edge_key) %>%
        transmute(Relação = edge_label(relation), Evidência = evidence_type, Desenho = study_design,
                  Espécie = species, Referência = reference, Contexto = context,
                  Trecho = substr(quote, 1, 220))
      datatable(ev, rownames = FALSE, options = list(pageLength = 8, scrollX = TRUE, dom = "tp"))
    }, server = FALSE)
  })
}
