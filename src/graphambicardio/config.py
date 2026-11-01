"""Central configuration for the GraphAmbiCardio study.

All study constants that must remain traceable (municipality, period,
exposure panel, phenotype panel, gene panel, evidence weights) live here.
Nothing in this file is data: it is the pre-registered analysis plan.
"""

from __future__ import annotations

import os
from pathlib import Path

# --------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[2]

DATA_RAW = ROOT / "data_raw"
DATA_PROCESSED = ROOT / "data_processed"
DATA_DICTIONARY = ROOT / "data_dictionary"
LITERATURE = ROOT / "literature"
SEARCHES = LITERATURE / "searches"
SCREENING = LITERATURE / "screening"
CURATED = LITERATURE / "curated"
OUTPUTS = ROOT / "outputs"
FIGURES = OUTPUTS / "figures"
TABLES = OUTPUTS / "tables"
GRAPH_OUT = OUTPUTS / "graph"
REPORTS = ROOT / "reports"
LOGS = ROOT / "logs"
TESTS = ROOT / "tests"

for _p in (
    DATA_RAW,
    DATA_PROCESSED,
    DATA_DICTIONARY,
    SEARCHES,
    SCREENING,
    CURATED,
    OUTPUTS,
    FIGURES,
    TABLES,
    GRAPH_OUT,
    REPORTS,
    LOGS,
):
    _p.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------------------------------
# Study scope
# --------------------------------------------------------------------------
STUDY_ID = "GraphAmbiCardio"
STUDY_VERSION = "0.4.0"
ONTOLOGY_VERSION = "0.4.0"

PERIOD_START = 2010
PERIOD_END = 2025

MUNICIPALITY = {
    "name": "Campos dos Goytacazes",
    "uf": "RJ",
    "ibge6": "330100",
    "ibge7": "3301000",
    "latitude": -21.7545,
    "longitude": -41.3245,
    "timezone": "America/Sao_Paulo",
}

# --------------------------------------------------------------------------
# Phenotypes (CID-10 Q20-Q28 anchor + HPO).  HPO ids verified against the
# HPO API (ontology.jax.org) on the retrieval date recorded in the logs.
# --------------------------------------------------------------------------
PHENOTYPES = [
    {
        "id": "CHD:VSD",
        "label": "Ventricular septal defect",
        "label_pt": "Comunicacao interventricular",
        "cid10": ["Q21.0"],
        "hpo": "HP:0001629",
        "category": "septal_defect",
    },
    {
        "id": "CHD:ASD",
        "label": "Atrial septal defect",
        "label_pt": "Comunicacao interatrial",
        "cid10": ["Q21.1"],
        "hpo": "HP:0001631",
        "category": "septal_defect",
    },
    {
        "id": "CHD:AVSD",
        "label": "Atrioventricular septal defect",
        "label_pt": "Defeito do septo atrioventricular",
        "cid10": ["Q21.2"],
        "hpo": "HP:0006695",
        "category": "septal_defect",
    },
    {
        "id": "CHD:TOF",
        "label": "Tetralogy of Fallot",
        "label_pt": "Tetralogia de Fallot",
        "cid10": ["Q21.3"],
        "hpo": "HP:0001636",
        "category": "outflow_tract",
    },
    {
        "id": "CHD:DORV",
        "label": "Double outlet right ventricle",
        "label_pt": "Dupla via de saida do ventriculo direito",
        "cid10": ["Q20.1"],
        "hpo": "HP:0001719",
        "category": "outflow_tract",
    },
    {
        "id": "CHD:TGA",
        "label": "Transposition of the great arteries",
        "label_pt": "Transposicao das grandes arterias",
        "cid10": ["Q20.3"],
        "hpo": "HP:0001669",
        "category": "great_arteries",
    },
    {
        "id": "CHD:HLHS",
        "label": "Hypoplastic left heart (HLHS)",
        "label_pt": "Sindrome do coracao esquerdo hipoplasico",
        "cid10": ["Q23.4"],
        "hpo": "HP:0004383",
        "category": "ventricle",
        "mapping_note": "HPO has no dedicated HLHS term; HP:0004383 (hypoplastic left ventricle) is the closest ancestor. OMIM 241550.",
    },
    {
        "id": "CHD:COA",
        "label": "Coarctation of the aorta",
        "label_pt": "Coartacao da aorta",
        "cid10": ["Q25.1"],
        "hpo": "HP:0001680",
        "category": "great_arteries",
    },
    {
        "id": "CHD:PDA",
        "label": "Patent ductus arteriosus",
        "label_pt": "Persistencia do canal arterial",
        "cid10": ["Q25.0"],
        "hpo": "HP:0001643",
        "category": "great_arteries",
    },
    {
        "id": "CHD:PS",
        "label": "Pulmonary valve stenosis",
        "label_pt": "Estenose valvar pulmonar",
        "cid10": ["Q25.6"],
        "hpo": "HP:0001642",
        "category": "valve",
    },
    {
        "id": "CHD:AS",
        "label": "Aortic valve stenosis",
        "label_pt": "Estenose valvar aortica",
        "cid10": ["Q23.0"],
        "hpo": "HP:0001650",
        "category": "valve",
    },
    {
        "id": "CHD:TAPVC",
        "label": "Total anomalous pulmonary venous connection",
        "label_pt": "Drenagem anomala total de veias pulmonares",
        "cid10": ["Q26.2"],
        "hpo": "HP:0011720",
        "category": "venous",
    },
    {
        "id": "CHD:TRUNCUS",
        "label": "Truncus arteriosus",
        "label_pt": "Tronco arterial comum",
        "cid10": ["Q20.0"],
        "hpo": "HP:0001660",
        "category": "outflow_tract",
    },
    {
        "id": "CHD:EBSTEIN",
        "label": "Ebstein anomaly",
        "label_pt": "Anomalia de Ebstein",
        "cid10": ["Q22.5"],
        "hpo": "HP:0010316",
        "category": "valve",
    },
]

# Local case group: congenital malformations of cardiac chambers and
# connections, septa, valves and great vessels (Q20-Q26). Q27 and Q28 are
# other circulatory malformations and are kept as a separate group.
CID10_CHAPTER_CHD = [f"Q2{i}" for i in range(0, 7)]  # Q20 .. Q26
CASE_GROUP_NAME = "Malformações congênitas das câmaras cardíacas e conexões, septos, válvulas e grandes vasos"
CASE_GROUP_CID10 = "Q20–Q26"
CID10_OTHER_CIRCULATORY = ["Q27", "Q28"]
CID10_CIRCULATORY_ALL = CID10_CHAPTER_CHD + CID10_OTHER_CIRCULATORY

# --------------------------------------------------------------------------
# Environmental / chemical exposures considered in the feasibility phase.
# `query_terms` are English literature terms; they are deliberately broader
# than the node label so that the search does not miss synonym-based papers.
# --------------------------------------------------------------------------
EXPOSURES = [
    {
        "id": "EXP:PM25",
        "label": "Fine particulate matter (PM2.5)",
        "class": "air_pollutant",
        "query_terms": ['"particulate matter"[MeSH]', '"PM2.5"[tiab]', '"PM 2.5"[tiab]', '"fine particulate matter"[tiab]'],
        "local_relevance": "Sugarcane burning and biomass smoke are relevant sources in the Norte Fluminense region; no local PM2.5 monitoring series is available (documented gap).",
        "priority": "primary",
    },
    {
        "id": "EXP:PM10",
        "label": "Coarse particulate matter (PM10)",
        "class": "air_pollutant",
        "query_terms": ['"particulate matter"[MeSH]', '"PM10"[tiab]', '"PM 10"[tiab]'],
        "local_relevance": "Same sources as PM2.5; no local monitoring.",
        "priority": "conditional",
    },
    {
        "id": "EXP:CO",
        "label": "Carbon monoxide (CO)",
        "class": "air_pollutant",
        "query_terms": ['"carbon monoxide"[MeSH]', '"carbon monoxide"[tiab]', '"CO exposure"[tiab]'],
        "local_relevance": "Vehicular and biomass-combustion marker; no local monitoring.",
        "priority": "conditional",
    },
    {
        "id": "EXP:NO2",
        "label": "Nitrogen dioxide (NO2) / traffic-related air pollution",
        "class": "air_pollutant",
        "query_terms": ['"nitrogen dioxide"[MeSH]', '"nitrogen dioxide"[tiab]', '"NO2"[tiab]', '"traffic-related air pollution"[tiab]'],
        "local_relevance": "Vehicular and industrial emissions; no local monitoring series.",
    },
    {
        "id": "EXP:O3",
        "label": "Ozone (O3)",
        "class": "air_pollutant",
        "query_terms": ['"ozone"[MeSH]', '"ozone"[tiab]'],
        "local_relevance": "Photochemical pollution; no local monitoring series.",
    },
    {
        "id": "EXP:SO2",
        "label": "Sulfur dioxide (SO2)",
        "class": "air_pollutant",
        "query_terms": ['"sulfur dioxide"[MeSH]', '"sulfur dioxide"[tiab]', '"sulphur dioxide"[tiab]'],
        "local_relevance": "Industrial emissions; no local monitoring series.",
    },
    {
        "id": "EXP:HEAT",
        "label": "Maternal heat exposure / hyperthermia",
        "class": "climate",
        "query_terms": ['"hot temperature"[MeSH]', '"hyperthermia"[MeSH]', '"hyperthermia"[tiab]', '"heat wave*"[tiab]', '"high temperature"[tiab]'],
        "local_relevance": "Daily temperature series available from ERA5-Land reanalysis for the municipality.",
        "priority": "secondary",
    },
    {
        "id": "EXP:COLD",
        "label": "Cold exposure",
        "class": "climate",
        "query_terms": ['"cold temperature"[MeSH]', '"cold spell*"[tiab]', '"low temperature"[tiab]'],
        "local_relevance": "Daily temperature series available from ERA5-Land reanalysis.",
    },
    {
        "id": "EXP:HUMIDITY",
        "label": "Relative humidity (contextual variable)",
        "class": "climate_context",
        "query_terms": ['"humidity"[MeSH]', '"relative humidity"[tiab]'],
        "local_relevance": "Available daily from ERA5-Land. Treated as contextual/confounding variable, not as a presumed causal exposure.",
        "priority": "contextual",
    },
    {
        "id": "EXP:PEST",
        "label": "Pesticides",
        "class": "chemical",
        "query_terms": ['"pesticides"[MeSH]', '"pesticide*"[tiab]', '"organophosphate*"[tiab]', '"glyphosate"[tiab]', '"insecticide*"[tiab]', '"herbicide*"[tiab]'],
        "local_relevance": "Intensive sugarcane and other agricultural activity in the region.",
    },
    {
        "id": "EXP:SOLV",
        "label": "Organic solvents (e.g., trichloroethylene, benzene)",
        "class": "chemical",
        "query_terms": ['"solvents"[MeSH]', '"trichloroethylene"[MeSH]', '"benzene"[MeSH]', '"organic solvent*"[tiab]', '"trichloroethylene"[tiab]', '"benzene exposure"[tiab]'],
        "local_relevance": "Industrial and petrochemical activity in the region.",
    },
    {
        "id": "EXP:METALS",
        "label": "Heavy metals (arsenic, lead, mercury)",
        "class": "chemical",
        "query_terms": ['"arsenic"[MeSH]', '"lead"[MeSH]', '"mercury"[MeSH]', '"metals, heavy"[MeSH]', '"heavy metal*"[tiab]'],
        "local_relevance": "Occupational and environmental sources; no local biomonitoring.",
    },
    {
        "id": "EXP:SMOKE",
        "label": "Tobacco smoke",
        "class": "chemical",
        "query_terms": ['"tobacco smoke pollution"[MeSH]', '"smoking"[MeSH]', '"tobacco smoke"[tiab]', '"cigarette smoke"[tiab]'],
        "local_relevance": "Behavioural exposure with individual-level data in SINASC only partially available.",
    },
    {
        "id": "EXP:ALCOHOL",
        "label": "Alcohol (ethanol)",
        "class": "chemical",
        "query_terms": ['"ethanol"[MeSH]', '"alcohol drinking"[MeSH]', '"alcohol"[tiab]', '"ethanol"[tiab]', '"fetal alcohol"[tiab]'],
        "local_relevance": "Behavioural exposure; not recorded in SINASC.",
    },
    {
        "id": "EXP:VPA",
        "label": "Valproic acid",
        "class": "medication",
        "query_terms": ['"valproic acid"[MeSH]', '"valproic acid"[tiab]', '"valproate"[tiab]'],
        "local_relevance": "Therapeutic exposure; not recorded in SINASC.",
    },
    {
        "id": "EXP:RA",
        "label": "Retinoic acid / vitamin A derivatives",
        "class": "medication",
        "query_terms": ['"tretinoin"[MeSH]', '"retinoic acid"[tiab]', '"isotretinoin"[tiab]', '"vitamin A"[tiab]'],
        "local_relevance": "Therapeutic and nutritional exposure; not recorded in SINASC.",
    },
    {
        "id": "EXP:DIOXIN",
        "label": "Dioxins / PCBs (endocrine-disrupting chemicals)",
        "class": "chemical",
        "query_terms": ['"dioxins"[MeSH]', '"polychlorinated biphenyls"[MeSH]', '"dioxin*"[tiab]', '"TCDD"[tiab]', '"polychlorinated biphenyl*"[tiab]', '"PCB"[tiab]'],
        "local_relevance": "Persistent organic pollutants; no local biomonitoring.",
    },
]

# --------------------------------------------------------------------------
# Biological mechanisms (curated vocabulary; not a claim of involvement)
# --------------------------------------------------------------------------
MECHANISMS = [
    ("MECH:OXSTRESS", "Oxidative stress"),
    ("MECH:INFLAM", "Inflammation"),
    ("MECH:EPIGEN", "Epigenetic alteration (DNA methylation, histone modification, ncRNA)"),
    ("MECH:MITO", "Mitochondrial dysfunction"),
    ("MECH:CELLSIG", "Altered cell signalling"),
    ("MECH:GENE_EXPR", "Altered gene expression"),
    ("MECH:APOPTOSIS", "Apoptosis / cell death"),
    ("MECH:PROLIF", "Proliferation / cell-cycle perturbation"),
    ("MECH:HEATSHOCK", "Heat-shock / proteostasis response"),
    ("MECH:AHR", "Aryl hydrocarbon receptor (AHR) signalling"),
    ("MECH:RA_SIGNAL", "Retinoic acid signalling perturbation"),
    ("MECH:WNT", "Wnt/beta-catenin signalling perturbation"),
    ("MECH:HDAC", "Histone deacetylase (HDAC) inhibition"),
    ("MECH:HYPOXIA", "Hypoxia / HIF signalling"),
    ("MECH:NEURAL_CREST", "Neural crest cell perturbation"),
    ("MECH:ENDOTHELIAL", "Endothelial / vascular perturbation"),
]

# --------------------------------------------------------------------------
# Cardiac developmental processes (embryology anchor)
# --------------------------------------------------------------------------
PROCESSES = [
    ("PROC:HEART_TUBE", "Heart tube formation"),
    ("PROC:LOOPING", "Cardiac looping"),
    ("PROC:CHAMBER", "Chamber development"),
    ("PROC:SEPTATION", "Atrial and ventricular septation"),
    ("PROC:AV_CUSHION", "Atrioventricular cushion / valve development"),
    ("PROC:OFT", "Outflow tract development"),
    ("PROC:GREAT_VESSELS", "Great vessel formation"),
    ("PROC:NEURAL_CREST_MIGRATION", "Cardiac neural crest migration"),
    ("PROC:CM_DIFF", "Cardiomyocyte differentiation"),
    ("PROC:CORONARY", "Coronary / vascular development"),
    ("PROC:CONDUCTION", "Cardiac conduction system development"),
]

# --------------------------------------------------------------------------
# Gene panel used for structured queries (ClinVar, Reactome).  The panel is a
# starting point only: HPO/ClinVar-derived genes are added automatically.
# --------------------------------------------------------------------------
GENE_PANEL = [
    "NKX2-5", "GATA4", "GATA6", "TBX5", "TBX1", "TBX20", "NOTCH1", "JAG1",
    "NKX2-6", "ZIC3", "CITED2", "HAND2", "MEF2C", "NODAL", "ACVR2B",
    "LEFTY2", "PTPN11", "RAF1", "SOS1", "KRAS", "NRAS", "BRAF", "MAP2K1",
    "MAP2K2", "SHOC2", "CBL", "ELN", "FBN1", "TGFBR1", "TGFBR2", "SMAD3",
    "MED13L", "CHD7", "KMT2D", "EP300", "CREBBP", "SALL4", "MYH6", "ACTC1",
    "MYH7", "FLT4", "FOXC2", "GDF1", "DLL4", "HEY2", "TFAP2B", "SEMA3E",
]

# --------------------------------------------------------------------------
# Evidence framework (pre-registered weights)
# --------------------------------------------------------------------------
EVIDENCE_TYPES = {
    "direct_human": {
        "label": "Direct human epidemiological evidence",
        "weight": 1.0,
        "description": "Association investigated in human populations with the phenotype and exposure window of interest.",
    },
    "experimental_human": {
        "label": "Human experimental / functional evidence",
        "weight": 0.85,
        "description": "Human cells, organoids or explants; functional assay of the mechanism.",
    },
    "experimental_animal": {
        "label": "Animal experimental evidence",
        "weight": 0.65,
        "description": "In vivo animal model; species and developmental window recorded.",
    },
    "experimental_cell": {
        "label": "Cell-line experimental evidence",
        "weight": 0.5,
        "description": "Cell lines or non-human in vitro systems.",
    },
    "structured_database": {
        "label": "Curated structured database annotation",
        "weight": 0.7,
        "description": "Annotation retrieved from a curated database (HPO, ClinVar, Reactome).",
    },
    "indirect": {
        "label": "Indirect evidence",
        "weight": 0.4,
        "description": "Supported only through documented intermediate steps.",
    },
    "hypothesis": {
        "label": "Hypothesis / not demonstrated",
        "weight": 0.1,
        "description": "Plausible relation without direct empirical support in retrieved sources.",
    },
}

STUDY_DESIGN_WEIGHTS = {
    "systematic_review_meta_analysis": 0.9,
    "systematic_review": 0.8,
    "meta_analysis": 0.9,
    "cohort": 0.9,
    "case_control": 0.8,
    "registry": 0.8,
    "cross_sectional": 0.6,
    "ecological": 0.45,
    "animal_in_vivo": 0.6,
    "in_vitro": 0.4,
    "in_silico": 0.2,
    "narrative_review": 0.7,
    "curated_database": 0.9,
    "unknown": 0.3,
}

# Minimum confidence for an edge to enter the "observed/curated core" graph.
CONFIDENCE_CORE_THRESHOLD = 0.55

# --------------------------------------------------------------------------
# External services
# --------------------------------------------------------------------------
NCBI_API_KEY = os.environ.get("NCBI_API_KEY", "")
NCBI_EMAIL = os.environ.get("NCBI_EMAIL", "ryan.paulo@gsuite.iff.edu.br")
NCBI_TOOL = "GraphAmbiCardio"

USER_AGENT = "GraphAmbiCardio/0.1 (academic research; contact: ryan.paulo@gsuite.iff.edu.br)"
HTTP_TIMEOUT = 60
HTTP_RETRIES = 3

PUBMED_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
EUROPEPMC_BASE = "https://www.ebi.ac.uk/europepmc/webservices/rest"
HPO_API = "https://ontology.jax.org/api/hp"
MONARCH_API = "https://api.monarchinitiative.org/v3/api"
REACTOME_ANALYSIS = "https://reactome.org/AnalysisService"
REACTOME_CONTENT = "https://reactome.org/ContentService"
OPEN_METEO_ARCHIVE = "https://archive-api.open-meteo.com/v1/archive"
OPEN_METEO_MODEL = "era5_land"
OPEN_METEO_MODEL_LABEL = "ERA5-Land"
OPEN_METEO_RESOLUTION_KM = 9

DATASUS_SINASC_FTP = "ftp://ftp.datasus.gov.br/dissemin/publicos/SINASC/NOV/DNRES"
DATASUS_SINASC_PRELIM_FTP = "ftp://ftp.datasus.gov.br/dissemin/publicos/SINASC/PRELIM/DNRES"
DATASUS_SIH_FTP = "ftp://ftp.datasus.gov.br/dissemin/publicos/SIHSUS/200801_/Dados"

# Data availability observed at the DATASUS FTP on 2026-10-31 (recorded in docs).
SINASC_YEARS_AVAILABLE = list(range(2010, 2023)) + [2025]
SINASC_YEARS_MISSING = [2023, 2024]
SINASC_PRELIMINARY_YEARS = [2025]

# --------------------------------------------------------------------------
# Search block used in the PRISMA-ScR searches (concept blocks)
# --------------------------------------------------------------------------
SEARCH_CONCEPTS = {
    "population": '("heart defects, congenital"[MeSH] OR "congenital heart defect*"[tiab] OR "congenital heart disease*"[tiab] OR "congenital heart anomal*"[tiab] OR "cardiac anomal*"[tiab])',
    "exposure": '("environmental exposure"[MeSH] OR "air pollution"[MeSH] OR "particulate matter"[MeSH] OR "maternal exposure"[MeSH] OR "pesticides"[MeSH] OR "metals, heavy"[MeSH] OR "hot temperature"[MeSH] OR "solvents"[MeSH] OR "tobacco smoke pollution"[MeSH] OR "alcohol drinking"[MeSH] OR "valproic acid"[MeSH])',
    "mechanism": '("oxidative stress"[MeSH] OR "epigenesis, genetic"[MeSH] OR "inflammation"[MeSH] OR "signal transduction"[MeSH] OR "gene expression regulation, developmental"[MeSH] OR "mitochondria"[MeSH])',
    "development": '("cardiogenesis"[tiab] OR "heart development"[tiab] OR "embryonic heart"[tiab] OR "neural crest"[tiab] OR "outflow tract"[tiab] OR "septation"[tiab])',
}

# Free-text terms used to query each phenotype (PubMed syntax).  Abbreviations
# are only used inside a congenital-heart-disease context block.
PHENOTYPE_QUERY_TERMS = {
    "CHD:VSD": ['"ventricular septal defect"[tiab]', '"ventricular septal defects"[tiab]', '"VSD"[tiab]'],
    "CHD:ASD": ['"atrial septal defect"[tiab]', '"atrial septal defects"[tiab]', '"ASD"[tiab]'],
    "CHD:AVSD": ['"atrioventricular septal defect"[tiab]', '"atrioventricular canal"[tiab]', '"AVSD"[tiab]'],
    "CHD:TOF": ['"tetralogy of fallot"[tiab]', '"fallot"[tiab]'],
    "CHD:DORV": ['"double outlet right ventricle"[tiab]', '"DORV"[tiab]'],
    "CHD:TGA": ['"transposition of the great arteries"[tiab]', '"transposition of the great vessels"[tiab]', '"D-TGA"[tiab]'],
    "CHD:HLHS": ['"hypoplastic left heart"[tiab]', '"HLHS"[tiab]'],
    "CHD:COA": ['"coarctation of the aorta"[tiab]', '"aortic coarctation"[tiab]'],
    "CHD:PDA": ['"patent ductus arteriosus"[tiab]', '"ductus arteriosus"[tiab]'],
    "CHD:PS": ['"pulmonary stenosis"[tiab]', '"pulmonary valve stenosis"[tiab]', '"pulmonic stenosis"[tiab]'],
    "CHD:AS": ['"aortic stenosis"[tiab]', '"aortic valve stenosis"[tiab]'],
    "CHD:TAPVC": ['"total anomalous pulmonary venous connection"[tiab]', '"TAPVC"[tiab]', '"TAPVR"[tiab]'],
    "CHD:TRUNCUS": ['"truncus arteriosus"[tiab]', '"common arterial trunk"[tiab]'],
    "CHD:EBSTEIN": ['"ebstein anomaly"[tiab]', '"ebstein"[tiab]'],
}
