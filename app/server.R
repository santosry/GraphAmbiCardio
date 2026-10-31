server <- function(input, output, session) {
  session$allowReconnect(TRUE)
  mod_home_server("home")
  mod_graph_server("graph")
  mod_epi_server("epi")
  mod_evidence_server("evidence")
  mod_hypotheses_server("hyp")
  mod_query_server("query")
  mod_methods_server("methods")
  mod_about_server("about")
}
