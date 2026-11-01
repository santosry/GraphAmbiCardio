# ==========================================================================
# INMET — estação automática A607 (Campos dos Goytacazes/RJ)
# ==========================================================================
# Baixa temperatura, umidade, chuva e vento com o pacote BrazilMet e compara
# com a série ERA5-Land usada no estudo. Saídas:
#   data_processed/inmet_campos_daily.csv
#   data_processed/inmet_campos_metadata.json
#   reports/inmet_comparison.json
#   outputs/tables/inmet_era5_comparison.csv
# ==========================================================================
suppressPackageStartupMessages({
  library(BrazilMet)
  library(jsonlite)
  library(tools)
})

STATION <- "A607"
START <- "2010-01-01"
END <- "2025-12-31"

dir.create("data_processed", showWarnings = FALSE)
dir.create("reports", showWarnings = FALSE)
dir.create("outputs/tables", recursive = TRUE, showWarnings = FALSE)

cat("Baixando INMET", STATION, "de", START, "a", END, "...\n")
raw <- download_AWS_INMET_daily(STATION, START, END)
if (is.null(raw) || nrow(raw) == 0) stop("INMET não retornou dados para A607")

keep <- c(
  "station_code", "station", "uf", "date",
  "tair_mean_c", "tair_min_c", "tair_max_c",
  "rh_mean_porc", "rh_min_porc", "rh_max_porc",
  "rainfall_mm", "ws_2_m_s",
  "latitude_degrees", "longitude_degrees", "altitude_m"
)
missing <- setdiff(keep, names(raw))
if (length(missing) > 0) stop("Colunas ausentes no INMET: ", paste(missing, collapse = ", "))

d <- raw[, keep]
d$date <- as.Date(d$date)
d <- d[d$date >= as.Date(START) & d$date <= as.Date(END), ]
d <- d[!duplicated(d$date), ]
d <- d[order(d$date), ]
rownames(d) <- NULL

# Plausibility checks (fail loudly if the API changes units/signals).
stopifnot(all(is.na(d$tair_max_c) | (d$tair_max_c > -10 & d$tair_max_c < 55)))
stopifnot(all(is.na(d$rh_mean_porc) | (d$rh_mean_porc >= 0 & d$rh_mean_porc <= 100)))

write.csv(d, "data_processed/inmet_campos_daily.csv", row.names = FALSE, fileEncoding = "UTF-8")

meta <- list(
  source = "INMET — estação automática A607 (Campos dos Goytacazes/RJ), dados históricos",
  url = "https://portal.inmet.gov.br/uploads/dadoshistoricos/",
  package = "BrazilMet",
  package_version = as.character(packageVersion("BrazilMet")),
  station_code = STATION,
  station_name = unique(d$station)[1],
  latitude = unique(d$latitude_degrees)[1],
  longitude = unique(d$longitude_degrees)[1],
  altitude_m = unique(d$altitude_m)[1],
  period = c(as.character(min(d$date)), as.character(max(d$date))),
  n_days = nrow(d),
  missing_tmax = sum(is.na(d$tair_max_c)),
  missing_rh = sum(is.na(d$rh_mean_porc)),
  retrieved_at = format(Sys.time(), "%Y-%m-%dT%H:%M:%SZ", tz = "UTC"),
  checksum_md5 = as.character(md5sum("data_processed/inmet_campos_daily.csv")),
  note = "Série de estação automática; pode ter falhas de sensor. Usada para validação do ERA5-Land, não como exposição individual."
)
write_json(meta, "data_processed/inmet_campos_metadata.json", auto_unbox = TRUE, pretty = TRUE)

# Comparison with ERA5-Land (daily grid cell used in the study).
era5_path <- "data_processed/climate_daily_campos.csv"
if (file.exists(era5_path)) {
  e <- read.csv(era5_path)
  e$date <- as.Date(e$date)
  m <- merge(
    data.frame(date = d$date, inmet_tmax = d$tair_max_c, inmet_tmin = d$tair_min_c,
               inmet_tmean = d$tair_mean_c, inmet_rh = d$rh_mean_porc),
    data.frame(date = e$date, era5_tmax = e$temperature_2m_max,
               era5_tmin = e$temperature_2m_min, era5_tmean = e$temperature_2m_mean,
               era5_rh = e$relative_humidity_2m_mean),
    by = "date"
  )
  m <- m[complete.cases(m), ]
  cor_one <- function(a, b) {
    if (length(a) < 3) return(NA_real_)
    round(cor(a, b, use = "complete.obs"), 3)
  }
  rmse <- function(a, b) round(sqrt(mean((a - b)^2, na.rm = TRUE)), 2)
  comp <- data.frame(
    variable = c("Tmax", "Tmin", "Tmean", "RH"),
    n = nrow(m),
    pearson_r = c(cor_one(m$inmet_tmax, m$era5_tmax),
                  cor_one(m$inmet_tmin, m$era5_tmin),
                  cor_one(m$inmet_tmean, m$era5_tmean),
                  cor_one(m$inmet_rh, m$era5_rh)),
    mean_bias_inmet_minus_era5 = c(round(mean(m$inmet_tmax - m$era5_tmax), 2),
                                   round(mean(m$inmet_tmin - m$era5_tmin), 2),
                                   round(mean(m$inmet_tmean - m$era5_tmean), 2),
                                   round(mean(m$inmet_rh - m$era5_rh), 2)),
    rmse = c(rmse(m$inmet_tmax, m$era5_tmax),
             rmse(m$inmet_tmin, m$era5_tmin),
             rmse(m$inmet_tmean, m$era5_tmean),
             rmse(m$inmet_rh, m$era5_rh))
  )
  write.csv(comp, "outputs/tables/inmet_era5_comparison.csv", row.names = FALSE)
  write_json(list(station = STATION, station_name = meta$station_name,
                  latitude = meta$latitude, longitude = meta$longitude,
                  altitude_m = meta$altitude_m, period = meta$period,
                  n_days = nrow(m), package = meta$package,
                  package_version = meta$package_version,
                  comparison = comp,
                  note = "INMET A607 vs ERA5-Land; correlação e viés descritivos. Latitude, longitude e altitude identificam a estação, não a exposição individual."),
             "reports/inmet_comparison.json", auto_unbox = TRUE, pretty = TRUE, digits = 6)
}

cat("INMET:", nrow(d), "dias (", meta$period[1], "a", meta$period[2], ")\n")
