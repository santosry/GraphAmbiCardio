"""Integration: assemble the provenance-first evidence table and build the graph.

Steps
-----
1. Verify every manually curated quote against the PubMed abstract (hard fail).
2. Add structured database evidence (HPO, ClinVar, Reactome).
3. Add local epidemiological/environmental indicator nodes and context edges.
4. Add an explicitly separated inferred layer (pathway -> process keyword map)
   and a hypothesis layer (exposure -> process 2-hop paths).
5. Export CSV, GraphML and JSON.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import networkx as nx  # noqa: E402
import pandas as pd  # noqa: E402

from graphambicardio import config  # noqa: E402
from graphambicardio.curation import seed_edges  # noqa: E402
from graphambicardio.graph import build, hypotheses  # noqa: E402
from graphambicardio.io_utils import get_logger, read_csv, today, write_csv, write_json  # noqa: E402
from graphambicardio.literature.pubmed import efetch  # noqa: E402

log = get_logger("build_graph")

PATHWAY_KEYWORDS = (
    "heart", "cardiac", "cardiogenesis", "muscle", "mesoderm", "embryo",
    "development", "wnt", "notch", "bmp", "fgf", "retinoic", "tgf",
    "apoptosis", "oxidative", "mitochondri", "neural crest", "endotheli",
    "vascul", "valve", "septation", "chamber", "morphogenesis", "sig",
)

PROCESS_KEYWORD_MAP = [
    ("heart tube", "PROC:HEART_TUBE"),
    ("looping", "PROC:LOOPING"),
    ("sept", "PROC:SEPTATION"),
    ("valve", "PROC:AV_CUSHION"),
    ("cushion", "PROC:AV_CUSHION"),
    ("outflow", "PROC:OFT"),
    ("conotruncal", "PROC:OFT"),
    ("neural crest", "PROC:NEURAL_CREST_MIGRATION"),
    ("chamber", "PROC:CHAMBER"),
    ("cardiomyocyte", "PROC:CM_DIFF"),
    ("cardiac muscle", "PROC:CM_DIFF"),
    ("conduction", "PROC:CONDUCTION"),
    ("coronary", "PROC:CORONARY"),
    ("angiogen", "PROC:CORONARY"),
    ("vascul", "PROC:GREAT_VESSELS"),
    ("endotheli", "PROC:ENDOTHELIAL"),
]


def _norm(s: str) -> str:
    s = (s or "").replace("\u2013", "-").replace("\u2014", "-").replace("\u2212", "-")
    s = s.replace("\u03bc", "µ").replace("\u2264", "<=").replace("\u2265", ">=")
    return re.sub(r"\s+", " ", s).strip().lower()


def verify_quotes(edges: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    pmids = sorted({e["reference"] for e in edges})
    studies = {s.pmid: s for s in efetch(pmids)}
    missing = []
    for e in edges:
        s = studies.get(e["reference"])
        if not s:
            missing.append((e["reference"], "PMID not retrieved"))
            continue
        if _norm(e["quote"]) not in _norm(s.abstract):
            missing.append((e["reference"], e["quote"][:80]))
        e["_study"] = {
            "pmid": s.pmid,
            "title": s.title,
            "journal": s.journal,
            "year": s.year,
            "doi": s.doi,
            "first_author": s.first_author,
        }
    if missing:
        for m in missing:
            log.error("quote verification failed: %s | %s", m[0], m[1])
        raise SystemExit(f"quote verification failed for {len(missing)} edge(s)")
    log.info("verified %s curated quotes across %s PMIDs", len(edges), len(pmids))
    return studies


def curated_evidence() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    edges = (
        seed_edges.EXPOSURE_PHENOTYPE
        + seed_edges.EXPOSURE_MECHANISM
        + seed_edges.MECHANISM_PROCESS
        + seed_edges.PROCESS_PHENOTYPE
        + seed_edges.GENE_PHENOTYPE
        + seed_edges.ADDITIONAL_EDGES
    )
    verify_quotes(edges)
    rows = []
    studies = {}
    for e in edges:
        st = e.pop("_study")
        studies[st["pmid"]] = st
        rows.append(
            build.make_evidence(
                e["source_id"], e["source_type"], e["target_id"], e["target_type"],
                e["relation"],
                layer=e["layer"],
                evidence_type=e["evidence_type"],
                study_design=e["study_design"],
                species=e["species"],
                population_or_model=e["population_or_model"],
                exposure_window=e["exposure_window"],
                effect_direction=e["effect_direction"],
                context=e["context"],
                quote=e["quote"],
                reference=e["reference"],
                reference_type="PMID",
                source_database="PubMed/MEDLINE (manual curation)",
                retrieved_at=today(),
                notes=e.get("notes", ""),
            )
        )
    anchor_rows = []
    for p, s in sorted(studies.items()):
        anchor_rows.append(
            {
                "pmid": p,
                "title": s["title"],
                "year": s["year"],
                "journal": s["journal"],
                "first_author": s["first_author"],
                "doi": s["doi"],
                "doi_url": f"https://doi.org/{s['doi']}" if s["doi"] else "",
                "pubmed_url": f"https://pubmed.ncbi.nlm.nih.gov/{p}/",
            }
        )
    write_csv(config.CURATED / "anchor_studies.csv", anchor_rows)
    write_csv(config.CURATED / "curated_edges.csv", rows, fieldnames=build.EVIDENCE_FIELDS)
    log.info("curated: %s evidence rows, %s anchor studies", len(rows), len(anchor_rows))
    return rows, anchor_rows


def hpo_evidence() -> list[dict[str, Any]]:
    path = config.DATA_PROCESSED / "hpo_gene_phenotype_edges.csv"
    if not path.exists():
        log.warning("HPO edges not found; skipping")
        return []
    rows = []
    for r in read_csv(path):
        rows.append(
            build.make_evidence(
                f"GENE:{r['gene_symbol']}", "Gene", r["phenotype_id"], "Phenotype",
                "GENE_ASSOCIATED_WITH_PHENOTYPE",
                layer="structured",
                evidence_type="structured_database",
                study_design="curated_database",
                species="human",
                population_or_model=r.get("disease_id", ""),
                context=f"HPO annotation frequency={r.get('frequency', '')}",
                reference=r.get("disease_id", ""),
                reference_type="HPO annotation",
                source_database="HPO genes_to_phenotype.txt",
                notes=f"HPO term {r['hpo_id']} ({r['hpo_name']})",
            )
        )
    log.info("HPO evidence rows: %s", len(rows))
    return rows


def clinvar_evidence() -> list[dict[str, Any]]:
    path = config.DATA_PROCESSED / "clinvar_variants.csv"
    if not path.exists():
        log.warning("ClinVar output not found; skipping")
        return []
    df = pd.read_csv(path)
    df = df[df["germline_classification"].astype(str).str.contains("athogenic", case=False, na=False)]
    rows = []
    for _, r in df.iterrows():
        gene = str(r.get("query_gene") or r.get("gene_symbol", "")).split(";")[0]
        if not gene:
            continue
        var_id = f"VAR:{r.get('accession', '')}"
        rows.append(
            build.make_evidence(
                var_id, "Variant", f"GENE:{gene}", "Gene",
                "VARIANT_IN_GENE",
                layer="structured",
                evidence_type="structured_database",
                study_design="curated_database",
                species="human",
                population_or_model=str(r.get("trait_set", "")),
                context=str(r.get("germline_classification", "")),
                reference=str(r.get("accession", "")),
                reference_type="ClinVar accession",
                source_database="ClinVar",
                notes=f"review={r.get('review_status', '')}; cDNA={r.get('cdna_change', '')}",
            )
        )
        # variant -> phenotype only when the ClinVar trait text matches our vocabulary
        trait = str(r.get("trait_set", "")).lower()
        for ph in config.PHENOTYPES:
            keys = [ph["label"].lower()] + [w for w in ph["label"].lower().split() if len(w) > 5]
            if any(k in trait for k in keys if k):
                rows.append(
                    build.make_evidence(
                        var_id, "Variant", ph["id"], "Phenotype",
                        "ALTERATION_ASSOCIATED_WITH_PHENOTYPE",
                        layer="structured",
                        evidence_type="structured_database",
                        study_design="curated_database",
                        species="human",
                        population_or_model=str(r.get("trait_set", "")),
                        context=str(r.get("germline_classification", "")),
                        reference=str(r.get("accession", "")),
                        reference_type="ClinVar accession",
                        source_database="ClinVar",
                        notes="Trait text matched to the study phenotype vocabulary; verbatim trait kept in population_or_model.",
                    )
                )
                break
    log.info("ClinVar evidence rows: %s (%s variants)", len(rows), len(df))
    return rows


def reactome_evidence() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    path = config.DATA_PROCESSED / "reactome_gene_pathway_edges.csv"
    if not path.exists():
        log.warning("Reactome output not found; skipping")
        return [], []
    df = pd.read_csv(path)
    df = df[df["pathway_name"].astype(str).str.lower().apply(lambda x: any(k in x for k in PATHWAY_KEYWORDS))]
    rows = []
    for _, r in df.iterrows():
        rows.append(
            build.make_evidence(
                f"GENE:{r['gene_symbol']}", "Gene", f"PATH:{r['st_id']}", "Pathway",
                "GENE_PARTICIPATES_IN_PATHWAY",
                layer="structured",
                evidence_type="structured_database",
                study_design="curated_database",
                species="human",
                context=str(r.get("pathway_name", "")),
                reference=str(r.get("st_id", "")),
                reference_type="Reactome pathway",
                source_database="Reactome",
                notes=f"FDR={r.get('fdr', '')}",
            )
        )
    log.info("Reactome evidence rows after developmental filter: %s (of %s)", len(rows), len(pd.read_csv(path)))
    return rows, df.to_dict("records")


def inferred_pathway_process(pathway_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    mapping_rows = []
    seen = set()
    for r in pathway_rows:
        name = str(r["pathway_name"]).lower()
        hits = {proc for kw, proc in PROCESS_KEYWORD_MAP if kw in name}
        for proc in hits:
            if (r["st_id"], proc) in seen:
                continue
            seen.add((r["st_id"], proc))
            rows.append(
                build.make_evidence(
                    f"PATH:{r['st_id']}", "Pathway", proc, "Process",
                    "PATHWAY_REGULATES_PROCESS",
                    layer="inferred",
                    evidence_type="indirect",
                    study_design="in_silico",
                    species="human",
                    context=f"Keyword mapping of Reactome pathway '{r['pathway_name']}'",
                    reference=r["st_id"],
                    reference_type="Reactome pathway",
                    source_database="GraphAmbiCardio rule-based mapping",
                    notes="INFERRED: pathway name keyword -> developmental process; not manually verified per pathway.",
                )
            )
            mapping_rows.append({"st_id": r["st_id"], "pathway_name": r["pathway_name"], "process_id": proc})
    write_csv(config.DATA_PROCESSED / "inferred_pathway_process_map.csv", mapping_rows)
    log.info("inferred pathway->process edges: %s", len(rows))
    return rows


def local_indicators(evidence: list[dict[str, Any]]) -> list[dict[str, Any]]:
    extra_nodes = [
        {
            "node_id": "POP:CAMPOS",
            "label": "Resident population, Campos dos Goytacazes",
            "type": "Population",
            "subtype": "",
            "identifiers": "IBGE:330100",
            "description": "Municipality of residence; ecological exposure assignment.",
            "source": "study",
        },
        {
            "node_id": "PERIOD:2010-2025",
            "label": "2010-2025",
            "type": "Period",
            "subtype": "",
            "identifiers": "",
            "description": "Epidemiological study period.",
            "source": "study",
        },
        {
            "node_id": "IND:SINASC_CHD",
            "label": "SINASC CHD cases / 10,000 live births",
            "type": "Indicator",
            "subtype": "prevalence_at_birth",
            "identifiers": "",
            "description": "Annual CHD cases reported in SINASC for resident live births; severe under-ascertainment documented.",
            "source": "SINASC",
        },
        {
            "node_id": "IND:SIH_CHD",
            "label": "SIH CHD admissions (primary diagnosis)",
            "type": "Indicator",
            "subtype": "hospital_admissions",
            "identifiers": "",
            "description": "AIHs of residents with primary diagnosis Q20-Q28; not incidence and not unique individuals.",
            "source": "SIH/SUS",
        },
        {
            "node_id": "IND:ERA5_TMAX",
            "label": "ERA5-Land daily maximum temperature (Campos)",
            "type": "Indicator",
            "subtype": "area_level_climate",
            "identifiers": "",
            "description": "Gridded reanalysis for the municipality, 2010-2025.",
            "source": "Open-Meteo / ERA5-Land",
        },
    ]
    for ind, target in (("IND:SINASC_CHD", "CHD:ALL"), ("IND:SIH_CHD", "CHD:ALL")):
        evidence.append(
            build.make_evidence(
                ind, "Indicator", target, "Phenotype",
                "INDICATOR_DESCRIBES_PHENOTYPE",
                layer="ecological",
                evidence_type="direct_human",
                study_design="ecological",
                species="human",
                population_or_model="Campos dos Goytacazes, RJ",
                exposure_window="",
                context="Local administrative health information system",
                reference="SINASC" if "SINASC" in ind else "SIH/SUS",
                reference_type="Brazilian health information system",
                source_database="DATASUS",
                notes="Ecological indicator; see reports for coverage and under-ascertainment.",
            )
        )
    evidence.append(
        build.make_evidence(
            "IND:ERA5_TMAX", "Indicator", "POP:CAMPOS", "Population",
            "ECOLOGICAL_CONTEXT_FOR",
            layer="ecological",
            evidence_type="structured_database",
            study_design="ecological",
            species="human",
            population_or_model="Campos dos Goytacazes, RJ",
            context="Area-level exposure series (no personal exposure)",
            reference="ERA5-Land",
            reference_type="reanalysis dataset",
            source_database="Open-Meteo / ERA5-Land",
            notes="Ecological exposure proxy; not individual exposure.",
        )
    )
    return extra_nodes


def hypothesis_edges(evidence: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Exposure -> process 2-hop paths that were never directly tested."""
    pairs = set()
    for e in evidence:
        if e["relation"] == "EXPOSURE_MODULATES_MECHANISM" and e["layer"] == "observed":
            for f in evidence:
                if f["relation"] == "MECHANISM_INTERFERES_WITH_PROCESS" and f["source_id"] == e["target_id"]:
                    pairs.add((e["source_id"], f["target_id"]))
    direct = {(e["source_id"], e["target_id"]) for e in evidence if e["layer"] == "observed"}
    rows = []
    for src, tgt in sorted(pairs - direct):
        rows.append(
            build.make_evidence(
                src, "Exposure", tgt, "Process",
                "HYPOTHESIS_LINK",
                layer="hypothesis",
                evidence_type="hypothesis",
                study_design="in_silico",
                species="",
                context="Generated by composing observed exposure->mechanism and mechanism->process edges",
                reference="GraphAmbiCardio inference",
                reference_type="rule",
                source_database="GraphAmbiCardio",
                notes="HYPOTHESIS: no direct study of this exposure on this process was retained.",
            )
        )
    log.info("hypothesis edges: %s", len(rows))
    return rows


def main() -> None:
    curated, anchors = curated_evidence()
    structured = hpo_evidence() + clinvar_evidence()
    reactome_rows, pathway_rows = reactome_evidence()
    structured += reactome_rows
    inferred = inferred_pathway_process(pathway_rows)

    extra_nodes = [n for n in local_indicators(curated) if n]
    hyp = hypothesis_edges(curated)

    gene_meta = read_csv(config.DATA_PROCESSED / "ncbi_gene_metadata.csv") if (config.DATA_PROCESSED / "ncbi_gene_metadata.csv").exists() else []
    nodes = build.gene_nodes(gene_meta) + build.pathway_nodes(pathway_rows) + extra_nodes
    # enrich HPO-only gene nodes with NCBI IDs when the annotation file provides one
    hpo_gene_ids = {}
    hpo_path = config.DATA_PROCESSED / "hpo_gene_phenotype_edges.csv"
    if hpo_path.exists():
        for r in read_csv(hpo_path):
            hpo_gene_ids.setdefault(r["gene_symbol"], r.get("ncbi_gene_id", ""))
    for n in nodes:
        if n["type"] == "Gene" and not n.get("identifiers"):
            gid = hpo_gene_ids.get(n["node_id"].split(":", 1)[1], "")
            if gid:
                n["identifiers"] = f"NCBI:{gid}"
    known = {n["node_id"] for n in nodes}
    for sym, gid in sorted(hpo_gene_ids.items()):
        nid = f"GENE:{sym}"
        if nid not in known:
            nodes.append({
                "node_id": nid, "label": sym, "type": "Gene", "subtype": "",
                "identifiers": f"NCBI:{gid}" if gid else "", "description": "",
                "source": "HPO genes_to_phenotype.txt",
            })
    node_map = {n["node_id"]: n for n in nodes}
    node_map["CHD:ALL"] = {
        "node_id": "CHD:ALL",
        "label": "Congenital heart defects (all Q20-Q28, aggregate)",
        "type": "Phenotype",
        "subtype": "aggregate",
        "identifiers": "ICD10:Q20-Q28",
        "description": "Aggregate phenotype used when a study reports overall CHD rather than a subtype.",
        "source": "study_ontology",
    }
    nodes = list(node_map.values())

    evidence = curated + structured + inferred + hyp
    G, nodes_out, relations = build.build(evidence, nodes)

    # Hypothesis layer: gene-set overlap candidates (explicitly non-evidential).
    hyp_candidates, _, _ = hypotheses.generate()
    if hyp_candidates:
        evidence = evidence + hyp_candidates
        G, nodes_out, relations = build.build(evidence, nodes)

    # exports
    nx.write_graphml(G, config.GRAPH_OUT / "graph.graphml")
    data = nx.node_link_data(G, edges="edges")
    write_json(config.GRAPH_OUT / "graph.json", data)
    write_json(config.GRAPH_OUT / "graph_summary.json", {
        "generated_at": today(),
        "n_nodes": G.number_of_nodes(),
        "n_edges": G.number_of_edges(),
        "nodes_by_type": {t: sum(1 for n in G.nodes if G.nodes[n]["type"] == t) for t in sorted({G.nodes[n]["type"] for n in G.nodes})},
        "edges_by_layer": {l: sum(1 for u, v, k, d in G.edges(keys=True, data=True) if d.get("layer") == l) for l in sorted({d.get("layer") for _, _, _, d in G.edges(keys=True, data=True)})},
        "edges_by_relation": {r: sum(1 for _, _, _, d in G.edges(keys=True, data=True) if d.get("relation") == r) for r in sorted({d.get("relation") for _, _, _, d in G.edges(keys=True, data=True)})},
    })
    log.info("exports written to %s", config.GRAPH_OUT)


if __name__ == "__main__":
    main()
