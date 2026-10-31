"""Fase A: feasibility matrix construction.

The matrix combines (i) bibliometric volume retrieved from PubMed for every
exposure x phenotype pair, (ii) automated triage signals from the retrieved
records, and (iii) the availability of structured data.  The automated
classification is explicitly labelled ``provisional``; the interpretive
report (docs/01_SCIENTIFIC_VIABILITY.md) is based on manual reading of the
anchor studies listed in literature/curated/.
"""

from __future__ import annotations

from typing import Any

from .. import config
from ..io_utils import get_logger, read_csv, write_csv, write_json
from .pubmed import esearch, search_and_fetch
from .screen import screen_record

log = get_logger("feasibility")

MECHANISM_UMBRELLAS = {
    "MECH:OXSTRESS": '"oxidative stress"',
    "MECH:INFLAM": '"inflammation"',
    "MECH:EPIGEN": '"epigenetic*" OR "DNA methylation"',
    "MECH:MITO": '"mitochondrial dysfunction" OR "mitochondria"',
    "MECH:CELLSIG": '"signal transduction" OR "signalling pathway" OR "signaling pathway"',
    "MECH:GENE_EXPR": '"gene expression"',
}


def volume_class(n: int) -> str:
    if n == 0:
        return "no_direct_literature"
    if n <= 2:
        return "sparse"
    if n <= 7:
        return "limited"
    if n <= 19:
        return "moderate"
    return "high"


def pair_query(exposure_terms: list[str], phenotype: dict[str, Any]) -> str:
    exp = "(" + " OR ".join(exposure_terms) + ")"
    chd = (
        '("congenital heart"[tiab] OR "congenital heart disease*"[tiab] OR '
        '"heart defects, congenital"[MeSH] OR "cardiac malformation*"[tiab])'
    )
    pheno_terms = config.PHENOTYPE_QUERY_TERMS[phenotype["id"]]
    pheno = "(" + " OR ".join(pheno_terms) + ")"
    # Context block: keeps the pair query anchored to prenatal/developmental
    # exposure rather than to adult cardiac disease or to clinical management.
    context = (
        '(pregnan*[tiab] OR maternal[tiab] OR prenatal[tiab] OR teratogen*[tiab] OR '
        '"birth defect*"[tiab] OR embry*[tiab] OR "in utero"[tiab])'
    )
    return f"{exp} AND {chd} AND {pheno} AND {context}"


def build_pair_matrix(retmax: int = 15, save: bool = True) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for exposure in config.EXPOSURES:
        for phenotype in config.PHENOTYPES:
            q = pair_query(exposure["query_terms"], phenotype)
            res = esearch(q, retmax=retmax)
            n = res["count"]
            screened = []
            if res["pmids"]:
                rec = search_and_fetch(
                    f"pair_{exposure['id'].split(':')[1]}_{phenotype['id'].split(':')[1]}",
                    q,
                    retmax=min(retmax, n),
                    save=save,
                )
                screened = [screen_record(s) for s in rec["studies"]]
            n_human = sum(1 for s in screened if s["species_human"])
            n_animal = sum(1 for s in screened if s["species_animal"])
            n_cell = sum(1 for s in screened if s["species_cell"])
            n_mech = sum(1 for s in screened if s["mechanisms"])
            n_window = sum(1 for s in screened if s["window_terms"])
            n_review = sum(1 for s in screened if s["is_review"])
            mech_terms = sorted({m for s in screened for m in s["mechanisms"].split(";") if m})
            rows.append(
                {
                    "exposure_id": exposure["id"],
                    "exposure": exposure["label"],
                    "phenotype_id": phenotype["id"],
                    "phenotype": phenotype["label"],
                    "cid10": ";".join(phenotype["cid10"]),
                    "n_pubmed": n,
                    "volume_class": volume_class(n),
                    "n_screened": len(screened),
                    "n_triage_human": n_human,
                    "n_triage_animal": n_animal,
                    "n_triage_cell": n_cell,
                    "n_triage_mechanism": n_mech,
                    "n_triage_exposure_window": n_window,
                    "n_triage_review": n_review,
                    "mechanism_terms_found": ";".join(mech_terms),
                    "provisional_class": _provisional_class(n, n_human, n_animal, n_cell, n_mech),
                    "query": q,
                    "retrieved_at": res["retrieved_at"],
                }
            )
            log.info("%s x %s: %s", exposure["id"], phenotype["id"], n)
    if save:
        write_csv(config.REPORTS / "feasibility_pair_matrix.csv", rows)
        write_json(config.REPORTS / "feasibility_pair_matrix.json", rows)
    return rows


def _provisional_class(n: int, n_human: int, n_animal: int, n_cell: int, n_mech: int) -> str:
    if n == 0:
        return "E_no_direct_literature"
    if n_human >= 3 and n >= 8:
        return "B_direct_human_literature_present"
    if n_human >= 1 and n >= 3:
        return "C_mixed_human_and_experimental"
    if n_animal or n_cell:
        return "D_experimental_only"
    if n_mech:
        return "D_association_with_mechanistic_terms"
    return "D_association_only"


def exposure_mechanism_counts() -> list[dict[str, Any]]:
    rows = []
    for exposure in config.EXPOSURES:
        exp = "(" + " OR ".join(exposure["query_terms"]) + ")"
        for mech_id, mech_q in MECHANISM_UMBRELLAS.items():
            q = f"{exp} AND ({mech_q}) AND (heart OR cardiac OR cardiogenesis OR embry* OR pregnancy OR placenta*)"
            res = esearch(q, retmax=0)
            rows.append(
                {
                    "exposure_id": exposure["id"],
                    "exposure": exposure["label"],
                    "mechanism_id": mech_id,
                    "n_pubmed": res["count"],
                    "volume_class": volume_class(res["count"]),
                    "query": q,
                    "retrieved_at": res["retrieved_at"],
                }
            )
            log.info("%s x %s: %s", exposure["id"], mech_id, res["count"])
    write_csv(config.REPORTS / "feasibility_exposure_mechanism_counts.csv", rows)
    return rows


def domain_counts() -> list[dict[str, Any]]:
    from .pubmed import domain_queries

    rows = []
    for name, q in domain_queries().items():
        rec = search_and_fetch(name, q, retmax=100)
        screened = [screen_record(s) for s in rec["studies"]]
        rows.append(
            {
                "domain": name,
                "query": q,
                "count_total": rec["count_total"],
                "retrieved_n": rec["retrieved_n"],
                "n_human": sum(s["species_human"] for s in screened),
                "n_animal": sum(s["species_animal"] for s in screened),
                "n_cell": sum(s["species_cell"] for s in screened),
                "n_review": sum(s["is_review"] for s in screened),
                "n_with_mechanism": sum(bool(s["mechanisms"]) for s in screened),
                "retrieved_at": rec["retrieved_at"],
            }
        )
    write_csv(config.REPORTS / "feasibility_domain_counts.csv", rows)
    return rows


def exposure_summary() -> list[dict[str, Any]]:
    """Aggregate the pair matrix per exposure (how many phenotypes have any evidence)."""
    rows = read_csv(config.REPORTS / "feasibility_pair_matrix.csv")
    out = []
    for exposure in config.EXPOSURES:
        sub = [r for r in rows if r["exposure_id"] == exposure["id"]]
        if not sub:
            continue
        out.append(
            {
                "exposure_id": exposure["id"],
                "exposure": exposure["label"],
                "n_pairs_with_evidence": sum(int(r["n_pubmed"]) > 0 for r in sub),
                "total_records": sum(int(r["n_pubmed"]) for r in sub),
                "pairs_with_human_triage": sum(int(r["n_triage_human"]) > 0 for r in sub),
                "pairs_experimental_only": sum(
                    int(r["n_pubmed"]) > 0 and int(r["n_triage_human"]) == 0 for r in sub
                ),
            }
        )
    write_csv(config.REPORTS / "feasibility_exposure_summary.csv", out)
    return out
