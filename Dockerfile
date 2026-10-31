# GraphAmbiCardio — Shiny application image
# Pin R version and CRAN snapshot for reproducibility.
FROM rocker/r-ver:4.6.1

ENV DEBIAN_FRONTEND=noninteractive \
    RENV_CONFIG_REPOS_OVERRIDE=https://packagemanager.posit.co/cran/2026-10-01

RUN apt-get update && apt-get install -y --no-install-recommends \
    libcurl4-openssl-dev libssl-dev libxml2-dev libglpk-dev \
    libpng-dev libfontconfig1-dev libharfbuzz-dev libfribidi-dev \
    libfreetype6-dev libgit2-dev pandoc \
    && rm -rf /var/lib/apt/lists/*

RUN R -q -e "install.packages(c('shiny','bslib','DT','visNetwork','plotly','dplyr','readr','jsonlite','stringr','scales','htmltools','igraph','commonmark','viridisLite'), repos='https://packagemanager.posit.co/cran/2026-10-01', Ncpus=4)"

COPY app /srv/graphambicardio
WORKDIR /srv/graphambicardio

EXPOSE 3838
CMD ["R", "-e", "shiny::runApp('/srv/graphambicardio', host = '0.0.0.0', port = 3838)"]
