# CAPES Catálogo de Teses e Dissertações collector (R)
# Public JSON endpoint. This is the CAPES thesis/dissertation catalogue, NOT the
# paywalled Portal de Periódicos full-text collection.
suppressPackageStartupMessages({
  library(httr)
  library(jsonlite)
})

capes_search <- function(termo, quantidade = 50, pagina = 1) {
  url <- "https://catalogodeteses.capes.gov.br/catalogo-teses/rest/busca"
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
  data <- fromJSON(content(resp, "text", encoding = "UTF-8"), flatten = TRUE)
  list(
    database = "CAPES Catálogo de Teses e Dissertações",
    query = termo,
    retrieved_at = format(Sys.time(), "%Y-%m-%dT%H:%M:%SZ", tz = "UTC"),
    total = data$total,
    n_items = nrow(data$tesesDissertacoes),
    items = data$tesesDissertacoes
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
    message(name, ": ", ifelse(is.null(res$total), "ERROR", res$total), " registros")
  }
}

if (sys.nframe() == 0) run_queries()
