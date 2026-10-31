"""Rule-based triage of retrieved records.

This module performs *automated triage only*.  It extracts signals that help a
human reviewer prioritise records (species, design, exposure window, mechanism
vocabulary, phenotype vocabulary).  It does **not** assign final evidence
grades; those require manual reading (see ``curation/seed_edges.py`` and the
audit files in ``reports/``).
"""

from __future__ import annotations

import re
from typing import Any

SPECIES_PATTERNS = {
    "human": r"\b(infant|newborn|neonat|child|children|pregnan|maternal|mother|women|cohort|case-control|registry|birth)\b",
    "mouse": r"\b(mouse|mice|murine)\b",
    "rat": r"\b(rat|rats)\b",
    "zebrafish": r"\bzebrafish\b",
    "chick": r"\b(chick|avian|chicken)\b",
    "xenopus": r"\bxenopus\b",
    "cell": r"\b(in vitro|cell line|hela|hek293|ipsc|stem cell|explants?)\b",
    "organoid": r"\borganoid",
}

DESIGN_PATTERNS = {
    "meta_analysis": r"\b(meta-analys|pooled analys)",
    "systematic_review": r"\bsystematic review\b",
    "cohort": r"\b(cohort|prospective|longitudinal)\b",
    "case_control": r"\bcase[- ]control\b",
    "registry": r"\b(registry|surveillance|national database|birth defects? surveillance)\b",
    "cross_sectional": r"\bcross[- ]sectional\b",
    "ecological": r"\becologic(al)?\b",
    "animal_in_vivo": r"\b(in vivo|animal model|knockout mice|transgenic mice)\b",
    "in_vitro": r"\b(in vitro|cell culture|cultured cells)\b",
}

WINDOW_PATTERNS = {
    "periconception": r"\b(periconception|periconceptional|around conception)\b",
    "first_trimester": r"\b(first trimester|1st trimester|early pregnancy|gestational week[s]? [3-8]|weeks? [3-8] of gestation|embryonic period|organogenesis)\b",
    "second_trimester": r"\b(second trimester|2nd trimester)\b",
    "third_trimester": r"\b(third trimester|3rd trimester)\b",
    "whole_pregnancy": r"\b(entire pregnancy|throughout pregnancy|whole pregnancy|during pregnancy)\b",
    "preconception": r"\b(preconception|before conception|pre-pregnan)\b",
}

MECHANISM_PATTERNS = {
    "MECH:OXSTRESS": r"\b(oxidative stress|reactive oxygen|ros\b|lipid peroxidation|glutathione|nrf2)\b",
    "MECH:INFLAM": r"\b(inflammat|cytokine|interleukin|tnf|nf-kappa|nf-\u03bab|crp)\b",
    "MECH:EPIGEN": r"\b(epigenetic|dna methylation|methylation|histone|microrna|mirna|non-coding rna|lncrna)\b",
    "MECH:MITO": r"\b(mitochondri|mitochondrial dysfunction|mtDNA)\b",
    "MECH:CELLSIG": r"\b(signal(l)?ing|pathway|notch|wnt|hedgehog|bmp|fgf|tgf)\b",
    "MECH:GENE_EXPR": r"\b(gene expression|transcriptom|differential expression|rna-seq|mrna)\b",
    "MECH:APOPTOSIS": r"\b(apoptosis|apoptotic|cell death)\b",
    "MECH:PROLIF": r"\b(proliferat|cell cycle)\b",
    "MECH:HEATSHOCK": r"\b(heat shock|hsp70|hsp90|hsf1|proteostasis)\b",
    "MECH:AHR": r"\b(aryl hydrocarbon|ahr\b|tcdd|dioxin)\b",
    "MECH:RA_SIGNAL": r"\b(retinoic acid|retinoid|raldh|cyp26)\b",
    "MECH:WNT": r"\b(wnt|beta-catenin|\u03b2-catenin)\b",
    "MECH:HDAC": r"\b(hdac|histone deacetylase|valproate|valproic)\b",
    "MECH:HYPOXIA": r"\b(hypoxia|hif-1|hif1|hif-2)\b",
    "MECH:NEURAL_CREST": r"\b(neural crest|cardiac crest)\b",
    "MECH:ENDOTHELIAL": r"\b(endothelial|angiogenesis|vasculogenesis)\b",
}

PHENOTYPE_PATTERNS = {
    "CHD:VSD": r"\b(ventricular septal defect|vsd|interventricular septal)\b",
    "CHD:ASD": r"\b(atrial septal defect|asd\b|interatrial septal)\b",
    "CHD:AVSD": r"\b(atrioventricular septal|avsd|av canal|endocardial cushion)\b",
    "CHD:TOF": r"\b(tetralogy of fallot|fallot)\b",
    "CHD:DORV": r"\b(double outlet right ventricle|dorv)\b",
    "CHD:TGA": r"\b(transposition of the great arter|tga\b|d-tga)\b",
    "CHD:HLHS": r"\b(hypoplastic left heart|hlhs)\b",
    "CHD:COA": r"\b(coarctation)\b",
    "CHD:PDA": r"\b(patent ductus|ductus arteriosus)\b",
    "CHD:PS": r"\b(pulmonary (valve )?stenosis|pulmonic stenosis)\b",
    "CHD:AS": r"\b(aortic (valve )?stenosis)\b",
    "CHD:TAPVC": r"\b(total anomalous pulmonary venous|tapvc|tapvr)\b",
    "CHD:TRUNCUS": r"\b(truncus arteriosus|common arterial trunk)\b",
    "CHD:EBSTEIN": r"\b(ebstein)\b",
}


def _flag(text: str, patterns: dict[str, str]) -> dict[str, bool]:
    text = text or ""
    return {k: bool(re.search(v, text, flags=re.I)) for k, v in patterns.items()}


def screen_record(rec: dict[str, Any]) -> dict[str, Any]:
    text = " ".join(
        str(rec.get(k, "")) for k in ("title", "abstract", "mesh_terms", "pubtypes")
    )
    species = _flag(text, SPECIES_PATTERNS)
    design = _flag(text, DESIGN_PATTERNS)
    window = _flag(text, WINDOW_PATTERNS)
    mech = _flag(text, MECHANISM_PATTERNS)
    pheno = _flag(text, PHENOTYPE_PATTERNS)
    review = bool(re.search(r"\b(review|meta-analys|systematic)\b", text, flags=re.I))
    return {
        "pmid": rec.get("pmid", ""),
        "year": rec.get("year", ""),
        "title": rec.get("title", ""),
        "journal": rec.get("journal", ""),
        "species_human": species["human"],
        "species_animal": any(species[k] for k in ("mouse", "rat", "zebrafish", "chick", "xenopus")),
        "species_cell": species["cell"] or species["organoid"],
        "design": ";".join(k for k, v in design.items() if v),
        "window_terms": ";".join(k for k, v in window.items() if v),
        "mechanisms": ";".join(k for k, v in mech.items() if v),
        "phenotypes": ";".join(k for k, v in pheno.items() if v),
        "is_review": review,
        "has_abstract": bool(rec.get("abstract")),
    }
