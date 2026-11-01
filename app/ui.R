ui <- bslib::page_navbar(
  id = "main_nav",
  lang = "pt-BR",
  title = div(
    class = "brand",
    span(class = "brand-mark", "GAC"),
    span(class = "brand-text", "GraphAmbiCardio")
  ),
  window_title = "GraphAmbiCardio — exposições, mecanismos e cardiopatias congênitas",
  theme = bslib::bs_theme(
    version = 5,
    primary = "#440154",
    secondary = "#31688E",
    success = "#35B779",
    warning = "#B5DE2B",
    danger = "#463480",
    bg = "#FAFAFC",
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
        HTML("GraphAmbiCardio v0.3.0 · Dados de 2026-10-31 · Código MIT · Dados de terceiros mantêm suas licenças · "),
        tags$a(href = "https://github.com/santosry/GraphAmbiCardio", target = "_blank", "Repositório"),
        " · ",
        tags$a(href = "https://github.com/santosry/GraphAmbiCardio/tree/main/docs", target = "_blank", "Documentação"),
        HTML(" · Contato: "),
        tags$a(href = "mailto:ryan.paulo@gsuite.iff.edu.br", "ryan.paulo@gsuite.iff.edu.br"),
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
  bslib::nav_panel("Transparência e equipe", mod_about_ui("about"))
)

# Overlay de carregamento (some automaticamente)
ui <- tagList(
  tags$a(class = "visually-hidden-focusable skip-link", href = "#main_nav", "Pular para a navegação"),
  div(id = "graphambicardio-loading", div(class = "loader-box",
    div(class = "loader-title", "Carregando GraphAmbiCardio…"),
    div(class = "loader-bar", div(class = "loader-fill"))
  )),
  ui
)
