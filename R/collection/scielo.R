# SciELO collector (R) via Crossref metadata restricted to the SciELO DOI prefix.
#
# Why Crossref: the SciELO search interface (search.scielo.org) returned HTTP 403
# / Bunny Shield challenges to automated clients on 2026-10-31, and the
# ArticleMeta API supports lookup by PID/ISSN but not free-text search. SciELO
# articles are registered with the 10.1590 DOI prefix, so Crossref provides a
# reproducible, official metadata route. The direct-interface attempt is kept
# below and its status is recorded for transparency.
suppressPackageStartupMessages({
  library(httr)
  library(jsonlite)
  library(stringr)
})

CHD_TERMS <- c("cardiopatia", "cardiopatias", "congênita", "congenita", "congenital heart",
               "heart defect", "cardiac malformation", "anomalia cardíaca", "defeito cardíaco")
EXPOSURE_TERMS <- c("poluição", "poluicao", "material particulado", "pm2.5", "pm10", "ozônio", "ozonio",
                    "agrotóxico", "agrotoxico", "pesticida", "temperatura", "calor", "umidade",
                    "exposição", "exposicao", "ambiental", "ar ", "solvente", "metal", "fumaça")

`%||%` <- function(a, b) if (is.null(a) || length(a) == 0) b else a

crossref_scielo <- function(query, rows = 100, from = "2010-01-01") {
  resp <- GET(
    "https://api.crossref.org/works",
    query = list(
      query = query,
      filter = paste0("prefix:10.1590,from-pub-date:", from),
      rows = rows,
      select = "DOI,title,container-title,issued,author,abstract,URL,type",
      mailto = "ryan.paulo@gsuite.iff.edu.br"
    ),
    add_headers(`User-Agent` = "GraphAmbiCardio/0.1 (mailto:ryan.paulo@gsuite.iff.edu.br)"),
    timeout(120)
  )
  if (status_code(resp) != 200) stop("Crossref HTTP ", status_code(resp))
  data <- fromJSON(content(resp, "text", encoding = "UTF-8"), simplifyVector = FALSE)
  items <- data$message$items
  flat <- lapply(items, function(it) {
    title <- paste(unlist(it$title), collapse = " ")
    abstract <- gsub("<[^>]+>", " ", paste(unlist(it$abstract), collapse = " "))
    journal <- paste(unlist(it$`container-title`), collapse = "; ")
    year <- tryCatch(it$issued$`date-parts`[[1]][[1]], error = function(e) NA)
    authors <- tryCatch(paste(vapply(it$author, function(a) paste(a$given, a$family), ""), collapse = "; "),
                        error = function(e) "")
    list(doi = it$DOI, title = title, journal = journal, year = year,
         authors = authors, abstract = abstract, url = it$URL %||% "")
  })
  text_all <- tolower(paste(vapply(flat, function(x) paste(x$title, x$abstract), ""), collapse = " "))
  has_chd <- any(vapply(CHD_TERMS, function(t) grepl(tolower(t), text_all, fixed = TRUE), logical(1)))
  has_exp <- any(vapply(EXPOSURE_TERMS, function(t) grepl(tolower(t), text_all, fixed = TRUE), logical(1)))
  list(
    database = "SciELO (via Crossref, DOI prefix 10.1590)",
    query = query,
    retrieved_at = format(Sys.time(), "%Y-%m-%dT%H:%M:%SZ", tz = "UTC"),
    total_results = data$message$`total-results`,
    n_retrieved = length(flat),
    n_with_chd_terms = sum(vapply(flat, function(x) any(vapply(CHD_TERMS, function(t) grepl(tolower(t), tolower(paste(x$title, x$abstract)), fixed = TRUE), logical(1))), logical(1))),
    query_has_chd_and_exposure_terms = has_chd && has_exp,
    items = flat
  )
}

run_queries <- function(outdir = "literature/searches") {
  dir.create(outdir, recursive = TRUE, showWarnings = FALSE)
  queries <- list(
    scielo_cardiopatia_ambiente = "cardiopatia congênita exposição ambiental",
    scielo_poluicao_ar = "cardiopatia congênita poluição do ar material particulado",
    scielo_agrotoxicos = "cardiopatia congênita agrotóxicos pesticidas",
    scielo_temperatura = "cardiopatia congênita temperatura calor",
    scielo_umidade = "cardiopatia congênita umidade"
  )
  for (name in names(queries)) {
    res <- tryCatch(crossref_scielo(queries[[name]]), error = function(e) {
      list(database = "SciELO (via Crossref)", query = queries[[name]],
           error = conditionMessage(e),
           retrieved_at = format(Sys.time(), "%Y-%m-%dT%H:%M:%SZ", tz = "UTC"))
    })
    write_json(res, file.path(outdir, paste0(name, ".json")), auto_unbox = TRUE, pretty = TRUE)
    message(name, ": ", ifelse(is.null(res$n_retrieved), "ERROR", res$n_retrieved), " registros")
  }
}

if (sys.nframe() == 0) run_queries()
