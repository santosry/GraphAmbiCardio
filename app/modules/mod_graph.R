mod_graph_ui <- function(id) {
  ns <- NS(id)
  tagList(
    card(
      class = "filter-card",
      card_body(
        layout_columns(
          col_widths = c(2, 2, 2, 2, 2, 2),
          radioButtons(ns("mode"), "Visualização",
                       choices = c("Conceitual" = "conceptual", "Molecular" = "molecular", "Completo" = "full"),
                       selected = "conceptual", inline = FALSE),
          checkboxGroupInput(ns("tiers"), "Nível de evidência",
                             choices = TIER_ORDER, selected = TIER_ORDER),
          selectInput(ns("exposure"), "Exposição",
                      choices = c("Todas" = "", setNames(hierarchy$exposicao_id, hierarchy$exposicao))),
          selectInput(ns("phenotype"), "Fenótipo",
                      choices = c("Todos" = "", setNames(
                        nodes$node_id[nodes$type == "Phenotype" & nodes$node_id != "CHD:ALL"],
                        nodes$label[nodes$type == "Phenotype" & nodes$node_id != "CHD:ALL"]))),
          sliderInput(ns("conf"), "Confiança mínima", min = 0, max = 0.95, value = 0.40, step = 0.05),
          checkboxInput(ns("edge_labels"), "Rótulos das arestas", value = FALSE),
          div(
            textInput(ns("search"), "Buscar", placeholder = "PM2.5, Wnt, septação"),
            actionButton(ns("reset"), "Limpar", class = "btn-outline-secondary btn-sm w-100")
          )
        )
      )
    ),
    card(
      card_header(textOutput(ns("caption"))),
      card_body(
        class = "graph-body",
        div(role = "img", `aria-label` = "Grafo interativo de exposições, mecanismos, processos e fenótipos; use os filtros acima e a aba Evidências para uma tabela equivalente.",
            visNetworkOutput(ns("network"), height = "78vh")),
        div(class = "small-muted", style = "padding:.4rem .6rem 0;",
            "Visualização interativa. Se o grafo não carregar ou para leitura por teclado, consulte a aba Evidências.")
      )
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
      updateCheckboxInput(session, "edge_labels", value = FALSE)
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
      sprintf("%s nós · %s arestas · confiança ≥ %.2f",
              fmt_int(nrow(gd$nodes)), fmt_int(nrow(gd$edges)), input$conf)
    })

    output$network <- renderVisNetwork({
      gd <- graph_data()
      if (is.null(gd$nodes) || nrow(gd$nodes) == 0) {
        return(visNetwork(data.frame(id = character(), label = character()),
                          data.frame(from = character(), to = character())))
      }
      deg <- table(c(gd$edges$source_id, gd$edges$target_id))
      full_label <- as.character(ifelse(is.na(gd$nodes$label), gd$nodes$node_id, gd$nodes$label))
      nd <- gd$nodes %>%
        mutate(
          group = unname(TYPE_LABELS[type]),
          label = ifelse(nchar(full_label) > 32, paste0(substr(full_label, 1, 30), "…"), full_label),
          title = as.character(paste0("<b>", full_label, "</b><br>", TYPE_LABELS[type],
                                      "<br><span style='color:#666'>", node_id, "</span>")),
          color = unname(TYPE_COLORS[type]),
          shape = ifelse(type == "Phenotype", "hexagon",
                         ifelse(type == "Exposure", "square",
                                ifelse(type == "Process", "triangle", "dot"))),
          level = ifelse(type == "Exposure", 0,
                         ifelse(type %in% c("Mechanism", "Gene"), 1,
                                ifelse(type %in% c("Process", "Pathway"), 2, 3))),
          size = as.numeric(12 + 2.4 * sqrt(ifelse(is.na(deg[node_id]), 1, as.numeric(deg[node_id]))))
        ) %>%
        select(id = node_id, label, group, title, color, shape, size, level)
      show_labels <- isTRUE(input$edge_labels)
      ed <- gd$edges %>%
        mutate(
          from = source_id, to = target_id,
          label = if (show_labels) as.character(edge_label(relation)) else "",
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
      p <- visNetwork(nd, ed) %>%
        visOptions(highlightNearest = list(enabled = TRUE, degree = 1, hover = TRUE),
                   nodesIdSelection = FALSE) %>%
        visInteraction(navigationButtons = TRUE, tooltipDelay = 100, hideEdgesOnDrag = TRUE) %>%
        visNodes(font = list(size = 17, face = "Arial"), borderWidth = 1.5) %>%
        visEdges(arrows = list(to = list(enabled = TRUE, scaleFactor = 0.6)),
                 color = list(opacity = 0.7)) %>%
        visLegend(useGroups = TRUE, position = "right", ncol = 1, main = "Tipo de nó")
      if (identical(input$mode, "conceptual")) {
        p <- p %>%
          visHierarchicalLayout(direction = "LR", levelSeparation = 240,
                                nodeSpacing = 170, treeSpacing = 220,
                                blockShifting = TRUE, edgeMinimization = TRUE,
                                parentCentralization = TRUE, sortMethod = "directed") %>%
          visPhysics(enabled = FALSE) %>%
          visEdges(smooth = list(type = "cubicBezier", forceDirection = "horizontal", roundness = 0.45),
                   arrows = list(to = list(enabled = TRUE, scaleFactor = 0.6)),
                   color = list(opacity = 0.7))
      } else {
        p <- p %>%
          visPhysics(solver = "forceAtlas2Based",
                     stabilization = list(enabled = TRUE, iterations = 250),
                     forceAtlas2Based = list(gravitationalConstant = -80,
                                             centralGravity = 0.01,
                                             springLength = 180,
                                             springConstant = 0.08,
                                             damping = 0.4,
                                             avoidOverlap = 0.6)) %>%
          visEdges(smooth = list(type = "continuous"),
                   arrows = list(to = list(enabled = TRUE, scaleFactor = 0.6)),
                   color = list(opacity = 0.7))
      }
      p
    })

    output$node_details <- renderUI({
      sel <- input$network_selected
      if (is.null(sel) || !nzchar(sel)) {
        return(div(class = "empty-state", "Clique em um nó para ver dados, relações e evidências."))
      }
      n <- nodes %>% filter(node_id == sel)
      if (nrow(n) == 0) return(div(class = "empty-state", "Nó não encontrado."))
      n <- n[1, ]
      tagList(
        div(class = "detail-box",
            h4(n$label),
            p(class = "small-muted", paste0(TYPE_LABELS[n$type], " · ", n$node_id,
                                            ifelse(nzchar(n$identifiers), paste0(" · ", n$identifiers), ""))),
            if (nzchar(n$description)) p(n$description),
            DTOutput(session$ns("inc_table"))
        ),
        div(style = "height:1rem;"),
        card(card_header("Evidências"), card_body(DTOutput(session$ns("ev_table"))))
      )
    })

    output$inc_table <- renderDT({
      sel <- input$network_selected
      req(sel)
      inc <- relations %>% filter(source_id == sel | target_id == sel) %>%
        transmute(Origem = node_label(source_id), Relação = edge_label(relation),
                  Destino = node_label(target_id), Nível = evidence_tier_label,
                  Confiança = round(confidence, 2), Referências = references) %>%
        arrange(desc(Confiança))
      datatable(inc, rownames = FALSE, options = list(pageLength = 6, dom = "tp", autoWidth = TRUE)) %>%
        formatStyle("Nível", backgroundColor = styleEqual(names(TIER_COLORS), unname(TIER_COLORS)),
                    color = styleEqual(names(TIER_TEXT), unname(TIER_TEXT)))
    }, server = FALSE)

    output$ev_table <- renderDT({
      sel <- input$network_selected
      req(sel)
      inc <- relations %>% filter(source_id == sel | target_id == sel)
      ev <- evidence %>% filter(edge_key %in% inc$edge_key) %>%
        transmute(Relação = edge_label(relation), Evidência = evidence_type, Desenho = study_design,
                  Espécie = species, Referência = reference, Trecho = substr(quote, 1, 180))
      datatable(ev, rownames = FALSE, options = list(pageLength = 6, dom = "tp", autoWidth = TRUE))
    }, server = FALSE)
  })
}
