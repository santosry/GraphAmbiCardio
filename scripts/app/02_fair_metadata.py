"""Generate FAIR metadata (DCAT + Frictionless Data Package) with checksums."""
from __future__ import annotations

import hashlib
import json
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
    ("sih_anual", "outputs/tables/sih_annual.csv", "Internações SIH/SUS por ano (Q20-Q28, diagnóstico principal)"),
    ("clima_diario", "data_processed/climate_daily_campos.csv", "Série diária ERA5-Land para Campos dos Goytacazes"),
    ("pm25_anual", "data_processed/pm25_campos_anual.csv", "PM2,5 anual municipal (VIGIAR/MS via pacote vigiar), 2010-2025"),
    ("pm25_mensal", "data_processed/pm25_campos_mensal.csv", "PM2,5 mensal municipal (VIGIAR/MS via pacote vigiar), 2010-2025"),
    ("caminhos", "outputs/tables/paths_exposure_phenotype.csv", "Caminhos exposição-fenótipo com confiança mínima"),
    ("lacunas", "outputs/tables/gap_analysis.csv", "Lacunas explícitas por exposição, mecanismo e processo"),
    ("candidatos_hipoteses", "outputs/tables/hypothesis_candidates.csv", "Hipóteses por sobreposição gênica (não evidenciais)"),
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


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
        "mediatype": "text/csv" if p.suffix == ".csv" else "application/octet-stream",
        "bytes": p.stat().st_size,
        "hash": "sha256:" + sha256(p),
        "schema": {"fields": fields} if fields else None,
    })

datapackage = {
    "name": "graphambicardio-graphambicardio",
    "title": "GraphAmbiCardio — grafo de conhecimento e dados derivados",
    "description": "Grafo de conhecimento sobre exposições ambientais, mecanismos moleculares, cardiogênese e cardiopatias congênitas, com dados locais de Campos dos Goytacazes (RJ) e proveniência por evidência.",
    "version": "0.2.0",
    "created": "2026-10-31",
    "licenses": [{"name": "MIT", "path": "https://opensource.org/licenses/MIT", "title": "Código sob MIT; dados de terceiros mantêm suas licenças"}],
    "contributors": [{"title": "GraphAmbiCardio study team", "role": "author"}],
    "keywords": ["congenital heart defects", "environmental exposure", "knowledge graph", "cardiogenesis", "Brazil", "FAIR"],
    "sources": [
        {"title": "PubMed/MEDLINE", "path": "https://pubmed.ncbi.nlm.nih.gov/"},
        {"title": "Europe PMC", "path": "https://europepmc.org/"},
        {"title": "HPO", "path": "https://hpo.jax.org/"},
        {"title": "ClinVar", "path": "https://www.ncbi.nlm.nih.gov/clinvar/"},
        {"title": "Reactome", "path": "https://reactome.org/"},
        {"title": "DATASUS/SINASC/SIH", "path": "https://datasus.saude.gov.br/"},
        {"title": "ERA5-Land via Open-Meteo", "path": "https://open-meteo.com/en/docs/historical-weather-api"},
        {"title": "SciELO via Crossref (prefixo 10.1590)", "path": "https://api.crossref.org/"},
        {"title": "CAPES Catálogo de Teses e Dissertações", "path": "https://catalogodeteses.capes.gov.br/"},
    ],
    "resources": resources,
}
(FAIR / "datapackage.json").write_text(json.dumps(datapackage, ensure_ascii=False, indent=2), encoding="utf-8")

dcat = {
    "@context": "https://www.w3.org/ns/dcat#",
    "@type": "Dataset",
    "identifier": "https://github.com/santosry/GraphAmbiCardio#v0.2.0",
    "name": "GraphAmbiCardio",
    "description": "Grafo de conhecimento com proveniência sobre exposições ambientais, mecanismos moleculares, processos do desenvolvimento cardíaco e fenótipos de cardiopatias congênitas, integrando literatura, bases biológicas curadas e dados ecológicos de Campos dos Goytacazes (2010-2025).",
    "version": "0.2.0",
    "issued": "2026-10-31",
    "modified": "2026-10-31",
    "creator": {"@type": "Organization", "name": "GraphAmbiCardio study team"},
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
    "provenance": "Cada aresta carrega referência (PMID/DOI/HPO/ClinVar/Reactome), tipo de evidência, espécie, desenho, janela de exposição, direção do efeito e limitações. Citações curadas foram verificadas contra o resumo indexado no PubMed.",
    "note": "Busca estruturada não sistemática. Hipóteses são explicitamente separadas das evidências.",
}
(FAIR / "metadata.json").write_text(json.dumps(dcat, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"FAIR metadata: {len(resources)} resources")
