mod_about_ui <- function(id) {
  ns <- NS(id)
  tagList(
    div(class = "hero", style = "padding:1.4rem 1.6rem;",
        h1("FAIR, licenças e uso de inteligência artificial", style = "font-size:1.5rem;"),
        p("Transparência sobre dados, metadados, reprodutibilidade e o papel da IA neste estudo.")
    ),
    layout_columns(
      col_widths = c(6,6),
      card(
        card_header("Princípios FAIR no GraphAmbiCardio"),
        card_body(
          tags$dl(
            tags$dt("Findable"), tags$dd("Identificadores persistentes por entidade (PMID, DOI, HPO, CID-10, ClinVar, Reactome, NCBI Gene) e metadados DCAT/Data Package."),
            tags$dt("Accessible"), tags$dd("Repositório público sem autenticação; dados de terceiros mantêm suas licenças; microdados brutos do DATASUS não são redistribuídos."),
            tags$dt("Interoperable"), tags$dd("CSV, JSON e GraphML; vocabulários padronizados; ontologia documentada."),
            tags$dt("Reusable"), tags$dd("Proveniência por evidência, camadas separadas, licença MIT para o código, dicionário de dados, pipeline e testes.")
          ),
          p(
            tags$a(class = "btn btn-sm btn-outline-primary", href = "metadata.json", target = "_blank", "Metadados DCAT (JSON)"),
            tags$a(class = "btn btn-sm btn-outline-primary ms-2", href = "datapackage.json", target = "_blank", "Data Package (JSON)"),
            tags$a(class = "btn btn-sm btn-outline-primary ms-2", href = "https://github.com/santosry/GraphAmbiCardio", target = "_blank", "Repositório")
          ),
          note_box("Lacunas FAIR declaradas: releases exatos de HPO/ClinVar/Reactome não estão pinados; o grafo é uma fotografia de 2026-10-31.", "info")
        )
      ),
      card(
        card_header("Como citar"),
        card_body(
          p(tags$b("Software e dados:")),
          tags$blockquote(style = "font-size:.88rem;",
            "GraphAmbiCardio study team. GraphAmbiCardio, v0.3.0. 2026. ",
            tags$a(href = "https://github.com/santosry/GraphAmbiCardio", target = "_blank", "https://github.com/santosry/GraphAmbiCardio")
          ),
          p(tags$b("Estudos-âncora:")),
          p(class = "small-muted", "As referências PMID/DOI de cada aresta estão na aba Evidências e em literature/curated/anchor_studies.csv."),
          p(tags$b("Licença:")),
          p("Código sob MIT. Dados de terceiros (PubMed/Europe PMC, HPO, ClinVar, Reactome, DATASUS, ERA5-Land/Open-Meteo, Crossref) mantêm suas licenças e termos.")
        )
      )
    ),
    br(),
    card(
      card_header("Declaração de uso de inteligência artificial — Portaria CNPq nº 2.664/2026"),
      card_body(
        uiOutput(ns("ai_declaration"))
      )
    )
  )
}

mod_about_server <- function(id) {
  moduleServer(id, function(input, output, session) {
    output$ai_declaration <- renderUI({
      path <- file.path("data", "ai_declaration.md")
      if (!file.exists(path)) return(div(class = "small-muted", "Declaração não encontrada no bundle."))
      html <- commonmark::markdown_html(paste(readLines(path, encoding = "UTF-8", warn = FALSE), collapse = "\n"))
      HTML(html)
    })
  })
}
