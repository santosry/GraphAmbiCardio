mod_epi_ui <- function(id) {
  ns <- NS(id)
  tagList(
    note_box("<b>Leia antes de interpretar.</b> Os dados locais são apresentados como contexto ecológico. ",
             "SINASC não é incidência (há subnotificação importante); SIH não representa indivíduos únicos; ",
             "a exposição climática é de área (ERA5-Land), não individual. O período é 2010–2025.", "warning"),
    layout_columns(
      col_widths = c(4,4,4),
      kpi_card("Nascidos vivos (SINASC)", textOutput(ns("kpi_births")), "2010–2025", "#0B3C5D", source = "Fonte: SINASC/DATASUS (microdados 2010–2022 e 2025; TabNet 2023–2024)."),
      kpi_card("Casos de cardiopatia", textOutput(ns("kpi_cases")), "definição do estudo", "#E7298A", source = "Fonte: SINASC/DATASUS; CID-10 Q20–Q28."),
      kpi_card("Internações (SIH)", textOutput(ns("kpi_sih")), "diagnóstico principal Q20–Q28", "#1D7874", source = "Fonte: SIH/SUS; AIH com diagnóstico principal Q20–Q28.")
    ),
    br(),
    layout_columns(
      col_widths = c(7,5),
      div(class = "figure-block",
          h5("SINASC — casos e taxa por 10.000 nascidos vivos"),
          div(class = "figure-canvas html-fill-container chart-canvas", plotlyOutput(ns("sinasc_plot"), height = "100%")),
          source_note("Fonte: SINASC/DATASUS. Casos = CID-10 Q20–Q28; 2023–2024 via TabNet; ver docs/07 e docs/09.")),
      div(class = "figure-block",
          h5("SIH/SUS — internações e óbitos"),
          div(class = "figure-canvas html-fill-container chart-canvas", plotlyOutput(ns("sih_plot"), height = "100%")),
          source_note("Fonte: SIH/SUS. AIH não são pessoas; ver docs/07 e docs/09."))
    ),
    layout_columns(
      col_widths = c(6,6),
      div(class = "figure-block",
          h5("Clima — temperatura máxima mensal (ERA5-Land)"),
          div(class = "figure-canvas html-fill-container chart-canvas", plotlyOutput(ns("climate_plot"), height = "100%")),
          source_note("Fonte: ERA5-Land via Open-Meteo, célula −21,757/−41,354; ver docs/03.")),
      div(class = "figure-block",
          h5("Dias de calor e ondas de calor por ano"),
          div(class = "figure-canvas html-fill-container chart-canvas", plotlyOutput(ns("heat_plot"), height = "100%")),
          source_note("Fonte: ERA5-Land via Open-Meteo; limiar P90 34,2 °C; ver docs/07."))
    ),
    br(),
    div(
      class = "figure-block",
      h5("PM2,5 — série municipal do VIGIAR (Ministério da Saúde)"),
      div(class = "figure-canvas html-fill-container chart-canvas-wide", plotlyOutput(ns("pm25_plot"), height = "100%")),
      htmlOutput(ns("pm25_note"))
    ),
    br(),
    div(
      class = "figure-block",
      h5("Validação da exposição climática — INMET A607 vs ERA5-Land"),
      div(class = "figure-canvas html-fill-container chart-canvas-wide",
          plotlyOutput(ns("inmet_plot"), height = "100%")),
      h6("Estação e coordenadas", style = "margin-top:1rem;"),
      DTOutput(ns("inmet_station")),
      h6("Comparação diária com ERA5-Land", style = "margin-top:1rem;"),
      DTOutput(ns("inmet_table")),
      uiOutput(ns("inmet_note"))
    ),
    br(),
    layout_columns(
      col_widths = c(6,6),
      card(card_header("Cobertura e status dos dados SINASC"),
           card_body(DTOutput(ns("coverage")))),
      card(card_header("Perfil materno-neonatal"),
           card_body(DTOutput(ns("maternal")),
                     source_note("Fonte: SINASC/DATASUS; 98.598 nascimentos; ver docs/05.")))
    ),
    br(),
    card(card_header("Modelos exploratórios de exposição no período de organogênese"),
         card_body(
           DTOutput(ns("models")),
           h6("Ajuste mútuo PM2,5 + temperatura", style = "margin-top:1rem;"),
           DTOutput(ns("models_two")),
           source_note("Fonte: outputs/tables/exploratory_models.csv; p e q (BH-FDR); ver docs/07."),
           note_box("<b>Não é um achado causal; todos os p-valores são ajustados por FDR (BH).</b> Há 56–59 eventos, exposição de área, ",
                    "idade gestacional estimada e modelos que discordam entre si (logístico vs. contagem mensal). ",
                    "Ver <i>docs/07_EPI_ENV_METHODS.md</i> e a análise de sensibilidade.", "danger")
         )),
    br(),
    card(card_header("Distribuição dos códigos CID-10 registrados"),
         card_body(DTOutput(ns("codes")),
                   source_note("Fonte: SINASC/DATASUS; CODANOMAL (Q20–Q28).")))
  )
}

mod_epi_server <- function(id) {
  moduleServer(id, function(input, output, session) {
    output$kpi_births <- renderText(fmt_int(sum(sinasc$live_births, na.rm = TRUE)))
    output$kpi_cases <- renderText(fmt_int(sum(sinasc$chd_cases, na.rm = TRUE)))
    output$kpi_sih <- renderText(fmt_int(sum(sih$admissions_primary_chd, na.rm = TRUE)))

    output$sinasc_plot <- renderPlotly({
      d <- sinasc %>% mutate(
        fonte = ifelse(grepl("TabNet", source), "TabNet (agregado)", "Microdados"),
        status = ifelse(grepl("preliminary|preliminar", data_status), "preliminar", "consolidado"),
        ano = as.integer(year)
      )
      plot_ly(d, x = ~ano) %>%
        add_bars(y = ~chd_cases, name = "Casos", color = ~fonte,
                 colors = c("Microdados" = "#E7298A", "TabNet (agregado)" = "#F4A6C8"),
                 hovertemplate = "Ano %{x}<br>Casos: %{y}<extra></extra>") %>%
        add_trace(y = ~chd_per_10000_lb, name = "Por 10.000 NV", yaxis = "y2",
                  type = "scatter", mode = "lines+markers", line = list(color = "#0B3C5D"),
                  hovertemplate = "Ano %{x}<br>Taxa: %{y:.2f}/10.000<extra></extra>") %>%
        layout(yaxis = list(title = "Casos"), yaxis2 = list(title = "Por 10.000 NV", overlaying = "y", side = "right"),
               legend = list(orientation = "h", y = -0.28), margin = list(l = 60, r = 60, t = 20, b = 70),
               hovermode = "x unified", font = list(size = 12),
               xaxis = list(title = "Ano", dtick = 1, tickangle = -45)) %>%
        plotly::config(displaylogo = FALSE, responsive = TRUE)
    })

    output$sih_plot <- renderPlotly({
      plot_ly(sih, x = ~year) %>%
        add_bars(y = ~admissions_primary_chd, name = "Internações", marker = list(color = "#1D7874")) %>%
        add_trace(y = ~deaths, name = "Óbitos", type = "scatter", mode = "lines+markers",
                  line = list(color = "#B2182B")) %>%
        layout(yaxis = list(title = "Registros"), xaxis = list(title = "Ano", dtick = 1, tickangle = -45),
               legend = list(orientation = "h", y = -0.28), margin = list(l = 60, r = 30, t = 20, b = 70),
               hovermode = "x unified", font = list(size = 12)) %>%
        plotly::config(displaylogo = FALSE, responsive = TRUE)
    })

    output$climate_plot <- renderPlotly({
      d <- climate_monthly
      plot_ly(d, x = ~period, y = ~tmax_mean, type = "scatter", mode = "lines",
              line = list(color = "#D95F02", width = 1.4), name = "Tmax média mensal") %>%
        layout(xaxis = list(title = "", tickangle = -45, nticks = 12),
               yaxis = list(title = "°C"), margin = list(l = 60, r = 30, t = 20, b = 80),
               hovermode = "x unified", font = list(size = 12)) %>%
        plotly::config(displaylogo = FALSE, responsive = TRUE)
    })

    output$heat_plot <- renderPlotly({
      plot_ly(climate_annual, x = ~year) %>%
        add_bars(y = ~heat_days_35, name = "Dias ≥ 35 °C", marker = list(color = "#E6A100")) %>%
        add_trace(y = ~heatwave_days, name = "Dias em onda de calor", type = "scatter", mode = "lines+markers",
                  line = list(color = "#B2182B")) %>%
        layout(yaxis = list(title = "Dias"), xaxis = list(title = "Ano", dtick = 1, tickangle = -45),
               legend = list(orientation = "h", y = -0.28), margin = list(l = 60, r = 30, t = 20, b = 70),
               hovermode = "x unified", font = list(size = 12)) %>%
        plotly::config(displaylogo = FALSE, responsive = TRUE)
    })

    output$pm25_plot <- renderPlotly({
      m <- pm25_monthly %>%
        mutate(periodo = as.Date(sprintf("%d-%02d-01", ano, mes)))
      a <- pm25_annual
      plot_ly() %>%
        add_trace(data = m, x = ~periodo, y = ~pm25_ug_m3, type = "scatter", mode = "lines",
                  name = "Mensal", line = list(color = "#9ECAE1", width = 1), opacity = 0.8) %>%
        add_trace(data = a, x = ~as.Date(sprintf("%d-01-01", ano)), y = ~pm25_ug_m3,
                  type = "scatter", mode = "lines+markers", name = "Anual",
                  line = list(color = "#08519C", width = 2.5)) %>%
        layout(xaxis = list(title = "", tickangle = -45),
               yaxis = list(title = "µg/m³"),
               legend = list(orientation = "h", y = -0.28), margin = list(l = 60, r = 30, t = 20, b = 70),
               hovermode = "x unified", font = list(size = 12)) %>%
        plotly::config(displaylogo = FALSE, responsive = TRUE)
    })

    output$pm25_note <- renderUI({
      if (length(pm25_meta) == 0) return(div(class = "small-muted", "Metadados de PM2,5 não encontrados."))
      HTML(sprintf(
        "<span class='small-muted'>Fonte: %s (pacote vigiar %s), filtro municipal 330100, extração %s. Série de área; não é estação local nem exposição individual.</span>",
        pm25_meta$source, pm25_meta$package_version, pm25_meta$retrieved_at
      ))
    })

    output$inmet_plot <- renderPlotly({
      d <- inmet_daily %>%
        transmute(date = as.Date(date), inmet_tmax = tair_max_c, inmet_rh = rh_mean_porc)
      e <- climate_daily %>%
        transmute(date = as.Date(date), era5_tmax = temperature_2m_max,
                  era5_rh = relative_humidity_2m_mean)
      m <- inner_join(d, e, by = "date") %>% filter(!is.na(era5_tmax), !is.na(inmet_tmax), !is.na(era5_rh), !is.na(inmet_rh))
      if (nrow(m) == 0) return(plotly_empty(type = "scatter", mode = "markers") %>% layout(title = "Sem dados INMET/ERA5 para comparar"))
      p1 <- plot_ly(m, x = ~era5_tmax, y = ~inmet_tmax, type = "scatter", mode = "markers",
                    marker = list(size = 3, color = "#440154", opacity = .35),
                    hovertemplate = "ERA5 %{x:.1f} °C<br>INMET %{y:.1f} °C<extra></extra>") %>%
        layout(xaxis = list(title = "ERA5-Land Tmax (°C)"), yaxis = list(title = "INMET Tmax (°C)"))
      p1 <- p1 %>% add_trace(x = range(m$era5_tmax), y = range(m$era5_tmax), type = "scatter",
                             mode = "lines", line = list(dash = "dash", color = "#999"), showlegend = FALSE)
      p2 <- plot_ly(m, x = ~era5_rh, y = ~inmet_rh, type = "scatter", mode = "markers",
                    marker = list(size = 3, color = "#31688E", opacity = .35),
                    hovertemplate = "ERA5 %{x:.0f} %<br>INMET %{y:.0f} %<extra></extra>") %>%
        layout(xaxis = list(title = "ERA5-Land UR (%)"), yaxis = list(title = "INMET UR (%)"))
      p2 <- p2 %>% add_trace(x = range(m$era5_rh), y = range(m$era5_rh), type = "scatter",
                             mode = "lines", line = list(dash = "dash", color = "#999"), showlegend = FALSE)
      subplot(p1, p2, nrows = 1, titleX = TRUE, titleY = TRUE, margin = 0.08) %>%
        layout(showlegend = FALSE, margin = list(l = 55, r = 25, t = 20, b = 55),
               font = list(size = 12)) %>%
        plotly::config(displaylogo = FALSE, responsive = TRUE)
    })

    output$inmet_station <- renderDT({
      if (length(inmet_meta) == 0) {
        return(datatable(data.frame(Mensagem = "Metadados da estação não disponíveis."),
                         rownames = FALSE, options = list(dom = "t")))
      }
      d <- data.frame(
        Estação = inmet_meta$station_code,
        Nome = inmet_meta$station_name,
        Latitude = as.numeric(inmet_meta$latitude),
        Longitude = as.numeric(inmet_meta$longitude),
        `Altitude (m)` = as.numeric(inmet_meta$altitude_m),
        Início = as.character(inmet_meta$period[1]),
        Fim = as.character(inmet_meta$period[2]),
        Dias = as.integer(inmet_meta$n_days),
        Pacote = paste(inmet_meta$package, inmet_meta$package_version),
        check.names = FALSE
      )
      datatable(d, rownames = FALSE, options = list(dom = "t", autoWidth = TRUE)) %>%
        formatRound(columns = c("Latitude", "Longitude", "Altitude (m)"), digits = 4)
    }, server = FALSE)

    output$inmet_table <- renderDT({
      d <- inmet_comparison
      if (nrow(d) == 0) return(datatable(data.frame(Mensagem = "Comparação INMET/ERA5 não disponível."), rownames = FALSE, options = list(dom = "t")))
      out <- d %>% transmute(Variável = variable, n, `r de Pearson` = pearson_r,
                             `Viés médio (INMET − ERA5)` = mean_bias_inmet_minus_era5,
                             `RMSE` = rmse)
      datatable(out, rownames = FALSE, options = list(dom = "t", autoWidth = TRUE)) %>%
        formatSignif(columns = c("r de Pearson", "Viés médio (INMET − ERA5)", "RMSE"), digits = 3)
    }, server = FALSE)

    output$inmet_note <- renderUI({
      if (length(inmet_meta) == 0) return(source_note("Fonte: INMET A607 via BrazilMet; ERA5-Land via Open-Meteo."))
      source_note(sprintf(
        "Fonte: INMET estação %s (%s), lat %s, lon %s, altitude %s m; %s a %s, %s dias; pacote BrazilMet %s. ERA5-Land via Open-Meteo (célula −21,757/−41,354, 12 m). Série de estação vs reanálise; não é exposição individual. Ver docs/07.",
        inmet_meta$station_code, inmet_meta$station_name,
        format(as.numeric(inmet_meta$latitude), nsmall = 4, decimal.mark = ","),
        format(as.numeric(inmet_meta$longitude), nsmall = 4, decimal.mark = ","),
        format(as.numeric(inmet_meta$altitude_m), trim = TRUE, decimal.mark = ","),
        inmet_meta$period[[1]], inmet_meta$period[[2]],
        fmt_int(inmet_meta$n_days), inmet_meta$package_version
      ))
    })

    output$coverage <- renderDT({
      datatable(sinasc %>% select(Ano = year, Nascidos = live_births, Casos = chd_cases,
                                  `Por 10.000` = chd_per_10000_lb, Status = data_status, Fonte = source),
                rownames = FALSE, options = list(pageLength = 8, dom = "tp"))
    }, server = FALSE)

    output$maternal <- renderDT({
      datatable(maternal, rownames = FALSE, options = list(dom = "t"))
    }, server = FALSE)

    output$models <- renderDT({
      d <- models[models$model != "leave_one_year_out", , drop = FALSE]
      est <- if ("or_per_sd" %in% names(d)) d$or_per_sd else rep(NA_real_, nrow(d))
      if ("rr_per_sd" %in% names(d)) est <- ifelse(is.na(est), d$rr_per_sd, est)
      ic <- if ("or_per_sd_ci95" %in% names(d)) d$or_per_sd_ci95 else rep("", nrow(d))
      if ("rr_per_sd_ci95" %in% names(d)) ic <- ifelse(is.na(ic) | ic == "", d$rr_per_sd_ci95, ic)
      out <- data.frame(Modelo = d$model, Exposição = d$exposure, n = d$n, Eventos = d$n_events,
                        OR_RR = est, IC95 = ic, p = d$p_value, q_FDR = d$q_value, check.names = FALSE)
      datatable(out, rownames = FALSE, options = list(dom = "t", autoWidth = TRUE)) %>%
        formatSignif(columns = c("p", "q_FDR"), digits = 3)
    }, server = FALSE)

    output$models_two <- renderDT({
      d <- models[models$model == "logistic_two_exposures", , drop = FALSE]
      if (nrow(d) == 0) return(datatable(data.frame(Mensagem = "Sem modelo de ajuste mútuo."), rownames = FALSE, options = list(dom = "t")))
      out <- data.frame(
        Exposição = c(d$exposure_1, d$exposure_2),
        OR_por_SD = c(d$exposure_1_or_per_sd, d$exposure_2_or_per_sd),
        IC95 = c(d$exposure_1_ci95, d$exposure_2_ci95),
        p = c(d$exposure_1_p, d$exposure_2_p),
        q_FDR = c(d$exposure_1_q, d$exposure_2_q),
        check.names = FALSE
      )
      datatable(out, rownames = FALSE, options = list(dom = "t", autoWidth = TRUE)) %>%
        formatSignif(columns = c("p", "q_FDR"), digits = 3)
    }, server = FALSE)

    output$codes <- renderDT({
      d <- sinasc_codes %>% arrange(desc(n)) %>% head(20)
      datatable(d, rownames = FALSE, options = list(pageLength = 8, dom = "tp"))
    }, server = FALSE)
  })
}
