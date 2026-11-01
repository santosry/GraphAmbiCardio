"""Generate FAIR metadata (DCAT + Frictionless Data Package) with checksums."""
from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
FAIR = ROOT / "fair"
FAIR.mkdir(exist_ok=True)

RESOURCES = [
    ("nos_grafo", "outputs/graph/nodes.csv", "Nós do grafo (exposições, mecanismos, genes, vias, processos, fenótipos)"),
    ("relacoes", "outputs/graph/relations.csv", "Relações agregadas com camada, confiança, grau e nível de evidência"),
    ("evidencias", "outputs/graph/evidence.csv", "Uma linha por evidência, com referência, espécie, desenho, citação e limitações"),
    ("hipoteses", "outputs/graph/hypotheses.csv", "Hipóteses geradas por composição de arestas observadas"),
    ("sinasc_anual", "outputs/tables/sinasc_annual_complete.csv", "Série anual SINASC (microdados + agregados TabNet 2023-2024)"),
    ("sih_anual", "outputs/tables/sih_annual.csv", "Internações SIH/SUS por ano (CHD core Q20-Q26, diagnóstico principal)"),
    ("sih_outras_circulatorias", "outputs/tables/sih_other_circulatory_annual.csv", "Internações SIH/SUS por ano para Q27-Q28 (não CHD)"),
    ("clima_diario", "data_processed/climate_daily_campos.csv", "Série diária ERA5-Land (modelo fixado) para Campos dos Goytacazes"),
    ("clima_qualidade", "data_processed/climate_quality_report.json", "QA e modelo explícito da série climática (era5_land)"),
    ("pm25_anual", "data_processed/pm25_campos_anual.csv", "PM2,5 anual municipal (VIGIAR/MS via pacote vigiar), 2010-2025"),
    ("pm25_mensal", "data_processed/pm25_campos_mensal.csv", "PM2,5 mensal municipal (VIGIAR/MS via pacote vigiar), 2010-2025"),
    ("caminhos", "outputs/tables/paths_exposure_phenotype.csv", "Caminhos exposição-fenótipo com confiança mínima"),
    ("lacunas", "outputs/tables/gap_analysis.csv", "Lacunas explícitas por exposição, mecanismo e processo"),
    ("candidatos_hipoteses", "outputs/tables/hypothesis_candidates.csv", "Hipóteses por sobreposição gênica (não evidenciais)"),
    ("modelos_exploratorios", "outputs/tables/exploratory_models.csv", "Modelos logísticos, Firth, cluster-robusto, contagem mensal e ajuste mútuo, com p e q (BH-FDR)"),
    ("sensibilidade_loo", "outputs/tables/sensitivity_leave_one_year_out.csv", "Sensibilidade leave-one-year-out com p e q"),
    ("sensibilidade_gestacional", "outputs/tables/gestational_window_sensitivity.csv", "Sensibilidade da janela de organogênese a ±7 dias de idade gestacional"),
    ("hipoteses_familia", "outputs/tables/hypothesis_family.csv", "Família completa de testes de sobreposição gênica, antes da seleção"),
    ("genes_mecanismos", "outputs/tables/mechanism_gene_sets.csv", "Conjuntos gênicos canônicos por mecanismo, com origem e presença no universo HPO"),
    ("correlacao_exposicoes", "outputs/tables/exposure_correlation.csv", "Matriz de correlação das exposições de janela"),
    ("vif_exposicoes", "outputs/tables/exposure_vif.csv", "Fatores de inflação de variância das exposições de janela"),
    ("figuras_site", "outputs/figures/site/manifest.json", "Manifesto das figuras do site com fonte, período, dados e SHA-256"),
    ("inmet_diario", "data_processed/inmet_campos_daily.csv", "INMET A607 (Campos dos Goytacazes): temperatura, umidade, chuva e vento, 2010-2025"),
    ("inmet_metadados", "data_processed/inmet_campos_metadata.json", "Metadados e checksum da estação INMET A607"),
    ("inmet_comparacao", "outputs/tables/inmet_era5_comparison.csv", "Comparação descritiva INMET A607 vs ERA5-Land"),
    ("inmet_relatorio", "reports/inmet_comparison.json", "Relatório legível por máquina da comparação INMET A607 vs ERA5-Land"),
    ("sinasc_outras_circulatorias", "outputs/tables/sinasc_other_circulatory_by_code.csv", "SINASC: códigos Q27-Q28 mantidos separados do CHD core"),
    ("dicionario_dados", "data_dictionary/data_dictionary.csv", "Dicionário de dados legível por máquina (variáveis, tipos, fontes e unidades)"),
]


def sha256(path: Path) -> str:
    # Normalise line endings so Windows (CRLF) and CI (LF) agree.
    data = path.read_bytes().replace(bytes((13, 10)), bytes((10)))
    return hashlib.sha256(data).hexdigest()


resources = []
for name, rel, desc in RESOURCES:
    p = ROOT / rel
    if not p.exists():
        continue
    fields = []
    if p.suffix.lower() == ".csv":
        df = pd.read_csv(p, nrows=5, low_memory=False)
        fields = [{"name": c, "type": str(df[c].dtype)} for c in df.columns]
    resources.append({
        "name": name,
        "path": rel,
        "description": desc,
        "format": p.suffix.lstrip("."),
        "mediatype": {".csv": "text/csv", ".json": "application/json", ".graphml": "application/xml", ".md": "text/markdown"}.get(p.suffix.lower(), "application/octet-stream"),
        "bytes": p.stat().st_size,
        "hash": "sha256:" + sha256(p),
        "schema": {"fields": fields} if fields else None,
    })

datapackage = {
    "name": "graphambicardio-graphambicardio",
    "title": "GraphAmbiCardio — grafo de conhecimento e dados derivados",
    "description": "Grafo de conhecimento sobre exposições ambientais, mecanismos moleculares, cardiogênese e cardiopatias congênitas, com dados locais de Campos dos Goytacazes (RJ) e proveniência por evidência.",
    "version": "0.4.0",
    "created": "2026-11-01",
    "licenses": [{"name": "MIT", "path": "https://opensource.org/licenses/MIT", "title": "Código sob MIT; dados de terceiros mantêm suas licenças"}],
    "contributors": [
        {"title": "Ryan de Paulo Santos", "role": "author", "path": "https://orcid.org/0009-0005-6770-2001"},
        {"title": "Letícia Maria Dias Freitas", "role": "author", "path": "https://orcid.org/0009-0009-9930-9588"},
    ],
    "keywords": ["congenital heart defects", "environmental exposure", "knowledge graph", "cardiogenesis", "Brazil", "FAIR"],
    "sources": [
        {"title": "PubMed/MEDLINE", "path": "https://pubmed.ncbi.nlm.nih.gov/"},
        {"title": "Europe PMC", "path": "https://europepmc.org/"},
        {"title": "HPO", "path": "https://hpo.jax.org/"},
        {"title": "ClinVar", "path": "https://www.ncbi.nlm.nih.gov/clinvar/"},
        {"title": "Reactome", "path": "https://reactome.org/"},
        {"title": "DATASUS/SINASC/SIH", "path": "https://datasus.saude.gov.br/"},
        {"title": "ERA5-Land via Open-Meteo (model fixed: era5_land)", "path": "https://open-meteo.com/en/docs/historical-weather-api"},
        {"title": "INMET A607 via BrazilMet", "path": "https://portal.inmet.gov.br/uploads/dadoshistoricos/"},
        {"title": "VIGIAR/MS via pacote vigiar", "path": "https://github.com/santosry/vigiar"},
        {"title": "SciELO via Crossref (prefixo 10.1590)", "path": "https://api.crossref.org/"},
        {"title": "CAPES Catálogo de Teses e Dissertações", "path": "https://catalogodeteses.capes.gov.br/"},
    ],
    "resources": resources,
}
(FAIR / "datapackage.json").write_text(json.dumps(datapackage, ensure_ascii=False, indent=2), encoding="utf-8")

dcat = {
    "@context": "https://www.w3.org/ns/dcat#",
    "@type": "Dataset",
    "identifier": "https://github.com/santosry/GraphAmbiCardio#v0.4.0",
    "name": "GraphAmbiCardio",
    "description": "Grafo de conhecimento com proveniência sobre exposições ambientais, mecanismos moleculares, processos do desenvolvimento cardíaco e fenótipos de cardiopatias congênitas, integrando literatura, bases biológicas curadas e dados ecológicos de Campos dos Goytacazes (2010-2025).",
    "version": "0.4.0",
    "issued": "2026-11-01",
    "modified": "2026-11-01",
    "creator": [
        {"@type": "Person", "name": "Ryan de Paulo Santos", "identifier": "https://orcid.org/0009-0005-6770-2001"},
        {"@type": "Person", "name": "Letícia Maria Dias Freitas", "identifier": "https://orcid.org/0009-0009-9930-9588"},
    ],
    "publisher": {"@type": "Organization", "name": "GraphAmbiCardio study team"},
    "contactPoint": {"@type": "ContactPoint", "email": "ryan.paulo@gsuite.iff.edu.br"},
    "keywords": ["congenital heart defects", "environmental exposure", "knowledge graph", "evidence grading", "FAIR", "Brazil"],
    "theme": ["http://id.nlm.nih.gov/mesh/D006330", "http://id.nlm.nih.gov/mesh/D000086382"],
    "spatial": {"@type": "Place", "name": "Campos dos Goytacazes, RJ, Brasil", "identifier": "IBGE:330100"},
    "temporal": {"@type": "PeriodOfTime", "startDate": "2010-01-01", "endDate": "2025-12-31"},
    "license": "https://opensource.org/licenses/MIT",
    "accessRights": "OPEN",
    "isAccessibleForFree": True,
    "distribution": [
        {"@type": "Distribution", "name": r["name"], "downloadURL": "https://github.com/santosry/GraphAmbiCardio/blob/main/" + r["path"], "format": r["format"], "byteSize": r["bytes"], "checksum": r["hash"]}
        for r in resources
    ],
    "conformsTo": "https://specs.frictionlessdata.io/data-package/",
    "provenance": "Cada aresta carrega referência (PMID/DOI/HPO/ClinVar/Reactome), tipo de evidência, espécie, desenho, janela de exposição, direção do efeito e limitações. Citações curadas foram verificadas contra o resumo indexado no PubMed. A validação climática usa a estação INMET A607 (latitude -21,7167; longitude -41,3500; altitude 25 m) e ERA5-Land.",
    "note": "Busca estruturada não sistemática. Hipóteses são explicitamente separadas das evidências.",
}
(FAIR / "metadata.json").write_text(json.dumps(dcat, ensure_ascii=False, indent=2), encoding="utf-8")
# Keep the self-contained app bundle in sync with the FAIR layer.
(ROOT / "app" / "www").mkdir(parents=True, exist_ok=True)
shutil.copy2(FAIR / "datapackage.json", ROOT / "app" / "www" / "datapackage.json")
shutil.copy2(FAIR / "metadata.json", ROOT / "app" / "www" / "metadata.json")
print(f"FAIR metadata: {len(resources)} resources")
