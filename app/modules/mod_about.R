mod_about_ui <- function(id) {
  ns <- NS(id)
  tagList(
    div(class = "hero", style = "padding:1.4rem 1.6rem;",
        h1("Transparência, FAIR e equipe", style = "font-size:1.5rem;"),
        p("Transparência sobre dados, metadados, reprodutibilidade, equipe e o papel da IA neste estudo.")
    ),
    card(
      card_header("Equipe do projeto"),
      card_body(
        p("O GraphAmbiCardio é desenvolvido por uma equipe de bacharelandos em Enfermagem pelo ",
          tags$b("Instituto Federal Fluminense, Campus Campos Guarus"), ".
",
          "A proposta integra formação em saúde, vigilância epidemiológica, ciência de dados e comunicação científica aplicada às cardiopatias congênitas."),
        div(
          class = "team-grid",
          div(
            class = "team-card",
            div(class = "team-avatar", "RS"),
            h4("Ryan de Paulo Santos"),
            div(class = "team-role", "Bacharelando em Enfermagem"),
            p(class = "team-bio", "Atua no desenvolvimento do pipeline em Python e R, integração de bases, construção do grafo de proveniência, aplicativo Shiny e publicação dos resultados."),
            div(class = "team-links",
              tags$a(href = "http://lattes.cnpq.br/7503796642571978", target = "_blank", class = "team-link-btn", "Lattes"),
              tags$a(href = "https://orcid.org/0009-0005-6770-2001", target = "_blank", class = "team-link-btn", "ORCID")
            )
          ),
          div(
            class = "team-card",
            div(class = "team-avatar", "LF"),
            h4("Letícia Maria Dias Freitas"),
            div(class = "team-role", "Bacharelanda em Enfermagem"),
            p(class = "team-bio", "Colabora na organização científica dos dados, curadoria bibliográfica, revisão dos indicadores e análise dos resultados do projeto."),
            div(class = "team-links",
              tags$a(href = "http://lattes.cnpq.br/4004634244195808", target = "_blank", class = "team-link-btn", "Lattes"),
              tags$a(href = "https://orcid.org/0009-0009-9930-9588", target = "_blank", class = "team-link-btn", "ORCID")
            )
          )
        ),
        source_note("Links para os currículos Lattes e ORCID; nomes completos, formação e produção estão nesses currículos.")
      )
    ),
    br(),
    card(
      card_header("Ciência aberta: compromisso verificável"),
      card_body(
        p("Código, dados derivados, metadados, figuras, tabelas e instruções de reprodução são públicos. ",
          "Dados individuais de saúde (SINASC/SIH) não são redistribuídos; o site publica apenas agregados e produtos derivados."),
        tags$ul(
          tags$li(tags$b("Código:"), " MIT, com pipeline modular, testes e validação automatizada."),
          tags$li(tags$b("Metadados:"), " DCAT e Frictionless Data Package com SHA-256 por recurso."),
          tags$li(tags$b("Figuras:"), " PNGs, dados de origem e manifesto com fonte, período e SHA-256."),
          tags$li(tags$b("Privacidade:"), " microdados individuais ficam fora do Git; ver docs/15_DATA_GOVERNANCE.md."),
          tags$li(tags$b("Reprodutibilidade:"), " versões fixadas (uv.lock, renv.lock), cache HTTP e comandos documentados.")
        ),
        p(
          tags$a(class = "btn btn-sm btn-outline-primary", href = "https://github.com/santosry/GraphAmbiCardio", target = "_blank", "Repositório"),
          tags$a(class = "btn btn-sm btn-outline-primary ms-2", href = "metadata.json", target = "_blank", "Metadados DCAT"),
          tags$a(class = "btn btn-sm btn-outline-primary ms-2", href = "datapackage.json", target = "_blank", "Data Package"),
          tags$a(class = "btn btn-sm btn-outline-primary ms-2", href = "https://github.com/santosry/GraphAmbiCardio/blob/main/outputs/figures/site/manifest.json", target = "_blank", "Manifesto das figuras"),
          tags$a(class = "btn btn-sm btn-outline-primary ms-2", href = "https://github.com/santosry/GraphAmbiCardio/blob/main/docs/15_DATA_GOVERNANCE.md", target = "_blank", "Governança de dados")
        ),
        source_note("Verificação: scripts/compliance/01_check.py, scripts/validation/02_schema.py e pytest. Documentação: docs/12_FAIR.md.")
      )
    ),
    br(),
    layout_columns(
      col_widths = c(6,6),
      card(
        card_header("Princípios FAIR no GraphAmbiCardio"),
        card_body(
          tags$dl(
            tags$dt("Findable"), tags$dd("Identificadores persistentes por entidade (PMID, DOI, CAPES, HPO, CID-10, ClinVar, Reactome, NCBI Gene) e metadados DCAT/Data Package."),
            tags$dt("Accessible"), tags$dd("Repositório público sem autenticação; dados de terceiros mantêm suas licenças; microdados brutos do DATASUS não são redistribuídos."),
            tags$dt("Interoperable"), tags$dd("CSV, JSON e GraphML; vocabulários padronizados; ontologia documentada."),
            tags$dt("Reusable"), tags$dd("Proveniência por evidência, camadas separadas, licença MIT para o código, dicionário de dados, pipeline e testes.")
          ),
          p(
            tags$a(class = "btn btn-sm btn-outline-primary", href = "metadata.json", target = "_blank", "Metadados DCAT (JSON)"),
            tags$a(class = "btn btn-sm btn-outline-primary ms-2", href = "datapackage.json", target = "_blank", "Data Package (JSON)"),
            tags$a(class = "btn btn-sm btn-outline-primary ms-2", href = "https://github.com/santosry/GraphAmbiCardio", target = "_blank", "Repositório")
          ),
          source_note("Fonte: fair/metadata.json e fair/datapackage.json."),
          note_box("Lacunas FAIR declaradas: releases exatos de HPO/ClinVar/Reactome não estão pinados; o grafo é uma fotografia de 2026-10-31.", "info")
        )
      ),
      card(
        card_header("Como citar"),
        card_body(
          p(tags$b("Software e dados:")),
          tags$blockquote(style = "font-size:.88rem;",
            "Ryan de Paulo Santos; Letícia Maria Dias Freitas; GraphAmbiCardio study team. GraphAmbiCardio, v0.4.0. 2026. ",
            tags$a(href = "https://github.com/santosry/GraphAmbiCardio", target = "_blank", "https://github.com/santosry/GraphAmbiCardio")
          ),
          p(tags$b("Estudos-âncora:")),
          p(class = "small-muted", "As referências PMID/DOI/CAPES de cada aresta estão na aba Evidências e em literature/curated/anchor_studies.csv."),
          p(tags$b("Licença:")),
          p("Código sob MIT. Dados de terceiros (PubMed/Europe PMC, HPO, ClinVar, Reactome, DATASUS, ERA5-Land/Open-Meteo, Crossref) mantêm suas licenças e termos."),
          source_note("Fonte: CITATION.cff, codemeta.json e LICENSE.")
        )
      )
    ),
    br(),
    card(
      card_header("Declaração de uso de inteligência artificial: Portaria CNPq nº 2.664/2026"),
      card_body(
        uiOutput(ns("ai_declaration")),
        source_note("Fonte: docs/13_DECLARACAO_IA.md.")
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
