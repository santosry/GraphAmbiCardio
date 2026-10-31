ui <- bslib::page_navbar(
  id = "main_nav",
  title = div(
    class = "brand",
    span(class = "brand-mark", "GAC"),
    span(class = "brand-text", "GraphAmbiCardio")
  ),
  window_title = "GraphAmbiCardio — exposições, mecanismos e cardiopatias congênitas",
  theme = bslib::bs_theme(
    version = 5,
    primary = "#0B3C5D",
    secondary = "#1D7874",
    success = "#1B7837",
    warning = "#E6A100",
    danger = "#B2182B",
    bg = "#F7F9FB",
    fg = "#1F2A36",
    base_font = "system-ui, -apple-system, Segoe UI, Roboto, sans-serif",
    heading_font = "system-ui, -apple-system, Segoe UI, Roboto, sans-serif"
  ),
  header = tags$head(
    tags$link(rel = "stylesheet", href = "styles.css"),
    tags$script(HTML("
      setTimeout(function(){
        var el = document.getElementById('graphambicardio-loading');
        if (el) el.style.display = 'none';
      }, 2500);
    "))
  ),
  footer = div(
    class = "graphambicardio-footer",
    div(class = "container",
        HTML("GraphAmbiCardio v0.2.0 · Dados de 2026-10-31 · Código MIT · Dados de terceiros mantêm suas licenças · "),
        tags$a(href = "https://github.com/santosry/GraphAmbiCardio", target = "_blank", "Repositório"),
        " · ",
        tags$a(href = "https://github.com/santosry/GraphAmbiCardio/tree/main/docs", target = "_blank", "Documentação"),
        HTML(" · Busca estruturada não sistemática.")
    )
  ),

  bslib::nav_panel("Início", mod_home_ui("home")),
  bslib::nav_panel("Grafo interativo", mod_graph_ui("graph")),
  bslib::nav_panel("Painel epidemiológico", mod_epi_ui("epi")),
  bslib::nav_panel("Evidências", mod_evidence_ui("evidence")),
  bslib::nav_panel("Hipóteses e lacunas", mod_hypotheses_ui("hyp")),
  bslib::nav_panel("Consulta científica", mod_query_ui("query")),
  bslib::nav_panel("Métodos", mod_methods_ui("methods")),
  bslib::nav_panel("FAIR e uso de IA", mod_about_ui("about"))
)

# Overlay de carregamento (some automaticamente)
ui <- tagList(
  div(id = "graphambicardio-loading", div(class = "loader-box",
    div(class = "loader-title", "Carregando GraphAmbiCardio…"),
    div(class = "loader-bar", div(class = "loader-fill"))
  )),
  ui
)
