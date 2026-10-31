# ==========================================================================
# PM2.5 para Campos dos Goytacazes via pacote vigiar (VIGIAR / Ministério da Saúde)
# ==========================================================================
# O vigiar acessa o dashboard público do VIGIAR (Power BI "Publish to Web").
# A API limita respostas a ~30.000 linhas e não expõe paginação; por isso
# filtramos server-side pelo código IBGE do município (330100) usando a
# cláusula Where da consulta DAX. O script depende dos internos do vigiar
# 0.7.2 e falha de forma explícita se o contrato mudar.
#
# Saídas:
#   data_processed/pm25_campos_anual.csv
#   data_processed/pm25_campos_mensal.csv
#   data_processed/pm25_vigiar_metadata.json
#   reports/pm25_quality.json
# ==========================================================================
suppressPackageStartupMessages({
  library(vigiar)
  library(jsonlite)
  library(tools)
})

MUNI <- "330100"
MUNI_LABEL <- "Campos dos Goytacazes"

`%||%` <- function(a, b) if (is.null(a) || length(a) == 0) b else a

vigiar_query_muni <- function(tabela, colunas, limite = 1000) {
  env <- vigiar:::.vigiar_env
  q <- vigiar:::.vigiar_construir_query(
    tabela, colunas = colunas,
    modelo_id = env$sessao$model_id, limite = limite
  )
  cmd <- q$queries[[1]]$Query$Commands[[1]]$SemanticQueryDataShapeCommand
  cmd$Query$Where <- list(list(Condition = list(In = list(
    Expressions = list(list(Column = list(
      Expression = list(SourceRef = list(Source = tabela)),
      Property = "muni"
    ))),
    Values = list(list(list(Literal = list(Value = sprintf("'%s'", MUNI)))))
  ))))
  q$queries[[1]]$Query$Commands[[1]]$SemanticQueryDataShapeCommand <- cmd
  resp <- vigiar:::.vigiar_executar_query(env$sessao, q, timeout = 180)
  vigiar:::.vigiar_parse_dados(resp, tabela)
}

main <- function() {
  dir.create("data_processed", showWarnings = FALSE)
  dir.create("reports", showWarnings = FALSE)

  vigiar_conectar(timeout = 180)
  on.exit(try(vigiar_desconectar(), silent = TRUE), add = TRUE)
  st <- vigiar_status()
  if (!isTRUE(st$tables_ok)) stop("Esquema do VIGIAR inconsistente; abortando.")

  annual <- vigiar_query_muni("df_anual", c("muni", "UF", "ano", "Media_pm25"))
  monthly <- vigiar_query_muni("df_mensal", c("muni", "UF", "ano", "mes", "pm25"))

  annual <- data.frame(
    cod_municipio = as.integer(annual$muni),
    uf = annual$UF,
    ano = as.integer(annual$ano),
    pm25_ug_m3 = round(as.numeric(annual$Media_pm25), 3),
    stringsAsFactors = FALSE
  )
  monthly <- data.frame(
    cod_municipio = as.integer(monthly$muni),
    uf = monthly$UF,
    ano = as.integer(monthly$ano),
    mes = as.integer(monthly$mes),
    pm25_ug_m3 = round(as.numeric(monthly$pm25), 3),
    stringsAsFactors = FALSE
  )

  stopifnot(all(annual$cod_municipio == as.integer(MUNI)))
  stopifnot(all(monthly$cod_municipio == as.integer(MUNI)))
  stopifnot(all(annual$pm25_ug_m3 >= 0 & annual$pm25_ug_m3 <= 500, na.rm = TRUE))
  stopifnot(all(monthly$pm25_ug_m3 >= 0 & monthly$pm25_ug_m3 <= 500, na.rm = TRUE))
  stopifnot(!anyDuplicated(annual[, c("ano")]))
  stopifnot(!anyDuplicated(monthly[, c("ano", "mes")]))

  annual <- annual[order(annual$ano), ]
  monthly <- monthly[order(monthly$ano, monthly$mes), ]

  write.csv(annual, "data_processed/pm25_campos_anual.csv", row.names = FALSE, fileEncoding = "UTF-8")
  write.csv(monthly, "data_processed/pm25_campos_mensal.csv", row.names = FALSE, fileEncoding = "UTF-8")

  quality <- list(
    source = "VIGIAR / Ministério da Saúde (dashboard público, Power BI)",
    package = "vigiar",
    package_version = as.character(packageVersion("vigiar")),
    filter = sprintf("muni == '%s' (%s)", MUNI, MUNI_LABEL),
    retrieved_at = format(Sys.time(), "%Y-%m-%dT%H:%M:%SZ", tz = "UTC"),
    annual = list(
      n = nrow(annual),
      years = range(annual$ano),
      min = min(annual$pm25_ug_m3), max = max(annual$pm25_ug_m3),
      mean = round(mean(annual$pm25_ug_m3), 3),
      missing_years = setdiff(2010:2025, annual$ano)
    ),
    monthly = list(
      n = nrow(monthly),
      years = range(monthly$ano),
      months = sort(unique(monthly$mes)),
      min = min(monthly$pm25_ug_m3), max = max(monthly$pm25_ug_m3),
      mean = round(mean(monthly$pm25_ug_m3), 3)
    ),
    checksums = list(
      annual_md5 = as.character(md5sum("data_processed/pm25_campos_anual.csv")),
      monthly_md5 = as.character(md5sum("data_processed/pm25_campos_mensal.csv"))
    ),
    note = "PM2.5 anual/mensal por município; não é monitoramento de estação local. Série de área."
  )
  write_json(quality, "data_processed/pm25_vigiar_metadata.json", auto_unbox = TRUE, pretty = TRUE)
  write_json(quality, "reports/pm25_quality.json", auto_unbox = TRUE, pretty = TRUE)
  cat("PM2.5:", nrow(annual), "anos e", nrow(monthly), "meses para", MUNI_LABEL, "\n")
}

if (sys.nframe() == 0) main()
