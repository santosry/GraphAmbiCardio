# CAPES Catálogo de Teses e Dissertações collector (R)
# Public JSON endpoint. This is the CAPES thesis/dissertation catalogue, NOT the
# paywalled Portal de Periódicos full-text collection.
suppressPackageStartupMessages({
  library(httr)
  library(jsonlite)
})

capes_search <- function(termo, quantidade = 20, max_pages = Inf) {
  url <- "https://catalogodeteses.capes.gov.br/catalogo-teses/rest/busca"
  fetch_page <- function(pagina) {
    body <- list(termo = termo, quantidade = quantidade, pagina = pagina)
    resp <- POST(
      url,
      body = toJSON(body, auto_unbox = TRUE),
      encode = "raw",
      content_type_json(),
      add_headers(
        `User-Agent` = "Mozilla/5.0 (academic research; GraphAmbiCardio)",
        `Accept` = "application/json"
      ),
      timeout(90)
    )
    if (status_code(resp) != 200) stop("CAPES HTTP ", status_code(resp))
    fromJSON(content(resp, "text", encoding = "UTF-8"), flatten = TRUE)
  }

  first <- fetch_page(1)
  total <- first$total
  n_pages <- if (is.null(total) || is.na(total) || total == 0) 1 else ceiling(total / quantidade)
  n_pages <- min(n_pages, max_pages)
  pages <- list(first$tesesDissertacoes)
  if (n_pages > 1) {
    for (pagina in 2:n_pages) {
      Sys.sleep(0.3)
      pages[[pagina]] <- fetch_page(pagina)$tesesDissertacoes
    }
  }
  pages <- Filter(function(x) !is.null(x) && length(x) > 0, pages)
  items <- if (length(pages)) do.call(rbind, pages) else data.frame()
  list(
    database = "CAPES Catálogo de Teses e Dissertações",
    query = termo,
    retrieved_at = format(Sys.time(), "%Y-%m-%dT%H:%M:%SZ", tz = "UTC"),
    total = total,
    n_items = nrow(items),
    n_pages = n_pages,
    items = items
  )
}

run_queries <- function(outdir = "literature/searches") {
  dir.create(outdir, recursive = TRUE, showWarnings = FALSE)
  queries <- list(
    capes_cardiopatias_congenitas = "cardiopatias congênitas",
    capes_poluicao_ar = "poluição do ar cardiopatia",
    capes_agrotoxicos = "agrotóxicos cardiopatia",
    capes_temperatura = "temperatura cardiopatia congênita"
  )
  for (name in names(queries)) {
    res <- tryCatch(capes_search(queries[[name]]), error = function(e) {
      list(database = "CAPES", query = queries[[name]], error = conditionMessage(e),
           retrieved_at = format(Sys.time(), "%Y-%m-%dT%H:%M:%SZ", tz = "UTC"))
    })
    write_json(res, file.path(outdir, paste0(name, ".json")), auto_unbox = TRUE, pretty = TRUE)
    message(name, ": ", ifelse(is.null(res$total), "ERROR", res$total), " hits; ",
            ifelse(is.null(res$n_items), 0, res$n_items), " itens recuperados em ",
            ifelse(is.null(res$n_pages), 0, res$n_pages), " página(s)")
  }
}

if (sys.nframe() == 0) run_queries()
