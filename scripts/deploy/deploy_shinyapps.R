# Publica o CEKP no shinyapps.io.
# Pré-requisitos: conta configurada em rsconnect (rsconnect::setAccountInfo)
# e o pacote rsconnect instalado.
#
# Uso:
#   Rscript scripts/deploy/deploy_shinyapps.R
#
# O nome da conta/servidor pode ser ajustado por variáveis de ambiente.
suppressPackageStartupMessages(library(rsconnect))

account <- Sys.getenv("CEKP_SHINYAPPS_ACCOUNT", "arbovirosescamposiff")
server <- Sys.getenv("CEKP_SHINYAPPS_SERVER", "shinyapps.io")
app_name <- Sys.getenv("CEKP_APP_NAME", "cekp")

deployApp(
  appDir = "app",
  appName = app_name,
  account = account,
  server = server,
  forceUpdate = TRUE,
  launch.browser = FALSE
)
