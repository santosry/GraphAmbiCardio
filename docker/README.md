# Docker

## Aplicativo Shiny

```bash
docker compose up --build
# abra http://localhost:3838
```

A imagem usa `rocker/r-ver:4.6.1` e um snapshot fixo do CRAN
(`2026-10-01`). O bundle de dados do app (`app/data/`) já está incluído;
não é necessário rodar o pipeline para abrir a interface.

### Observação

O Docker não estava instalado no ambiente em que o estudo foi executado;
o `Dockerfile` foi validado por inspeção e pelo fato de o app ser
autocontido, mas o build não pôde ser executado localmente. O comando
acima é o caminho reprodutível pretendido.

## Pipeline

O pipeline completo (Python + R + DATASUS + VIGIAR) é mais pesado e deve
ser executado no host, conforme o `README.md` e o `Makefile`. Para um
container de pipeline, use a imagem `python:3.12-slim` com R instalado e
monte `data_raw/` como volume; não foi incluído para evitar uma imagem
de vários GB sem necessidade para o app.
