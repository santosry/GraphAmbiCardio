"""Unit and integrity tests for GraphAmbiCardio."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from graphambicardio.epi import sinasc, sih  # noqa: E402
from graphambicardio.graph.build import edge_confidence, make_evidence  # noqa: E402
from graphambicardio.io_utils import read_csv  # noqa: E402
from graphambicardio.literature.europepmc import to_europepmc_query  # noqa: E402


def test_parse_multiple_icd_codes():
    assert sinasc.parse_icd_codes("Q339Q652") == ["Q339", "Q652"]
    assert sinasc.parse_icd_codes("Q179Q189Q740") == ["Q179", "Q189", "Q740"]
    assert sinasc.chd_codes("Q339Q211") == ["Q211"]
    assert sinasc.chd_codes("Q652") == []
    assert sinasc.chd_codes("Q699") == []
    assert sinasc.chd_codes("Q211") == ["Q211"]
    assert sinasc.chd_codes("Q02X") == []


def test_estimate_conception():
    from datetime import datetime

    c = sinasc.estimate_conception(datetime(2020, 1, 1), 40, "5")
    assert c is not None
    assert (datetime(2020, 1, 1) - c).days == 280
    # fall back to the categorical midpoint when SEMAGESTAC is absent
    c2 = sinasc.estimate_conception(datetime(2020, 1, 1), None, "5")
    assert c2 is not None


def test_age_groups():
    assert sih.age_group(None) == "unknown"
    assert sih.age_group(0.5) == "<1y"
    assert sih.age_group(3) == "1-4y"
    assert sih.age_group(17.9) == "15-17y"
    assert sih.age_group(30) == "18y+"


def test_europepmc_translation():
    assert to_europepmc_query('"PM2.5"[tiab]') == 'TITLE_ABS:"PM2.5"'
    assert (
        to_europepmc_query('"heart defects, congenital"[MeSH]')
        == 'MESH:"heart defects, congenital"'
    )


def _ev(**kw):
    base = dict(
        source_id="EXP:X", source_type="Exposure", target_id="CHD:Y",
        target_type="Phenotype", relation="EXPOSURE_ASSOCIATED_WITH_PHENOTYPE",
        reference="1", species="human", study_design="cohort",
        evidence_type="direct_human",
    )
    base.update(kw)
    return make_evidence(**base)


def test_confidence_ordering():
    human = edge_confidence([_ev()])[0]
    animal = edge_confidence([_ev(evidence_type="experimental_animal", study_design="animal_in_vivo", species="mouse")])[0]
    indirect = edge_confidence([_ev(evidence_type="indirect", study_design="narrative_review")])[0]
    assert human > animal > indirect
    assert 0 <= indirect <= 1 and 0 <= human <= 1


def test_non_significant_penalty():
    sig = edge_confidence([_ev(effect_direction="positive")])[0]
    ns = edge_confidence([_ev(effect_direction="positive but non-significant")])[0]
    assert ns < sig


def test_replication_bonus():
    one = edge_confidence([_ev(reference="1")])[0]
    three = edge_confidence([_ev(reference="1"), _ev(reference="2"), _ev(reference="3")])[0]
    assert three > one


@pytest.mark.skipif(not (ROOT / "outputs" / "graph" / "relations.csv").exists(), reason="graph not built")
def test_graph_integrity():
    nodes = read_csv(ROOT / "outputs" / "graph" / "nodes.csv")
    rels = read_csv(ROOT / "outputs" / "graph" / "relations.csv")
    ids = {n["node_id"] for n in nodes}
    assert len(ids) == len(nodes)
    for r in rels:
        assert r["source_id"] in ids and r["target_id"] in ids
        assert r["source_id"] != r["target_id"]
        assert 0 <= float(r["confidence"]) <= 1
        assert r["grade"] in {"A", "B", "C", "D", "E"}


@pytest.mark.skipif(not (ROOT / "reports" / "feasibility_pair_matrix.csv").exists(), reason="matrix not built")
def test_feasibility_matrix_complete():
    d = read_csv(ROOT / "reports" / "feasibility_pair_matrix.csv")
    assert len(d) == 14 * 14
    assert all(int(r["n_pubmed"]) >= 0 for r in d)


@pytest.mark.skipif(not (ROOT / "outputs" / "tables" / "paths_exposure_phenotype.csv").exists(), reason="paths not built")
def test_paths_do_not_use_hypothesis_layer():
    d = read_csv(ROOT / "outputs" / "tables" / "paths_exposure_phenotype.csv")
    assert all("hypothesis" not in r["layers"] for r in d)
    assert all(float(r["path_confidence_min"]) > 0 for r in d)
