# Publica o GraphAmbiCardio no shinyapps.io.
#
# As credenciais NÃO ficam no repositório. O script lê um arquivo local
# (padrão: ~/.graphambicardio/rsconnect.env) com as variáveis:
#   RSCONNECT_NAME, RSCONNECT_TOKEN, RSCONNECT_SECRET
#
# Uso:
#   Rscript scripts/deploy/deploy_shinyapps.R
#
# Variáveis opcionais: GRAPHAMBICARDIO_CREDENTIALS, GRAPHAMBICARDIO_SHINYAPPS_ACCOUNT,
# GRAPHAMBICARDIO_APP_NAME.
suppressPackageStartupMessages(library(rsconnect))

cred_file <- Sys.getenv("GRAPHAMBICARDIO_CREDENTIALS", path.expand("~/.graphambicardio/rsconnect.env"))
if (file.exists(cred_file)) readRenviron(cred_file)

if (nzchar(Sys.getenv("RSCONNECT_TOKEN")) && nzchar(Sys.getenv("RSCONNECT_SECRET"))) {
  setAccountInfo(
    name = Sys.getenv("RSCONNECT_NAME", "ryansantospaulo"),
    token = Sys.getenv("RSCONNECT_TOKEN"),
    secret = Sys.getenv("RSCONNECT_SECRET")
  )
}

account <- Sys.getenv("GRAPHAMBICARDIO_SHINYAPPS_ACCOUNT", "ryansantospaulo")
app_name <- Sys.getenv("GRAPHAMBICARDIO_APP_NAME", "graphambicardio")

deployApp(
  appDir = "app",
  appName = app_name,
  account = account,
  server = "shinyapps.io",
  forceUpdate = TRUE,
  launch.browser = FALSE
)
