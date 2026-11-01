"""Hypothesis-generation layer (explicitly non-evidential).

Two complementary, documented rules are used:

1. **Composition** (already produced in the build script): exposure -> mechanism
   plus mechanism -> process implies a candidate exposure -> process link.
2. **Gene-set overlap** (this module): a canonical gene set for a mechanism is
   intersected with the genes annotated to a phenotype.  A large overlap
   prioritises a candidate exposure -> phenotype hypothesis, but it is **not**
   evidence that the exposure causes the phenotype.

Statistical design (v0.4)
--------------------------
* The test family is fixed *before* candidate selection: every observed
  exposure -> mechanism edge is crossed with every phenotype that has HPO
  annotations, for every mechanism with a canonical seed set.
* The hypergeometric universe is the set of genes with at least one HPO
  phenotype annotation.  Seed genes outside this universe are ineligible.
* Benjamini-Hochberg FDR is applied to the **entire family**, not to a
  pre-selected top-40 list.
* A size-matched permutation p-value is reported as a sensitivity analysis for
  annotation-size effects; it is not used to select candidates.
* Candidate tables are a prioritisation output.  They never enter path or
  centrality analyses.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

import networkx as nx
import numpy as np
from scipy.stats import hypergeom

from .. import config
from ..io_utils import get_logger, read_csv, write_csv, write_json
from ..stats.fdr import bh_fdr
from . import build

log = get_logger("hypotheses")

# Canonical seed gene sets (biological knowledge, NOT evidence for any exposure).
MECH_GENES = {
    "MECH:OXSTRESS": ["NFE2L2", "KEAP1", "HMOX1", "SOD1", "SOD2", "CAT", "GPX1", "TXN", "TXNRD1", "NQO1"],
    "MECH:INFLAM": ["IL6", "TNF", "IL1B", "CRP", "NFKB1", "NLRP3", "IL10", "CCL2"],
    "MECH:EPIGEN": ["DNMT1", "DNMT3A", "DNMT3B", "HDAC1", "HDAC2", "KMT2A", "EZH2", "TET1", "TET2"],
    "MECH:MITO": ["SIRT3", "PPARGC1A", "TFAM", "NDUFS1", "SDHA", "UQCRC2", "ATP5F1A"],
    "MECH:WNT": ["CTNNB1", "AXIN2", "LEF1", "TCF7L2", "GSK3B", "APC", "RSPO2", "WNT3A"],
    "MECH:AHR": ["AHR", "ARNT", "CYP1A1", "CYP1B1", "AHRR"],
    "MECH:RA_SIGNAL": ["RARA", "RARB", "ALDH1A2", "CYP26A1", "RBP1", "CRABP2"],
    "MECH:HDAC": ["HDAC1", "HDAC2", "HDAC3", "HDAC4", "HDAC5"],
    "MECH:HYPOXIA": ["HIF1A", "EPAS1", "VHL", "EGLN1", "EGLN2"],
    "MECH:NEURAL_CREST": ["SOX10", "PAX3", "SNAI2", "TWIST1", "FOXD3", "TFAP2A", "EDNRB"],
    "MECH:HEATSHOCK": ["HSPA1A", "HSPA1B", "HSP90AA1", "HSF1", "HSPB1"],
    "MECH:APOPTOSIS": ["BAX", "BCL2", "CASP3", "CASP8", "TP53", "BAK1"],
    "MECH:PROLIF": ["CCND1", "CDKN1A", "MYC", "MKI67", "CDK4"],
    "MECH:CELLSIG": ["NOTCH1", "JAG1", "BMP4", "FGF8", "TGFB1", "SMAD4"],
    "MECH:GENE_EXPR": ["GATA4", "NKX2-5", "TBX5", "MEF2C", "HAND2", "TBX20"],
    "MECH:ENDOTHELIAL": ["VEGFA", "FLT4", "KDR", "PECAM1", "CDH5"],
}

# Traceable origin of each canonical set (pathway/GO membership, not a PMID claim).
MECH_GENE_SOURCES = {
    "MECH:OXSTRESS": "Canonical NRF2/ARE oxidative-stress response genes (GO:0006979; KEGG/Reactome antioxidant pathways).",
    "MECH:INFLAM": "Canonical inflammatory cytokines and inflammasome genes (GO:0006954; KEGG cytokine signalling).",
    "MECH:EPIGEN": "Canonical DNA-methylation and histone-modification enzymes (GO:0006306, GO:0016570).",
    "MECH:MITO": "Canonical mitochondrial biogenesis and respiratory-chain genes (GO:0007005; Reactome respiratory electron transport).",
    "MECH:WNT": "Canonical Wnt/beta-catenin signalling genes (GO:0016055; Reactome Wnt signalling).",
    "MECH:AHR": "Canonical aryl-hydrocarbon receptor signalling genes (GO:0001666; Reactome AHR pathway).",
    "MECH:RA_SIGNAL": "Canonical retinoic-acid synthesis, transport and receptor genes (GO:0002138; Reactome retinoid metabolism).",
    "MECH:HDAC": "Canonical histone deacetylase genes (GO:0016575; Reactome HDAC activity).",
    "MECH:HYPOXIA": "Canonical hypoxia-inducible factor and oxygen-sensing genes (GO:0001666; Reactome HIF signalling).",
    "MECH:NEURAL_CREST": "Canonical neural-crest specification and migration genes (GO:0014032; Reactome neural crest development).",
    "MECH:HEATSHOCK": "Canonical heat-shock protein and HSF1 response genes (GO:0009408; Reactome HSF1 activation).",
    "MECH:APOPTOSIS": "Canonical intrinsic/extrinsic apoptosis genes (GO:0006915; Reactome apoptosis).",
    "MECH:PROLIF": "Canonical cell-cycle and proliferation genes (GO:0008283; Reactome cell cycle).",
    "MECH:CELLSIG": "Canonical Notch/BMP/FGF/TGF-beta developmental signalling genes (GO:0007219, GO:0030509).",
    "MECH:GENE_EXPR": "Canonical cardiac transcription factors (GO:0045165; Reactome heart development).",
    "MECH:ENDOTHELIAL": "Canonical endothelial and angiogenic genes (GO:0001525; Reactome VEGF signalling).",
}

MIN_OVERLAP = 2
MAX_CANDIDATES = 40
N_PERMUTATIONS = 1000
RANDOM_SEED = 20261031


def _phenotype_genes() -> dict[str, set[str]]:
    genes: dict[str, set[str]] = defaultdict(set)
    path = config.DATA_PROCESSED / "hpo_gene_phenotype_edges.csv"
    if path.exists():
        for r in read_csv(path):
            genes[r["phenotype_id"]].add(r["gene_symbol"].upper())
    for r in read_csv(config.GRAPH_OUT / "relations.csv"):
        if r["relation"] == "GENE_ASSOCIATED_WITH_PHENOTYPE" and r["target_type"] == "Phenotype":
            genes[r["target_id"]].add(r["source_id"].split(":", 1)[1].upper())
    return genes


def _permutation_p(
    observed_overlap: int,
    seed: set[str],
    n_pheno: int,
    universe: set[str],
    rng: np.random.Generator,
    n_perm: int,
) -> float:
    """Size-matched permutation p-value for one overlap test."""
    if not seed or n_pheno <= 0 or not universe:
        return 1.0
    universe_arr = np.array(sorted(universe))
    seed_mask = np.isin(universe_arr, np.array(sorted(seed)))
    n_draw = min(n_pheno, len(universe_arr))
    hits = 0
    for _ in range(n_perm):
        draw = rng.choice(len(universe_arr), size=n_draw, replace=False)
        if int(seed_mask[draw].sum()) >= observed_overlap:
            hits += 1
    return (1 + hits) / (1 + n_perm)


def generate() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    relations = read_csv(config.GRAPH_OUT / "relations.csv")
    pheno_genes = _phenotype_genes()
    universe = set().union(*pheno_genes.values()) if pheno_genes else set()
    universe_size = len(universe)

    exp_mech: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in relations:
        if r["layer"] == "observed" and r["relation"] == "EXPOSURE_MODULATES_MECHANISM":
            exp_mech[r["source_id"]].append(r)
    direct = {
        (r["source_id"], r["target_id"])
        for r in relations
        if r["relation"] == "EXPOSURE_ASSOCIATED_WITH_PHENOTYPE"
    }

    # Complete pre-specified family: exposure x mechanism x phenotype.
    family: list[dict[str, Any]] = []
    for exp, mech_edges in exp_mech.items():
        for ph, genes in pheno_genes.items():
            if (exp, ph) in direct:
                continue
            n_pheno = len(genes)
            for mech_edge in mech_edges:
                mech = mech_edge["target_id"]
                seed_all = {g.upper() for g in MECH_GENES.get(mech, [])}
                seed = seed_all & universe
                if not seed or not n_pheno or not universe_size:
                    continue
                overlap = sorted(seed & genes)
                k = len(overlap)
                p_hyper = float(hypergeom.sf(k - 1, universe_size, n_pheno, len(seed)))
                family.append(
                    {
                        "exposure_id": exp,
                        "phenotype_id": ph,
                        "mechanism_id": mech,
                        "n_overlap": k,
                        "phenotype_genes": n_pheno,
                        "mechanism_genes": len(seed),
                        "mechanism_genes_seed_total": len(seed_all),
                        "universe_genes": universe_size,
                        "gene_set_fraction": round(k / len(seed), 3) if seed else 0.0,
                        "overlap_genes": ";".join(overlap[:20]),
                        "supporting_reference": mech_edge.get("references", ""),
                        "mechanism_gene_source": MECH_GENE_SOURCES.get(mech, ""),
                        "p_hyper": p_hyper,
                        "missing_link": (
                            f"Nenhuma aresta documentada de {mech} para um processo/fenótipo "
                            "específico; a sobreposição gênica é apenas priorização."
                        ),
                    }
                )

    # FDR across the complete family, before any overlap/ranking filter.
    qvals = bh_fdr([r["p_hyper"] for r in family])
    for r, q in zip(family, qvals):
        r["q_fdr"] = round(float(q), 6)
        r["fdr_significant"] = bool(q < 0.05)
        r["family_size"] = len(family)

    # Permutation sensitivity across all tests with the minimum overlap.
    eligible = [r for r in family if r["n_overlap"] >= MIN_OVERLAP]
    rng = np.random.default_rng(RANDOM_SEED)
    for r in eligible:
        seed = {g.upper() for g in MECH_GENES.get(r["mechanism_id"], [])} & universe
        r["p_perm"] = _permutation_p(
            r["n_overlap"], seed, r["phenotype_genes"], universe, rng, N_PERMUTATIONS
        )
    q_perm = bh_fdr([r["p_perm"] for r in eligible])
    for r, q in zip(eligible, q_perm):
        r["q_perm_bh"] = round(float(q), 6)
        r["perm_significant"] = bool(q < 0.05)

    eligible.sort(
        key=lambda r: (
            r["q_fdr"],
            -r["n_overlap"],
            -r["gene_set_fraction"],
            r["exposure_id"],
            r["phenotype_id"],
            r["mechanism_id"],
        )
    )
    candidates = eligible[:MAX_CANDIDATES]
    for c in candidates:
        c["priority"] = (
            "alta" if c["n_overlap"] >= 4 else ("média" if c["n_overlap"] == 3 else "baixa")
        )

    # Write the complete family for auditability, plus the prioritised table.
    family_fields = [
        "exposure_id", "phenotype_id", "mechanism_id", "n_overlap", "phenotype_genes",
        "mechanism_genes", "mechanism_genes_seed_total", "universe_genes",
        "gene_set_fraction", "overlap_genes", "supporting_reference", "p_hyper",
        "q_fdr", "fdr_significant", "family_size", "p_perm", "q_perm_bh",
        "perm_significant", "mechanism_gene_source", "missing_link",
    ]
    write_csv(config.TABLES / "hypothesis_family.csv", family, fieldnames=family_fields)
    write_csv(config.TABLES / "hypothesis_candidates.csv", candidates)

    # Gene-level provenance table for the canonical mechanism sets.
    gene_rows = []
    for mech, genes in MECH_GENES.items():
        for g in genes:
            gene_rows.append(
                {
                    "mechanism_id": mech,
                    "gene_symbol": g,
                    "in_hpo_universe": g.upper() in universe,
                    "source": MECH_GENE_SOURCES.get(mech, ""),
                }
            )
    write_csv(config.TABLES / "mechanism_gene_sets.csv", gene_rows)

    evidence_rows: list[dict[str, Any]] = []
    for c in candidates:
        ev = build.make_evidence(
            c["exposure_id"], "Exposure", c["phenotype_id"], "Phenotype",
            "HYPOTHESIS_CANDIDATE",
            layer="hypothesis",
            evidence_type="hypothesis",
            study_design="in_silico",
            species="",
            population_or_model="gene-set overlap with HPO phenotype annotations",
            context=(
                f"mechanism={c['mechanism_id']}; overlap={c['n_overlap']} genes "
                f"({c['gene_set_fraction']:.2f} of the seed set in the HPO universe)"
            ),
            reference="GraphAmbiCardio gene-overlap rule",
            reference_type="rule",
            source_database="GraphAmbiCardio",
            notes=(
                c["missing_link"]
                + f" Hypergeometric p={c['p_hyper']:.3g}; BH q={c['q_fdr']:.3g}; "
                + f"permutation p={c.get('p_perm', float('nan')):.3g}; "
                + f"BH q(perm)={c.get('q_perm_bh', float('nan')):.3g}. "
                + f"Supporting documented edge references: {c['supporting_reference']}"
            ),
        )
        evidence_rows.append(ev)

    # Candidate paths that reach a process but lack a process -> phenotype edge.
    observed = [r for r in relations if r["layer"] == "observed"]
    G = nx.DiGraph()
    for r in observed:
        if r["source_type"] in {"Exposure", "Mechanism", "Process", "Phenotype"} and r["target_type"] in {"Exposure", "Mechanism", "Process", "Phenotype"}:
            G.add_edge(r["source_id"], r["target_id"], **r)
    has_pheno = {e["source_id"] for e in observed if e["relation"] == "ALTERATION_ASSOCIATED_WITH_PHENOTYPE"}
    path_rows = []
    for exp in [e["id"] for e in config.EXPOSURES]:
        if exp not in G:
            continue
        for proc in [p for p, _ in config.PROCESSES]:
            if proc not in G or proc in has_pheno:
                continue
            if nx.has_path(G, exp, proc):
                for path in nx.all_simple_paths(G, exp, proc, cutoff=5):
                    path_rows.append({
                        "exposure_id": exp,
                        "process_id": proc,
                        "path": " -> ".join(path),
                        "n_steps": len(path) - 1,
                        "missing_link": f"{proc} -> fenótipo específico (não demonstrado)",
                    })
    write_csv(config.GRAPH_OUT / "hypotheses.csv", evidence_rows, fieldnames=build.EVIDENCE_FIELDS)
    write_csv(config.TABLES / "candidate_paths_missing_link.csv", path_rows)
    write_json(config.REPORTS / "hypothesis_summary.json", {
        "n_family_tests": len(family),
        "n_overlap_ge2": len(eligible),
        "n_candidates_reported": len(candidates),
        "n_fdr_significant": int(sum(1 for c in candidates if c.get("fdr_significant"))),
        "n_fdr_significant_in_family": int(sum(1 for r in family if r.get("fdr_significant"))),
        "n_perm_significant_in_eligible": int(sum(1 for r in eligible if r.get("perm_significant"))),
        "universe_genes": universe_size,
        "universe_definition": "union of genes with at least one HPO phenotype annotation",
        "min_overlap": MIN_OVERLAP,
        "max_candidates_reported": MAX_CANDIDATES,
        "n_permutations": N_PERMUTATIONS,
        "n_candidate_paths": len(path_rows),
        "rule": "full exposure x mechanism x phenotype family; hypergeometric test with HPO universe; BH-FDR across the family; size-matched permutation sensitivity",
        "warning": "Hypotheses are not evidence. They are excluded from all path and centrality analyses.",
        "annotation_bias_note": "Permutation uses size-matched random gene sets from the HPO universe; residual annotation bias may remain because HPO coverage differs across phenotypes.",
    })
    log.info(
        "hypothesis family: %s tests; %s with overlap>=2; %s reported; %s FDR-significant",
        len(family), len(eligible), len(candidates), sum(1 for r in family if r.get("fdr_significant")),
    )
    return evidence_rows, candidates, path_rows
