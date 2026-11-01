mod_home_ui <- function(id) {
  ns <- NS(id)
  tagList(
    div(class = "hero",
        h1("GraphAmbiCardio"),
        p("Grafo de conhecimento com proveniência sobre exposições ambientais, mecanismos moleculares, processos do desenvolvimento cardíaco e cardiopatias congênitas."),
        p(class = "small-muted", style = "color:#D8EEEA;",
          "Campos dos Goytacazes, RJ · 2010–2025 · Camadas de evidência e hipótese separadas · Busca estruturada não sistemática."),
        div(style = "margin-top:.8rem;",
            tags$a(class = "btn btn-light btn-sm", href = "#", onclick = "Shiny.setInputValue('home_go_graph', Math.random()); return false;", "Explorar o grafo"),
            tags$a(class = "btn btn-outline-light btn-sm ms-2", href = "https://github.com/santosry/GraphAmbiCardio", target = "_blank", "Código e dados")
        )
    ),
    layout_columns(
      col_widths = c(3,3,3,3),
      kpi_card("Nós", textOutput(ns("kpi_nodes")), "entidades tipadas", "#0B3C5D", source = "Fonte: outputs/graph/nodes.csv."),
      kpi_card("Relações", textOutput(ns("kpi_edges")), "arestas com proveniência", "#1D7874", source = "Fonte: outputs/graph/relations.csv."),
      kpi_card("Evidências", textOutput(ns("kpi_evidence")), "linhas de evidência", "#7570B3", source = "Fonte: outputs/graph/evidence.csv."),
      kpi_card("Estudos-âncora", textOutput(ns("kpi_studies")), "curadoria manual verificada", "#D95F02", source = "Fonte: literature/curated/anchor_studies.csv.")
    ),
    br(),
    layout_columns(
      col_widths = c(7,5),
      card(
        card_header("Hierarquia de evidências do estudo"),
        card_body(
          p("As relações são classificadas em três níveis explícitos. A classificação descreve a sustentação da relação, não a importância biológica do nó."),
          DTOutput(ns("tiers")),
          source_note("Fonte: outputs/graph/relations.csv. Gradação e limitações em docs/06_EVIDENCE_GRADING.md."),
          div(class = "small-muted", style = "margin-top:.5rem;",
              "Hipóteses e regras inferidas nunca são apresentadas como evidência confirmada.")
        )
      ),
      card(
        card_header("Eixos de exposição"),
        card_body(
          p("A hierarquia foi definida antes da construção do grafo e orienta a apresentação dos resultados."),
          DTOutput(ns("hierarchy")),
          source_note("Fonte: hierarquia definida em docs/00_PROTOCOL.md e docs/07_EPI_ENV_METHODS.md."),
          note_box("<b>Umidade</b> é mantida como variável contextual/confundidora, sem conexão molecular presumida.", "info")
        )
      )
    ),
    br(),
    card(
      card_header("Como ler este painel"),
      card_body(
        layout_columns(
          col_widths = c(4,4,4),
          div(
            h6("1. Evidência"),
            p("Cada aresta tem tipo de evidência, espécie, desenho, janela de exposição, referência e limitações. Citações curadas foram verificadas contra o resumo indexado no PubMed."),
            tags$a(href = "#", onclick = "Shiny.setInputValue('home_go_evidence', Math.random()); return false;", "Ver tabela de evidências →")
          ),
          div(
            h6("2. Hipótese"),
            p("Caminhos candidatos são gerados por composição de arestas observadas e sobreposição gênica. Todos os elos ausentes são declarados. Hipóteses não entram nas análises de caminhos."),
            tags$a(href = "#", onclick = "Shiny.setInputValue('home_go_hyp', Math.random()); return false;", "Explorar hipóteses e lacunas →")
          ),
          div(
            h6("3. Contexto local"),
            p("SINASC, SIH/SUS e ERA5-Land são apresentados como contexto ecológico. Internações não são incidência; exposição de área não é exposição individual."),
            tags$a(href = "#", onclick = "Shiny.setInputValue('home_go_epi', Math.random()); return false;", "Abrir painel epidemiológico →")
          )
        ),
        source_note("Referências: docs/04_ONTOLOGY.md, docs/06_EVIDENCE_GRADING.md e docs/15_DATA_GOVERNANCE.md.")
      )
    )
  )
}

mod_home_server <- function(id) {
  moduleServer(id, function(input, output, session) {
    output$kpi_nodes <- renderText(fmt_int(nrow(nodes)))
    output$kpi_edges <- renderText(fmt_int(nrow(relations)))
    output$kpi_evidence <- renderText(fmt_int(nrow(evidence)))
    output$kpi_studies <- renderText(fmt_int(length(unique(evidence$reference[grepl("^[0-9]+$", evidence$reference)]))))

    tier_counts <- relations %>%
      filter(layer == "observed") %>%
      count(evidence_tier_label, name = "n") %>%
      mutate(rotulo = factor(evidence_tier_label, levels = TIER_ORDER)) %>%
      arrange(rotulo)
    output$tiers <- renderDT({
      datatable(tier_counts %>% select(Nível = evidence_tier_label, `Relações observadas` = n),
                rownames = FALSE, options = list(dom = "t", pageLength = 10)) |>
        formatStyle("Nível", backgroundColor = styleEqual(names(TIER_COLORS), unname(TIER_COLORS)), color = styleEqual(names(TIER_TEXT), unname(TIER_TEXT)), fontWeight = "600")
    }, server = FALSE)

    output$hierarchy <- renderDT({
      datatable(hierarchy %>% select(Ordem = ordem, Exposição = exposicao, Papel = papel, `Evidência epidemiológica` = evidencia_epidemiologica),
                rownames = FALSE, options = list(dom = "t", pageLength = 10, columnDefs = list(list(width = "30%", targets = 3))))
    }, server = FALSE)

    observeEvent(input$home_go_graph, { bslib::nav_select("main_nav", "Grafo interativo") }, ignoreInit = TRUE)
  })
}
