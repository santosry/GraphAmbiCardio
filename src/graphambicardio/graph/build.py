"""Knowledge-graph construction with explicit provenance.

Design
------
Two tabular layers are produced:

* ``outputs/graph/evidence.csv`` - one row per (source, target, relation,
  study/reference).  Multiple evidence rows can support the same relation; the
  original studies are never collapsed.
* ``outputs/graph/relations.csv`` - one row per unique relation, with
  aggregated evidence counts, evidence-type mix and a pre-registered
  confidence score.

The graph is exported to GraphML and JSON.  Three evidence layers are kept
separate and are never mixed in the analyses:

* ``observed``    - relation directly investigated/documented in a retrieved source
* ``structured``  - curated database annotation (HPO, ClinVar, Reactome)
* ``inferred``    - derived by documented composition rules (marked)
* ``hypothesis``  - plausible but not demonstrated (kept out of the core graph)
"""

from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict
from typing import Any, Iterable

import networkx as nx

from .. import config
from ..io_utils import get_logger, read_csv, today, write_csv, write_json

log = get_logger("graph_build")

NODE_TYPES = {
    "Exposure",
    "Chemical",
    "ClimateVariable",
    "Mechanism",
    "Gene",
    "Pathway",
    "Process",
    "Phenotype",
    "Variant",
    "Indicator",
    "Population",
    "Period",
    "Study",
    "DataSource",
}

RELATIONS = {
    "EXPOSURE_ASSOCIATED_WITH_PHENOTYPE",
    "EXPOSURE_MODULATES_MECHANISM",
    "MECHANISM_INTERFERES_WITH_PROCESS",
    "MECHANISM_MODULATES_MECHANISM",
    "GENE_ASSOCIATED_WITH_PHENOTYPE",
    "GENE_PARTICIPATES_IN_PATHWAY",
    "PATHWAY_REGULATES_PROCESS",
    "VARIANT_IN_GENE",
    "ALTERATION_ASSOCIATED_WITH_PHENOTYPE",
    "INDICATOR_DESCRIBES_PHENOTYPE",
    "ECOLOGICAL_CONTEXT_FOR",
    "HYPOTHESIS_LINK",
    "HYPOTHESIS_CANDIDATE",
    "STUDY_DOCUMENTS_RELATION",
    "PROCESS_ORIGINATES_STRUCTURE",
}

EVIDENCE_FIELDS = [
    "evidence_id",
    "edge_key",
    "source_id",
    "source_type",
    "target_id",
    "target_type",
    "relation",
    "layer",
    "evidence_type",
    "study_design",
    "species",
    "population_or_model",
    "exposure_window",
    "effect_direction",
    "context",
    "quote",
    "reference",
    "reference_type",
    "source_database",
    "retrieved_at",
    "notes",
]


def evidence_id(*parts: str) -> str:
    return "EV:" + hashlib.sha1("|".join(parts).encode("utf-8")).hexdigest()[:16]


def make_evidence(
    source_id: str,
    source_type: str,
    target_id: str,
    target_type: str,
    relation: str,
    *,
    layer: str = "observed",
    evidence_type: str = "direct_human",
    study_design: str = "unknown",
    species: str = "human",
    population_or_model: str = "",
    exposure_window: str = "",
    effect_direction: str = "",
    context: str = "",
    quote: str = "",
    reference: str = "",
    reference_type: str = "PMID",
    source_database: str = "",
    retrieved_at: str | None = None,
    notes: str = "",
) -> dict[str, Any]:
    assert source_type in NODE_TYPES, source_type
    assert target_type in NODE_TYPES, target_type
    assert relation in RELATIONS, relation
    assert layer in {"observed", "structured", "inferred", "hypothesis", "ecological"}
    edge_key = f"{source_id}|{relation}|{target_id}"
    return {
        "evidence_id": evidence_id(edge_key, reference, evidence_type, population_or_model),
        "edge_key": edge_key,
        "source_id": source_id,
        "source_type": source_type,
        "target_id": target_id,
        "target_type": target_type,
        "relation": relation,
        "layer": layer,
        "evidence_type": evidence_type,
        "study_design": study_design,
        "species": species,
        "population_or_model": population_or_model,
        "exposure_window": exposure_window,
        "effect_direction": effect_direction,
        "context": context,
        "quote": quote,
        "reference": reference,
        "reference_type": reference_type,
        "source_database": source_database,
        "retrieved_at": retrieved_at or today(),
        "notes": notes,
    }


def edge_confidence(evs: list[dict[str, Any]]) -> tuple[float, str, dict[str, Any]]:
    """Pre-registered confidence aggregation (see docs/06_EVIDENCE_GRADING.md)."""
    if not evs:
        return 0.0, "E", {}
    type_w = [config.EVIDENCE_TYPES.get(e["evidence_type"], {"weight": 0.2})["weight"] for e in evs]
    design_w = [config.STUDY_DESIGN_WEIGHTS.get(e.get("study_design", "unknown"), 0.3) for e in evs]
    # Weighted combination: the evidence type (directness) dominates, the study
    # design modulates it.  A pure product double-penalises strong animal
    # experiments and is not used.
    strengths = [0.7 * t + 0.3 * d for t, d in zip(type_w, design_w)]
    base = min(0.9, max(strengths))
    # independent references (a reference is counted once per edge)
    refs = {e.get("reference") for e in evs if e.get("reference")}
    n_refs = len(refs) if refs else 1
    replication = min(0.15, 0.05 * max(0, n_refs - 1))
    single_study_penalty = 0.05 if n_refs <= 1 else 0.0
    species = {e.get("species", "") for e in evs}
    concordance = 0.05 if ("human" in species and any(s in species for s in ("mouse", "rat", "zebrafish", "chick", "xenopus", "cell"))) else 0.0
    contradiction = 0.10 if any("contradict" in (e.get("notes", "") + e.get("effect_direction", "")).lower() for e in evs) else 0.0
    non_significant = 0.10 if any(
        k in (e.get("effect_direction", "") + " " + e.get("notes", "")).lower()
        for e in evs for k in ("non-significant", "non significant", "marginal", "null")
    ) else 0.0
    conf = max(0.0, min(0.95, base + replication + concordance - contradiction - single_study_penalty - non_significant))
    grade = "A" if conf >= 0.88 else "B" if conf >= 0.72 else "C" if conf >= 0.55 else "D" if conf >= 0.4 else "E"
    detail = {
        "base_strength": round(base, 3),
        "replication_bonus": round(replication, 3),
        "species_concordance_bonus": round(concordance, 3),
        "contradiction_penalty": round(contradiction, 3),
        "non_significance_penalty": round(non_significant, 3),
        "single_study_penalty": round(single_study_penalty, 3),
        "n_references": n_refs,
    }
    return round(conf, 3), grade, detail


TIER_LABELS = {
    "estabelecida": "Bem sustentada",
    "plausivel_experimental": "Plausível (experimental)",
    "nao_demonstrada": "Não demonstrada",
    "contextual": "Contextual",
    "inferida": "Inferida (regra)",
}


def evidence_tier(layer: str, grade: str, evidence_types: str) -> str:
    """Three-level evidence hierarchy required by the study design.

    * estabelecida: direct human association or replicated human genetics (A/B)
    * plausivel_experimental: experimental support (C) or indirect synthesis of experiments
    * nao_demonstrada: D/E, hypothesis, or only an inferred rule
    * contextual: ecological/context variables (humidity, indicators)
    """
    types = set((evidence_types or "").split(";"))
    if layer == "ecological":
        return "contextual"
    if layer == "hypothesis":
        return "nao_demonstrada"
    if layer == "inferred":
        return "inferida"
    if layer == "structured":
        return "estabelecida" if grade in {"A", "B", "C"} else "nao_demonstrada"
    if grade in {"A", "B"} and ({"direct_human", "structured_database"} & types):
        return "estabelecida"
    if grade == "C" and ({"experimental_human", "experimental_animal", "experimental_cell"} & types):
        return "plausivel_experimental"
    return "nao_demonstrada"


def aggregate(evidence: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_edge: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for e in evidence:
        by_edge[e["edge_key"]].append(e)
    rows = []
    for key, evs in by_edge.items():
        first = evs[0]
        conf, grade, detail = edge_confidence(evs)
        rows.append(
            {
                "edge_id": "EDGE:" + hashlib.sha1(key.encode()).hexdigest()[:12],
                "edge_key": key,
                "source_id": first["source_id"],
                "source_type": first["source_type"],
                "target_id": first["target_id"],
                "target_type": first["target_type"],
                "relation": first["relation"],
                "layer": first["layer"],
                "n_evidence": len(evs),
                "n_references": len({e.get("reference") for e in evs if e.get("reference")}),
                "evidence_types": ";".join(sorted({e["evidence_type"] for e in evs})),
                "species": ";".join(sorted({e.get("species", "") for e in evs if e.get("species")})),
                "study_designs": ";".join(sorted({e.get("study_design", "") for e in evs if e.get("study_design")})),
                "confidence": conf,
                "grade": grade,
                "evidence_tier": evidence_tier(
                    first["layer"], grade, ";".join(sorted({e["evidence_type"] for e in evs}))
                ),
                "evidence_tier_label": TIER_LABELS[
                    evidence_tier(first["layer"], grade, ";".join(sorted({e["evidence_type"] for e in evs})))
                ],
                "confidence_detail": json.dumps(detail),
                "references": ";".join(sorted({e.get("reference", "") for e in evs if e.get("reference")})),
                "source_database": ";".join(sorted({e.get("source_database", "") for e in evs if e.get("source_database")})),
                "retrieved_at": max(e["retrieved_at"] for e in evs),
            }
        )
    return sorted(rows, key=lambda r: (r["layer"], -r["confidence"], r["edge_key"]))


# --------------------------------------------------------------------------
# Node construction
# --------------------------------------------------------------------------
def base_nodes() -> list[dict[str, Any]]:
    nodes = []
    for e in config.EXPOSURES:
        nodes.append(
            {
                "node_id": e["id"],
                "label": e["label"],
                "type": "Exposure",
                "subtype": e["class"],
                "identifiers": "",
                "description": e["local_relevance"],
                "source": "study_ontology",
            }
        )
    for ph in config.PHENOTYPES:
        nodes.append(
            {
                "node_id": ph["id"],
                "label": ph["label"],
                "type": "Phenotype",
                "subtype": ph["category"],
                "identifiers": f"ICD10:{';'.join(ph['cid10'])};HPO:{ph['hpo']}",
                "description": ph.get("mapping_note", ""),
                "source": "study_ontology",
            }
        )
    for mid, label in config.MECHANISMS:
        nodes.append(
            {
                "node_id": mid,
                "label": label,
                "type": "Mechanism",
                "subtype": "",
                "identifiers": "",
                "description": "",
                "source": "study_ontology",
            }
        )
    for pid, label in config.PROCESSES:
        nodes.append(
            {
                "node_id": pid,
                "label": label,
                "type": "Process",
                "subtype": "cardiac_development",
                "identifiers": "",
                "description": "",
                "source": "study_ontology",
            }
        )
    return nodes


def gene_nodes(gene_meta: list[dict[str, str]]) -> list[dict[str, Any]]:
    out = []
    for g in gene_meta:
        gid = g.get("ncbi_gene_id") or ""
        out.append(
            {
                "node_id": f"GENE:{g.get('symbol', '')}",
                "label": g.get("symbol", ""),
                "type": "Gene",
                "subtype": "",
                "identifiers": f"NCBI:{gid}" if gid else "",
                "description": g.get("description", ""),
                "source": "NCBI Gene",
            }
        )
    return out


def pathway_nodes(pathways: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = {}
    for p in pathways:
        seen[p["st_id"]] = {
            "node_id": f"PATH:{p['st_id']}",
            "label": p["pathway_name"],
            "type": "Pathway",
            "subtype": "Reactome",
            "identifiers": f"Reactome:{p['st_id']}",
            "description": "",
            "source": "Reactome",
        }
    return list(seen.values())


def build(
    evidence: list[dict[str, Any]],
    extra_nodes: list[dict[str, Any]] | None = None,
) -> tuple[nx.MultiDiGraph, list[dict[str, Any]], list[dict[str, Any]]]:
    nodes = {n["node_id"]: n for n in base_nodes()}
    for n in extra_nodes or []:
        nodes.setdefault(n["node_id"], n)
    relations = aggregate(evidence)
    # add nodes referenced by evidence that are not in the base vocabulary
    for ev in evidence:
        for side, typ in (("source", ev["source_type"]), ("target", ev["target_type"])):
            nid = ev[f"{side}_id"]
            if nid not in nodes:
                nodes[nid] = {
                    "node_id": nid,
                    "label": nid.split(":", 1)[-1],
                    "type": typ,
                    "subtype": "",
                    "identifiers": nid.split(":", 1)[1] if nid.startswith("VAR:") else "",
                    "description": "",
                    "source": ev.get("source_database", ""),
                }

    G = nx.MultiDiGraph()
    for n in nodes.values():
        G.add_node(n["node_id"], **n)
    for r in relations:
        G.add_edge(
            r["source_id"],
            r["target_id"],
            key=r["edge_id"],
            relation=r["relation"],
            layer=r["layer"],
            confidence=r["confidence"],
            grade=r["grade"],
            n_evidence=r["n_evidence"],
            evidence_tier=r["evidence_tier"],
            references=r["references"],
        )
    write_csv(config.GRAPH_OUT / "nodes.csv", list(nodes.values()))
    write_csv(config.GRAPH_OUT / "relations.csv", relations)
    write_csv(config.GRAPH_OUT / "evidence.csv", evidence, fieldnames=EVIDENCE_FIELDS)
    write_json(config.GRAPH_OUT / "graph_metadata.json", {
        "study_version": config.STUDY_VERSION,
        "ontology_version": config.ONTOLOGY_VERSION,
        "built_at": today(),
        "n_nodes": len(nodes),
        "n_relations": len(relations),
        "n_evidence_rows": len(evidence),
        "layers": {l: sum(1 for r in relations if r["layer"] == l) for l in sorted({r["layer"] for r in relations})},
    })
    log.info("graph built: %s nodes, %s relations, %s evidence rows", len(nodes), len(relations), len(evidence))
    return G, list(nodes.values()), relations
