"""Human Phenotype Ontology retrieval.

Two artefacts are used:
  1. HPO term metadata for the 14 pre-registered CHD phenotypes (API check that
     the identifiers and labels are current).
  2. The HPO gene-to-phenotype annotation release, filtered to the CHD terms.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .. import config
from ..io_utils import get_json, get_logger, http_get, today, write_csv, write_json

log = get_logger("hpo")

GENES_TO_PHENOTYPE_URL = (
    "https://github.com/obophenotype/human-phenotype-ontology/releases/latest/download/genes_to_phenotype.txt"
)
PHENOTYPE_HPOA_URL = (
    "https://github.com/obophenotype/human-phenotype-ontology/releases/latest/download/phenotype.hpoa"
)


def fetch_term_metadata() -> list[dict[str, Any]]:
    rows = []
    for ph in config.PHENOTYPES:
        data = get_json(f"{config.HPO_API}/terms/{ph['hpo']}")
        rows.append(
            {
                "phenotype_id": ph["id"],
                "label_study": ph["label"],
                "cid10": ";".join(ph["cid10"]),
                "hpo_id": ph["hpo"],
                "hpo_label": data.get("name", ""),
                "hpo_definition": data.get("definition", ""),
                "hpo_synonyms": ";".join(data.get("synonyms", []) or []),
                "hpo_xrefs": ";".join(data.get("xrefs", []) or []),
                "retrieved_at": today(),
            }
        )
        log.info("%s -> %s (%s)", ph["id"], data.get("name"), ph["hpo"])
    write_csv(config.DATA_DICTIONARY / "hpo_phenotype_mapping.csv", rows)
    write_json(config.DATA_PROCESSED / "hpo_phenotype_metadata.json", rows)
    return rows


def download_annotations(force: bool = False) -> Path:
    path = config.DATA_RAW / "external" / "genes_to_phenotype.txt"
    if path.exists() and not force:
        return path
    log.info("downloading HPO gene annotations")
    text = http_get(GENES_TO_PHENOTYPE_URL)
    path.write_text(text, encoding="utf-8")
    (config.DATA_RAW / "external" / "genes_to_phenotype.retrieved_at").write_text(today())
    return path


def gene_phenotype_edges() -> list[dict[str, Any]]:
    """Return gene -> CHD phenotype annotations from the HPO release."""
    path = download_annotations()
    targets = {ph["hpo"]: ph for ph in config.PHENOTYPES}
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        header = fh.readline().rstrip("\n").split("\t")
        idx = {name: i for i, name in enumerate(header)}
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < len(header):
                continue
            hpo_id = parts[idx["hpo_id"]]
            if hpo_id not in targets:
                continue
            ph = targets[hpo_id]
            rows.append(
                {
                    "gene_symbol": parts[idx["gene_symbol"]],
                    "ncbi_gene_id": parts[idx["ncbi_gene_id"]],
                    "hpo_id": hpo_id,
                    "hpo_name": parts[idx["hpo_name"]],
                    "frequency": parts[idx["frequency"]],
                    "disease_id": parts[idx["disease_id"]],
                    "phenotype_id": ph["id"],
                    "source": "HPO genes_to_phenotype.txt",
                    "retrieved_at": today(),
                }
            )
    write_csv(config.DATA_PROCESSED / "hpo_gene_phenotype_edges.csv", rows)
    log.info("HPO: %s gene-phenotype annotations for the CHD panel", len(rows))
    return rows
