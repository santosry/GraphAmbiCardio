"""Prepare the self-contained data bundle used by the Shiny app (GraphAmbiCardio)."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "app" / "data"
APP.mkdir(parents=True, exist_ok=True)

COPY = {
    "outputs/graph/nodes.csv": "nodes.csv",
    "outputs/graph/relations.csv": "relations.csv",
    "outputs/graph/evidence.csv": "evidence.csv",
    "outputs/graph/hypotheses.csv": "hypotheses.csv",
    "outputs/tables/sinasc_annual_complete.csv": "sinasc_annual.csv",
    "data_processed/sinasc_tabnet_aggregates.csv": "sinasc_tabnet.csv",
    "outputs/tables/sih_annual.csv": "sih_annual.csv",
    "outputs/tables/sih_by_age_group.csv": "sih_by_age.csv",
    "outputs/tables/sih_admission_municipality_flow.csv": "sih_flow.csv",
    "outputs/tables/sinasc_chd_by_code.csv": "sinasc_chd_by_code.csv",
    "outputs/tables/sinasc_maternal_neonatal.csv": "sinasc_maternal_neonatal.csv",
    "outputs/tables/climate_annual_campos.csv": "climate_annual.csv",
    "data_processed/climate_monthly_campos.csv": "climate_monthly.csv",
    "data_processed/pm25_campos_anual.csv": "pm25_annual.csv",
    "data_processed/pm25_campos_mensal.csv": "pm25_monthly.csv",
    "data_processed/pm25_vigiar_metadata.json": "pm25_metadata.json",
    "outputs/tables/gestational_window_exposure_summary.csv": "window_exposure.csv",
    "outputs/tables/exploratory_models.csv": "models.csv",
    "outputs/tables/sensitivity_leave_one_year_out.csv": "loo.csv",
    "outputs/tables/paths_exposure_phenotype.csv": "paths.csv",
    "outputs/tables/gap_analysis.csv": "gaps.csv",
    "outputs/tables/phenotype_gene_convergence.csv": "phenotype_genes.csv",
    "reports/feasibility_pair_matrix.csv": "feasibility.csv",
    "outputs/tables/hypothesis_candidates.csv": "hypothesis_candidates.csv",
    "outputs/tables/candidate_paths_missing_link.csv": "candidate_paths.csv",
    "outputs/tables/network_centrality.csv": "centrality.csv",
    "outputs/tables/low_evidence_edges.csv": "low_evidence.csv",
    "outputs/tables/enrichr_top30.csv": "enrichr_top30.csv",
    "outputs/tables/reactome_top_pathways.csv": "reactome_top.csv",
    "reports/validation_results.json": "validation.json",
}
for src, dst in COPY.items():
    p = ROOT / src
    if p.exists():
        shutil.copy2(p, APP / dst)
    else:
        print("missing:", src)

# FAIR metadata and AI declaration for the app
for src, dst in {
    "fair/datapackage.json": "app/www/datapackage.json",
    "fair/metadata.json": "app/www/metadata.json",
    "docs/13_DECLARACAO_IA.md": "app/data/ai_declaration.md",
}.items():
    p = ROOT / src
    if p.exists():
        (ROOT / dst).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, ROOT / dst)

# exposure hierarchy defined by the scientific review
hierarchy = [
    {"ordem": 1, "exposicao_id": "EXP:PM25", "exposicao": "PM2,5", "papel": "Eixo principal",
     "evidencia_epidemiologica": "Moderada; associações descritas para cardiopatias congênitas",
     "evidencia_molecular": "Relativamente consistente em modelos experimentais (AHR, ROS, mitocôndria, Wnt)",
     "decisao": "Incluído como eixo principal; hipóteses moleculares explicitadas"},
    {"ordem": 2, "exposicao_id": "EXP:HEAT", "exposicao": "Temperatura elevada", "papel": "Eixo secundário",
     "evidencia_epidemiologica": "Crescente, inclusive no Brasil (OR 1,08 para defeitos circulatórios)",
     "evidencia_molecular": "Mecanismos específicos ainda insuficientemente estabelecidos (neural crest/TRPV)",
     "decisao": "Incluído como eixo secundário; cadeia mecanística marcada como parcial"},
    {"ordem": 3, "exposicao_id": "EXP:PM10", "exposicao": "PM10", "papel": "Condicional",
     "evidencia_epidemiologica": "Associações com alguns fenótipos, heterogêneas",
     "evidencia_molecular": "Mecanismos menos específicos",
     "decisao": "Incluído com evidência limitada"},
    {"ordem": 4, "exposicao_id": "EXP:NO2", "exposicao": "NO₂", "papel": "Condicional",
     "evidencia_epidemiologica": "Associações para determinados fenótipos",
     "evidencia_molecular": "Evidência mecanística limitada",
     "decisao": "Incluído com evidência limitada"},
    {"ordem": 5, "exposicao_id": "EXP:CO", "exposicao": "CO", "papel": "Condicional",
     "evidencia_epidemiologica": "Sinais de associação com alguns defeitos cardíacos",
     "evidencia_molecular": "Hipóxia e alterações do desenvolvimento são plausíveis",
     "decisao": "Incluído; mecanismo não demonstrado"},
    {"ordem": 6, "exposicao_id": "EXP:O3", "exposicao": "O₃", "papel": "Condicional",
     "evidencia_epidemiologica": "Sinais epidemiológicos em janelas gestacionais específicas",
     "evidencia_molecular": "Evidência mecanística limitada",
     "decisao": "Incluído com evidência limitada"},
    {"ordem": 7, "exposicao_id": "EXP:HUMIDITY", "exposicao": "Umidade relativa", "papel": "Contextual",
     "evidencia_epidemiologica": "Evidência direta muito limitada",
     "evidencia_molecular": "Sem conexão molecular estabelecida",
     "decisao": "Mantida como variável contextual/confundidora; sem aresta causal"},
]
pd.DataFrame(hierarchy).to_csv(APP / "hierarchy.csv", index=False)

# compact metadata for the app and FAIR layer
meta = {
    "titulo": "GraphAmbiCardio",
    "subtitulo": "Grafo de conhecimento sobre exposições ambientais, mecanismos moleculares, cardiogênese e cardiopatias congênitas",
    "versao": "0.3.0",
    "data": "2026-10-31",
    "municipio": "Campos dos Goytacazes, RJ, Brasil (IBGE 330100)",
    "periodo": "2010-2025",
    "licenca_codigo": "MIT",
    "licenca_dados": "Dados de terceiros mantêm suas licenças (PubMed/Europe PMC, SciELO/Crossref, CAPES, HPO, ClinVar, Reactome, DATASUS, ERA5-Land/Open-Meteo, VIGIAR)",
    "contato": "ryan.paulo@gsuite.iff.edu.br",
    "repositorio": "https://github.com/santosry/GraphAmbiCardio",
    "declaracao_ia": "Portaria CNPq nº 2.664/2026",
    "nota_revisao": "Busca estruturada não sistemática (não é revisão sistemática).",
}
(APP / "metadata.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

print("app data:", len(list(APP.glob('*'))), "files")
