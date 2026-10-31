mod_epi_ui <- function(id) {
  ns <- NS(id)
  tagList(
    note_box("<b>Leia antes de interpretar.</b> Os dados locais são apresentados como contexto ecológico. ",
             "SINASC não é incidência (há subnotificação importante); SIH não representa indivíduos únicos; ",
             "a exposição climática é de área (ERA5-Land), não individual. O período é 2010–2025.", "warning"),
    layout_columns(
      col_widths = c(4,4,4),
      kpi_card("Nascidos vivos (SINASC)", textOutput(ns("kpi_births")), "2010–2025", "#0B3C5D"),
      kpi_card("Casos de cardiopatia", textOutput(ns("kpi_cases")), "definição do estudo", "#E7298A"),
      kpi_card("Internações (SIH)", textOutput(ns("kpi_sih")), "diagnóstico principal Q20–Q28", "#1D7874")
    ),
    br(),
    layout_columns(
      col_widths = c(7,5),
      card(card_header("SINASC — casos e taxa por 10.000 nascidos vivos"),
           card_body(plotlyOutput(ns("sinasc_plot"), height = "360px"))),
      card(card_header("SIH/SUS — internações e óbitos"),
           card_body(plotlyOutput(ns("sih_plot"), height = "360px")))
    ),
    layout_columns(
      col_widths = c(6,6),
      card(card_header("Clima — temperatura máxima mensal (ERA5-Land)"),
           card_body(plotlyOutput(ns("climate_plot"), height = "340px"))),
      card(card_header("Dias de calor e ondas de calor por ano"),
           card_body(plotlyOutput(ns("heat_plot"), height = "340px")))
    ),
    br(),
    card(
      card_header("PM2,5 — série municipal do VIGIAR (Ministério da Saúde)"),
      card_body(
        plotlyOutput(ns("pm25_plot"), height = "340px"),
        htmlOutput(ns("pm25_note"))
      )
    ),
    br(),
    layout_columns(
      col_widths = c(6,6),
      card(card_header("Cobertura e status dos dados SINASC"),
           card_body(DTOutput(ns("coverage")))),
      card(card_header("Perfil materno-neonatal"),
           card_body(DTOutput(ns("maternal"))))
    ),
    br(),
    card(card_header("Modelos exploratórios de exposição no período de organogênese"),
         card_body(
           DTOutput(ns("models")),
           note_box("<b>Não é um achado causal.</b> Há 56–59 eventos, exposição de área, ",
                    "idade gestacional estimada e modelos que discordam entre si (logístico vs. contagem mensal). ",
                    "Ver <i>docs/07_EPI_ENV_METHODS.md</i> e a análise de sensibilidade.", "danger")
         )),
    br(),
    card(card_header("Distribuição dos códigos CID-10 registrados"),
         card_body(DTOutput(ns("codes"))))
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
               legend = list(orientation = "h"), margin = list(l = 50, r = 50, t = 10, b = 40),
               xaxis = list(title = "Ano", dtick = 1))
    })

    output$sih_plot <- renderPlotly({
      plot_ly(sih, x = ~year) %>%
        add_bars(y = ~admissions_primary_chd, name = "Internações", marker = list(color = "#1D7874")) %>%
        add_trace(y = ~deaths, name = "Óbitos", type = "scatter", mode = "lines+markers",
                  line = list(color = "#B2182B")) %>%
        layout(yaxis = list(title = "Registros"), xaxis = list(title = "Ano", dtick = 1),
               legend = list(orientation = "h"), margin = list(l = 50, r = 20, t = 10, b = 40))
    })

    output$climate_plot <- renderPlotly({
      d <- climate_monthly
      plot_ly(d, x = ~period, y = ~tmax_mean, type = "scatter", mode = "lines",
              line = list(color = "#D95F02", width = 1.4), name = "Tmax média mensal") %>%
        layout(xaxis = list(title = "", tickangle = -45, nticks = 12),
               yaxis = list(title = "°C"), margin = list(l = 50, r = 20, t = 10, b = 60))
    })

    output$heat_plot <- renderPlotly({
      plot_ly(climate_annual, x = ~year) %>%
        add_bars(y = ~heat_days_35, name = "Dias ≥ 35 °C", marker = list(color = "#E6A100")) %>%
        add_trace(y = ~heatwave_days, name = "Dias em onda de calor", type = "scatter", mode = "lines+markers",
                  line = list(color = "#B2182B")) %>%
        layout(yaxis = list(title = "Dias"), xaxis = list(title = "Ano", dtick = 1),
               legend = list(orientation = "h"), margin = list(l = 50, r = 20, t = 10, b = 40))
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
        layout(xaxis = list(title = ""), yaxis = list(title = "µg/m³"),
               legend = list(orientation = "h"), margin = list(l = 50, r = 20, t = 10, b = 40))
    })

    output$pm25_note <- renderUI({
      if (length(pm25_meta) == 0) return(div(class = "small-muted", "Metadados de PM2,5 não encontrados."))
      HTML(sprintf(
        "<span class='small-muted'>Fonte: %s (pacote vigiar %s), filtro municipal 330100, extração %s. Série de área; não é estação local nem exposição individual.</span>",
        pm25_meta$source, pm25_meta$package_version, pm25_meta$retrieved_at
      ))
    })

    output$coverage <- renderDT({
      datatable(sinasc %>% select(Ano = year, Nascidos = live_births, Casos = chd_cases,
                                  `Por 10.000` = chd_per_10000_lb, Status = data_status, Fonte = source),
                rownames = FALSE, options = list(pageLength = 8, dom = "tp", scrollX = TRUE))
    }, server = FALSE)

    output$maternal <- renderDT({
      datatable(maternal, rownames = FALSE, options = list(dom = "t", scrollX = TRUE))
    }, server = FALSE)

    output$models <- renderDT({
      d <- models[models$model != "leave_one_year_out", , drop = FALSE]
      est <- if ("or_per_sd" %in% names(d)) d$or_per_sd else rep(NA_real_, nrow(d))
      if ("rr_per_sd" %in% names(d)) est <- ifelse(is.na(est), d$rr_per_sd, est)
      ic <- if ("or_per_sd_ci95" %in% names(d)) d$or_per_sd_ci95 else rep("", nrow(d))
      if ("rr_per_sd_ci95" %in% names(d)) ic <- ifelse(is.na(ic) | ic == "", d$rr_per_sd_ci95, ic)
      out <- data.frame(Modelo = d$model, Exposição = d$exposure, n = d$n, Eventos = d$n_events,
                        OR_RR = est, IC95 = ic, p = d$p_value, check.names = FALSE)
      datatable(out, rownames = FALSE, options = list(dom = "t", scrollX = TRUE))
    }, server = FALSE)

    output$codes <- renderDT({
      d <- sinasc_codes %>% arrange(desc(n)) %>% head(20)
      datatable(d, rownames = FALSE, options = list(pageLength = 8, dom = "tp"))
    }, server = FALSE)
  })
}
