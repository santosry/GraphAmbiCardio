"""Integration: assemble the provenance-first evidence table and build the graph.

Steps
-----
1. Verify every curated quote against the PubMed abstract or the archived CAPES
   abstract (hard fail), including the reviewed batch rows.
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
from graphambicardio.curation import batch_review, seed_edges  # noqa: E402
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


def _capes_abstract(reference: str) -> dict[str, Any]:
    """Load the locally archived CAPES/Sucupira abstract for a thesis."""
    capes_id = reference.split(":")[-1]
    path = config.CURATED / "capes_abstracts" / f"{capes_id}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def verify_quotes(edges: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    pmids = sorted({e["reference"] for e in edges if e.get("reference_type") == "PMID"})
    studies = {s.pmid: s for s in efetch(pmids)} if pmids else {}
    missing = []
    for e in edges:
        ref_type = e.get("reference_type", "PMID")
        if e.get("quote_source") == "full_text":
            archive_path = config.CURATED / (e.get("quote_archive") or "")
            try:
                payload = json.loads(archive_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                missing.append((e.get("reference", ""), f"full-text archive unavailable: {exc}"))
                continue
            if _norm(e.get("quote", "")) != _norm(payload.get("quote", "")):
                missing.append((e.get("reference", ""), "full-text quote differs from archive"))
                continue
            authors = str(payload.get("authors", ""))
            e["_study"] = {
                "pmid": e.get("reference", ""),
                "title": payload.get("title", ""),
                "journal": payload.get("journal", ""),
                "year": str(payload.get("year", "")),
                "doi": payload.get("doi", ""),
                "first_author": authors.split(",")[0].strip() if authors else "",
                "url": payload.get("pubmed_url", "") or f"https://pubmed.ncbi.nlm.nih.gov/{e.get('reference', '')}/",
                "source_database": "PubMed/MEDLINE (full-text curation, reviewed)",
                "reference": e.get("reference", ""),
                "reference_type": ref_type,
            }
            continue
        if ref_type == "PMID":
            s = studies.get(e["reference"])
            abstract = s.abstract if s else ""
            meta = {
                "pmid": s.pmid if s else "",
                "title": s.title if s else "",
                "journal": s.journal if s else "",
                "year": s.year if s else "",
                "doi": s.doi if s else "",
                "first_author": s.first_author if s else "",
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{s.pmid}/" if s else "",
                "source_database": "PubMed/MEDLINE (manual curation)",
            }
        elif ref_type == "CAPES thesis":
            try:
                local = _capes_abstract(e["reference"])
                abstract = local["abstract"]
                meta = {
                    "pmid": "",
                    "title": local["title"],
                    "journal": f"{local['degree']}, {local['institution']}",
                    "year": local["year"],
                    "doi": "",
                    "first_author": local["author"],
                    "url": local["source_url"],
                    "source_database": "CAPES Catálogo de Teses e Dissertações",
                }
            except (OSError, KeyError, json.JSONDecodeError) as exc:
                abstract = ""
                meta = {}
                log.error("CAPES abstract unavailable for %s: %s", e["reference"], exc)
        else:
            abstract = ""
            meta = {}
            log.error("unsupported reference type: %s", ref_type)
        if not abstract:
            missing.append((e["reference"], "source abstract not retrieved"))
            continue
        if _norm(e["quote"]) not in _norm(abstract):
            missing.append((e["reference"], e["quote"][:80]))
            continue
        e["_study"] = {
            **meta,
            "reference": e["reference"],
            "reference_type": ref_type,
        }
    if missing:
        for m in missing:
            log.error("quote verification failed: %s | %s", m[0], m[1])
        raise SystemExit(f"quote verification failed for {len(missing)} edge(s)")
    n_non_pmid = sum(1 for e in edges if e.get("reference_type") != "PMID")
    log.info("verified %s curated quotes across %s PMIDs and %s non-PMID edges", len(edges), len(pmids), n_non_pmid)
    return studies


EXPOSURE_LABEL = {e["id"]: e["label"] for e in config.EXPOSURES}
PHENOTYPE_LABEL = {p["id"]: p["label"] for p in config.PHENOTYPES}


def batch_evidence() -> list[dict[str, Any]]:
    """Evidence promoted from the exhaustive screening via reviewed batch curation.

    Automatic extraction only produces candidates. This function accepts rows
    that a reviewer marked ``verified`` in ``batch_chd_review.csv`` and rejects
    the run when the review file is inconsistent. Every quote is still verified
    verbatim against the PubMed abstract by :func:`verify_quotes`.
    """
    queue_path = config.CURATED / "batch_chd_queue.csv"
    review_path = config.CURATED / "batch_chd_review.csv"
    if not queue_path.exists() or not review_path.exists():
        log.warning("batch curation files not found; skipping")
        return []
    queue = read_csv(queue_path)
    reviews = batch_review.load_reviews(review_path)
    # Verified rows may come from anchor studies that are not in the candidate
    # queue, or from full-text reading. Add minimal metadata rows for them so the
    # generic resolver can attach title, journal, year and DOI.
    known = {str(row.get("pmid", "")).strip() for row in queue}
    missing = sorted({
        key[0] for key, review in reviews.items()
        if review.get("review_status") == "verified" and key[0] and key[0] not in known
    })
    if missing:
        anchors = {str(row.get("pmid", "")).strip(): row for row in read_csv(config.CURATED / "anchor_studies.csv")}
        metadata_path = config.CURATED / "fulltext_metadata.csv"
        metadata = {row["pmid"]: row for row in read_csv(metadata_path)} if metadata_path.exists() else {}
        studies = {s.pmid: s for s in efetch(missing)}
        for pmid in missing:
            anchor = anchors.get(pmid, {})
            meta = metadata.get(pmid, {})
            study = studies.get(pmid)
            queue.append({
                "pmid": pmid,
                "title": anchor.get("title") or meta.get("title") or (study.title if study else ""),
                "journal": anchor.get("journal") or meta.get("journal") or (study.journal if study else ""),
                "year": str(anchor.get("year") or meta.get("year") or (study.year if study else "")),
                "doi": anchor.get("doi") or meta.get("doi") or (study.doi if study else ""),
                "candidate_exposures": "",
                "candidate_phenotypes": "",
            })
    issues = batch_review.review_issues(reviews.values(), queue)
    if issues:
        for issue in issues:
            log.error("batch review: %s", issue)
        raise SystemExit(f"batch review failed with {len(issues)} issue(s)")

    edges: list[dict[str, Any]] = []
    for row in batch_review.resolved_rows(reviews, queue):
        evidence = seed_edges.edge(
            row["exposure_id"], "Exposure", row["phenotype_id"], "Phenotype",
            "EXPOSURE_ASSOCIATED_WITH_PHENOTYPE",
            ev=row.get("evidence_type") or "direct_human",
            design=row.get("study_design") or "unknown",
            species=row.get("species") or "human",
            quote=row["quote"],
            reference=row["pmid"],
            reference_type="PMID",
            population=row.get("population_or_model", ""),
            window=row.get("exposure_window", ""),
            direction=row.get("effect_direction", ""),
            context=(
                "Batch CHD curation (AI-assisted extraction, reviewed): "
                f"{row.get('exposure_label') or EXPOSURE_LABEL.get(row['exposure_id'], row['exposure_id'])} and "
                f"{row.get('phenotype_label') or PHENOTYPE_LABEL.get(row['phenotype_id'], row['phenotype_id'])}"
            ),
            notes=(
                "AI-assisted extraction from the PubMed abstract; reviewed by "
                f"{row.get('reviewed_by', 'a reviewer')} on {row.get('reviewed_at', '')}. "
                f"Review note: {row.get('review_note', '')}"
            ),
        )
        source = row.get("quote_source") or "abstract"
        evidence["quote_source"] = source
        evidence["quote_archive"] = row.get("quote_archive", "")
        evidence["source_database"] = (
            "PubMed/MEDLINE (full-text curation, reviewed)"
            if source == "full_text"
            else "PubMed/MEDLINE (AI-assisted batch curation, reviewed)"
        )
        if source == "full_text":
            evidence["notes"] = (
                "AI-assisted full-text extraction; complete article not retained. "
                f"Reviewed by {row.get('reviewed_by', 'a reviewer')} on {row.get('reviewed_at', '')}. "
                f"Quote archive: {row.get('quote_archive', '')}. "
                f"Review note: {row.get('review_note', '')}"
            )
        edges.append(evidence)
    n_rejected = sum(1 for item in reviews.values() if item.get("review_status") == "rejected")
    log.info("batch curation: %s verified edges, %s rejected candidates", len(edges), n_rejected)
    return edges


def curated_evidence() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    edges = (
        seed_edges.EXPOSURE_PHENOTYPE
        + seed_edges.EXPOSURE_MECHANISM
        + seed_edges.MECHANISM_PROCESS
        + seed_edges.PROCESS_PHENOTYPE
        + seed_edges.GENE_PHENOTYPE
        + seed_edges.ADDITIONAL_EDGES
        + seed_edges.CAPES_THESIS_EDGES
        + batch_evidence()
    )
    verify_quotes(edges)
    rows = []
    studies = {}
    for e in edges:
        st = e.pop("_study")
        studies[st["reference"]] = st
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
                reference_type=e["reference_type"],
                source_database=e.get("source_database") or st["source_database"],
                retrieved_at=today(),
                notes=e.get("notes", ""),
                quote_source=e.get("quote_source", "abstract"),
                quote_archive=e.get("quote_archive", ""),
            )
        )
    anchor_rows = []
    for ref, s in sorted(studies.items()):
        anchor_rows.append(
            {
                "pmid": s["pmid"],
                "title": s["title"],
                "year": s["year"],
                "journal": s["journal"],
                "first_author": s["first_author"],
                "doi": s["doi"],
                "doi_url": f"https://doi.org/{s['doi']}" if s["doi"] else "",
                "pubmed_url": s["url"] if s["reference_type"] == "PMID" else "",
                "reference": ref,
                "reference_type": s["reference_type"],
                "url": s["url"],
                "source_database": s["source_database"],
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
            "label": "SINASC Q20–Q26 cases / 1,000 live births",
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
            "node_id": "IND:PM25_VIGIAR",
            "label": "PM2.5 anual (VIGIAR/MS)",
            "type": "Indicator",
            "subtype": "area_level_air_quality",
            "identifiers": "",
            "description": "Série anual de PM2.5 para Campos dos Goytacazes obtida do VIGIAR (Ministério da Saúde) via pacote vigiar; 2010-2025.",
            "source": "VIGIAR / vigiar",
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
            "IND:PM25_VIGIAR", "Indicator", "POP:CAMPOS", "Population",
            "ECOLOGICAL_CONTEXT_FOR",
            layer="ecological",
            evidence_type="structured_database",
            study_design="ecological",
            species="human",
            population_or_model="Campos dos Goytacazes, RJ",
            context="Série anual de PM2.5 de área (VIGIAR/MS), 2010-2025",
            reference="VIGIAR",
            reference_type="Brazilian health information system",
            source_database="VIGIAR / vigiar",
            notes="Exposição de área, não individual; usada no painel e nos modelos exploratórios.",
        )
    )
    evidence.append(
        build.make_evidence(
            "EXP:PM25", "Exposure", "IND:PM25_VIGIAR", "Indicator",
            "ECOLOGICAL_CONTEXT_FOR",
            layer="ecological",
            evidence_type="structured_database",
            study_design="ecological",
            species="human",
            population_or_model="Campos dos Goytacazes, RJ",
            context="Ligação entre o nó conceitual PM2.5 e a série local do VIGIAR",
            reference="VIGIAR",
            reference_type="Brazilian health information system",
            source_database="VIGIAR / vigiar",
            notes="Contexto ecológico; não é uma aresta de efeito.",
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
        "label": "Malformações congênitas do aparelho circulatório (agregado de estudos)",
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
