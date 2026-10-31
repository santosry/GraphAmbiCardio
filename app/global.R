# ==========================================================================
# GraphAmbiCardio — dados, paletas e funções auxiliares
# global.R: dados, paletas e funções auxiliares
# ==========================================================================
suppressPackageStartupMessages({
  library(shiny)
  library(bslib)
  library(DT)
  library(visNetwork)
  library(plotly)
  library(dplyr)
  library(readr)
  library(jsonlite)
  library(stringr)
  library(scales)
  library(htmltools)
})

DATA_DIR <- "data"

read_data <- function(file) {
  path <- file.path(DATA_DIR, file)
  if (!file.exists(path)) {
    warning("Arquivo ausente: ", path)
    return(tibble())
  }
  readr::read_csv(path, show_col_types = FALSE, progress = FALSE)
}

nodes <- read_data("nodes.csv")
relations <- read_data("relations.csv")
evidence <- read_data("evidence.csv")
sinasc <- read_data("sinasc_annual.csv")
sinasc_tabnet <- read_data("sinasc_tabnet.csv")
sih <- read_data("sih_annual.csv")
sih_age <- read_data("sih_by_age.csv")
sih_flow <- read_data("sih_flow.csv")
sinasc_codes <- read_data("sinasc_chd_by_code.csv")
maternal <- read_data("sinasc_maternal_neonatal.csv")
climate_annual <- read_data("climate_annual.csv")
climate_monthly <- read_data("climate_monthly.csv")
pm25_annual <- read_data("pm25_annual.csv")
pm25_monthly <- read_data("pm25_monthly.csv")
pm25_meta <- tryCatch(jsonlite::fromJSON(file.path(DATA_DIR, "pm25_metadata.json")), error = function(e) list())
window_exposure <- read_data("window_exposure.csv")
models <- read_data("models.csv")
loo <- read_data("loo.csv")
paths <- read_data("paths.csv")
gaps <- read_data("gaps.csv")
phenotype_genes <- read_data("phenotype_genes.csv")
feasibility <- read_data("feasibility.csv")
hyp_candidates <- read_data("hypothesis_candidates.csv")
candidate_paths <- read_data("candidate_paths.csv")
centrality <- read_data("centrality.csv")
low_evidence <- read_data("low_evidence.csv")
enrichr_top <- read_data("enrichr_top30.csv")
reactome_top <- read_data("reactome_top.csv")
hierarchy <- read_data("hierarchy.csv")
meta <- tryCatch(jsonlite::fromJSON(file.path(DATA_DIR, "metadata.json")), error = function(e) list())
validation <- tryCatch(jsonlite::fromJSON(file.path(DATA_DIR, "validation.json")), error = function(e) list())

relations <- relations %>%
  mutate(
    confidence = as.numeric(confidence),
    grade = as.character(grade),
    evidence_tier = as.character(evidence_tier),
    evidence_tier_label = as.character(evidence_tier_label)
  )

nodes <- nodes %>% mutate(type = as.character(type), node_id = as.character(node_id))
evidence <- evidence %>% mutate(across(where(is.logical), as.character))

# --------------------------------------------------------------------------
# Paletas e rótulos
# --------------------------------------------------------------------------
TYPE_COLORS <- c(
  Exposure = "#D95F02", Mechanism = "#7570B3", Process = "#1B9E77",
  Phenotype = "#E7298A", Gene = "#8C8C8C", Pathway = "#66A61E",
  Variant = "#BDBDBD", Indicator = "#4D4D4D", Population = "#666666",
  Period = "#999999"
)
TYPE_LABELS <- c(
  Exposure = "Exposição", Mechanism = "Mecanismo", Process = "Processo",
  Phenotype = "Fenótipo", Gene = "Gene", Pathway = "Via", Variant = "Variante",
  Indicator = "Indicador", Population = "População", Period = "Período"
)
TIER_COLORS <- c(
  "Bem sustentada" = "#1B7837",
  "Plausível (experimental)" = "#E6A100",
  "Não demonstrada" = "#B2182B",
  "Contextual" = "#4A6FA5",
  "Inferida (regra)" = "#7F7F7F"
)
TIER_ORDER <- c("Bem sustentada", "Plausível (experimental)", "Não demonstrada", "Contextual", "Inferida (regra)")

tier_badge <- function(tier) {
  color <- TIER_COLORS[[tier]]
  if (is.null(color)) color <- "#777777"
  tags$span(class = "badge-tier", style = paste0("background:", color, ";"), tier)
}

ref_link <- function(ref, type = "PMID") {
  if (is.na(ref) || ref == "") return("")
  refs <- strsplit(as.character(ref), ";")[[1]]
  refs <- refs[refs != ""]
  links <- vapply(refs, function(r) {
    r <- trimws(r)
    if (grepl("^[0-9]+$", r)) {
      sprintf("<a href='https://pubmed.ncbi.nlm.nih.gov/%s/' target='_blank'>PMID %s</a>", r, r)
    } else if (grepl("^VCV", r)) {
      sprintf("<a href='https://www.ncbi.nlm.nih.gov/clinvar/variation/%s/' target='_blank'>%s</a>", r, r)
    } else if (grepl("^R-HSA", r)) {
      sprintf("<a href='https://reactome.org/content/detail/%s' target='_blank'>%s</a>", r, r)
    } else {
      r
    }
  }, character(1))
  paste(links, collapse = "; ")
}

node_label <- function(id) {
  lab <- nodes$label[match(id, nodes$node_id)]
  ifelse(is.na(lab), id, lab)
}

node_type <- function(id) {
  t <- nodes$type[match(id, nodes$node_id)]
  ifelse(is.na(t), "", t)
}

fmt_int <- function(x) formatC(as.integer(x), big.mark = ".", decimal.mark = ",", format = "d")
fmt_dec <- function(x, d = 1) formatC(as.numeric(x), big.mark = ".", decimal.mark = ",", format = "f", digits = d)

kpi_card <- function(title, value, subtitle = NULL, color = "#0B3C5D") {
  bslib::card(
    class = "kpi-card",
    style = paste0("border-top: 4px solid ", color, ";"),
    bslib::card_body(
      div(class = "kpi-title", title),
      div(class = "kpi-value", style = paste0("color:", color, ";"), value),
      if (!is.null(subtitle)) div(class = "kpi-sub", subtitle)
    )
  )
}

note_box <- function(..., type = "info") {
  args <- list(...)
  if (length(args) > 1 && is.character(args[[length(args)]]) &&
      args[[length(args)]] %in% c("info", "warning", "danger", "success")) {
    type <- args[[length(args)]]
    args <- args[-length(args)]
  }
  text <- paste0(unlist(args), collapse = "")
  cls <- switch(type, warning = "note-warning", danger = "note-danger", success = "note-success", "note-info")
  div(class = cls, HTML(text))
}

EDGE_LABELS <- c(
  EXPOSURE_ASSOCIATED_WITH_PHENOTYPE = "Exposição → fenótipo",
  EXPOSURE_MODULATES_MECHANISM = "Exposição → mecanismo",
  MECHANISM_INTERFERS_WITH_PROCESS = "Mecanismo → processo",
  MECHANISM_INTERFERES_WITH_PROCESS = "Mecanismo → processo",
  MECHANISM_MODULATES_MECHANISM = "Mecanismo → mecanismo",
  GENE_ASSOCIATED_WITH_PHENOTYPE = "Gene → fenótipo",
  GENE_PARTICIPATES_IN_PATHWAY = "Gene → via",
  PATHWAY_REGULATES_PROCESS = "Via → processo",
  VARIANT_IN_GENE = "Variante → gene",
  ALTERATION_ASSOCIATED_WITH_PHENOTYPE = "Processo/variante → fenótipo",
  INDICATOR_DESCRIBES_PHENOTYPE = "Indicador → fenótipo",
  ECOLOGICAL_CONTEXT_FOR = "Contexto ecológico",
  HYPOTHESIS_LINK = "Hipótese (composição)",
  HYPOTHESIS_CANDIDATE = "Hipótese (sobreposição gênica)"
)

edge_label <- function(x) {
  out <- EDGE_LABELS[x]
  ifelse(is.na(out), x, out)
}

# Módulos Shiny (modo ui.R/server.R/global.R)
for (.mod in list.files("modules", pattern = "[.]R$", full.names = TRUE)) source(.mod)
