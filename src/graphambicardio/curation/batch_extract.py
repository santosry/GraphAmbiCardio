"""Deterministic clause-level extraction for batch literature curation.

The functions here are deliberately pure and offline: they take an abstract
sentence and a set of vocabulary hits and decide whether the sentence states
one exposure, one congenital heart defect phenotype and one explicit effect
size. Network access and file handling live in ``scripts/curation``.

Design decisions that keep the extraction honest:

* Effect anchors are matched case-sensitively for abbreviations (``OR``,
  ``aOR``, ``RR`` ...), so the English word "or" is never read as an odds
  ratio.
* The text between the anchor and the number may contain connector words but
  no digits, no percent signs and no ``p =`` markers. This rejects
  ``OR 1st trimester=3.96`` and p-value fragments.
* The number must look like an effect size (0 < value < 100). Values such as
  ``95`` followed by ``%`` are rejected as confidence-interval bounds.
* Ambiguous phenotype abbreviations (``ASD``) need cardiac context.
* A clause must mention exactly one phenotype of the full vocabulary and
  exactly one candidate exposure. Multi-phenotype result sentences are sent to
  human review instead of being assigned to the first phenotype that matches.
"""
from __future__ import annotations

import re
from typing import Any, Iterable

from ..literature.screen import PHENOTYPE_PATTERNS as _SCREEN_PHENOTYPES

# ---------------------------------------------------------------------------
# Vocabulary patterns used to confirm a candidate inside a clause.
# ---------------------------------------------------------------------------
EXPOSURE_PATTERNS: dict[str, str] = {
    "EXP:PM25": r"\bpm\s*2[.,]?5\b|fine particulate|particulate matter\s*2[.,]?5",
    "EXP:PM10": r"\bpm\s*10\b|particulate matter\s*10",
    "EXP:NO2": r"\bno2\b|nitrogen dioxide|nitrogen oxides|traffic[- ]related air",
    "EXP:O3": r"\bo3\b|ozone",
    "EXP:CO": r"carbon monoxide",
    "EXP:HEAT": r"\bheat\b|high temperature|ambient temperature|hot temperature|heatwave|heat wave",
    "EXP:HUMIDITY": r"humidity|relative humidity",
    "EXP:PEST": r"pesticid|agrochemical|agricultural chemical|organophosphate|herbicide|insecticide",
    "EXP:SOLV": r"\bsolvents?\b",
    "EXP:METALS": (
        r"\bmetals?\b(?:[^.;]{0,40}\b(?:exposure|level|levels|concentration|"
        r"concentrations|mixture|mixtures|burden)\b)?|"
        r"\b(?:lead|mercury|arsenic|cadmium|manganese|chromium)\b"
        r"(?=\s*(?:exposure|level|levels|concentration|concentrations|"
        r"in\s+(?:blood|urine|hair|serum|plasma)|poisoning|contamination|biomarkers?))"
    ),
    "EXP:SMOKE": r"smok|tobacco|cigarette",
    "EXP:ALCOHOL": r"alcohol|ethanol",
    "EXP:VPA": r"valproi|valproate",
    "EXP:DIOXIN": r"dioxin|tcdd|\bpcb",
}

# Exposures that are not part of the project vocabulary but appear in the same
# sentence. They are used to reject an effect that belongs to another exposure
# (for example, phthalates next to heavy metals).
COMPETING_EXPOSURES: dict[str, str] = {
    "OTHER:PHTHALATE": r"phthalat",
    "OTHER:ALKYLPHENOL": r"alkylphenol",
    "OTHER:BISPHENOL": r"bisphenol|\bbpa\b",
    "OTHER:PFAS": r"\bpfas\b|perfluor",
    "OTHER:ORGANIC_SOLVENT": r"benzen|toluene|xylene|trichloroethylene",
    "OTHER:ANESTHETIC": r"anesthetic|anaesthetic",
}

# Extra patterns for phenotype mentions that the screening vocabulary spells out
# less often. They are *unioned* with the screening patterns, never used as a
# replacement, so "ventricular septal defect" and "PmVSD" are both detected.
PHENOTYPE_PATTERNS_EXTRA: dict[str, str] = {
    "CHD:COA": r"\bcoa\b|coarctation",
    "CHD:TGA": r"\btga\b|transposition of the great|levo-transposition",
    "CHD:VSD": r"pmvsd|perimembranous vsd",
    "CHD:ASD": r"s-asd|secundum asd",
    "CHD:PS": r"pulmonary (?:artery and )?(?:valve )?stenosis|pulmonary artery and valve defect|pulmonic stenosis",
    "CHD:AVSD": r"\bavsd\b|atrioventricular septal|av canal",
    "CHD:TAPVC": r"\btapvc\b|total anomalous pulmonary venous",
    "CHD:TRUNCUS": r"truncus arteriosus|common arterial trunk",
}

# Vocabulary patterns usually end in a word boundary. Allow a plural "s"
# before that boundary so "ventricular septal defects" is not missed.
PLURAL_TAIL = ")" + chr(92) + "b"


def pluralise(pattern: str) -> str:
    if pattern.endswith(PLURAL_TAIL):
        return pattern[: -len(PLURAL_TAIL)] + ")s?" + chr(92) + "b"
    return pattern


def merge_phenotype_patterns() -> dict[str, str]:
    merged: dict[str, str] = {}
    for pid in set(_SCREEN_PHENOTYPES) | set(PHENOTYPE_PATTERNS_EXTRA):
        parts = [
            pluralise(part)
            for part in (_SCREEN_PHENOTYPES.get(pid), PHENOTYPE_PATTERNS_EXTRA.get(pid))
            if part
        ]
        merged[pid] = "(?:" + "|".join(parts) + ")"
    return merged


PHENOTYPE_PATTERNS_ALL = merge_phenotype_patterns()

# ---------------------------------------------------------------------------
# Effect-size anchors
# ---------------------------------------------------------------------------
# Abbreviations are matched case-sensitively. The lookarounds stop matches
# inside words such as "ORs" or "PRES".
_ABBREV = (
    r"(?<![A-Za-z])(?:aOR|AOR|aRR|ARR|aHR|AHR|aPR|APR|OR|RR|HR|PR)(?![A-Za-z])"
)
# Spelled-out names are case-insensitive because abstracts use sentence case.
_SPELLED = r"(?i:\b(?:odds ratio|risk ratio|hazard ratio|prevalence ratio|relative risk)s?\b)"
ANCHOR = f"(?:{_ABBREV}|{_SPELLED})"

EFFECT_RE = re.compile(
    r"(?P<anchor>" + ANCHOR + r")"
    # Lazy bridge from the anchor to the number. Digits are rejected below, so
    # "OR 1st trimester=3.96" cannot be captured as "OR 1".
    r"(?P<gap>[^.;\n]{0,48}?)"
    r"(?P<value>\d+(?:[.,]\d+)?)(?![\w])"
)

MAX_GAP_WORDS = 6
_CLAUSE_SPLIT = re.compile(r"(?<=[.!?])\s+|;\s*")
_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")

# Terms that make a short gap acceptable between anchor and value, e.g.
# "OR for high versus low = 1.14".
_GAP_FORBIDDEN = re.compile(r"\d|%|\bci\b|\bp\s*[=<>~]", re.I)


def normalise(text: str) -> str:
    """Collapse whitespace and unify dashes for verbatim comparisons."""
    text = (text or "").replace("\u2013", "-").replace("\u2014", "-").replace("\u2212", "-")
    return _WS_RE.sub(" ", text).strip()


def split_clauses(text: str) -> list[str]:
    """Split an abstract into sentences and semicolon clauses."""
    text = _TAG_RE.sub(" ", text or "")
    text = _WS_RE.sub(" ", text).strip()
    return [part.strip() for part in _CLAUSE_SPLIT.split(text) if len(part.strip()) >= 30]


def _gap_ok(gap: str) -> bool:
    if _GAP_FORBIDDEN.search(gap):
        return False
    return len(re.findall(r"[A-Za-z]+", gap)) <= MAX_GAP_WORDS


def iter_effects(clause: str):
    """Yield every usable effect size found in a clause."""
    for match in EFFECT_RE.finditer(clause):
        gap = match.group("gap")
        if not _gap_ok(gap):
            continue
        # Reject confidence-interval bounds such as "95%" and "0.03" inside
        # "p = 0.03" (the p-value case is already caught by the gap rule).
        end = match.end()
        if end < len(clause) and clause[end] == "%":
            continue
        raw = match.group("value").replace(",", ".")
        try:
            value = float(raw)
        except ValueError:
            continue
        if not 0.0 < value < 100.0:
            continue
        yield {
            "anchor": match.group("anchor"),
            "gap": normalise(gap),
            "value": value,
            "text": normalise(clause[match.start():end]),
            "start": match.start(),
            "end": end,
            "direction": "inverse" if value < 1.0 else "positive",
        }


def find_effect(clause: str) -> dict[str, Any] | None:
    """Return the first usable effect size in a clause, or ``None``.

    The returned ``text`` is the verbatim slice from the anchor to the number,
    and ``direction`` is ``"inverse"`` when the value is below 1.
    """
    return next(iter_effects(clause), None)


def _phenotype_present(pid: str, clause: str, patterns: dict[str, str]) -> bool:
    pattern = patterns.get(pid) or PHENOTYPE_PATTERNS_ALL.get(pid)
    if not pattern:
        return False
    pattern = pluralise(pattern)
    if not re.search(pattern, clause, re.I):
        return False
    if pid == "CHD:ASD" and not re.search(r"heart|cardiac|septal|atrial", clause, re.I):
        return False
    return True


def phenotypes_in_clause(
    clause: str,
    vocabulary: Iterable[str],
    patterns: dict[str, str],
) -> list[str]:
    """All phenotypes of the vocabulary mentioned in the clause."""
    return [pid for pid in vocabulary if _phenotype_present(pid, clause, patterns)]


def exposures_in_clause(clause: str, candidates: Iterable[str]) -> list[str]:
    """Candidate exposures confirmed in the clause."""
    found = []
    for exp in candidates:
        pattern = EXPOSURE_PATTERNS.get(exp)
        if pattern and re.search(pattern, clause, re.I):
            found.append(exp)
    return found


def extract_clause(
    clause: str,
    candidate_exposures: Iterable[str],
    candidate_phenotypes: Iterable[str],
    phenotype_vocabulary: Iterable[str],
    phenotype_patterns: dict[str, str],
    *,
    require_link: bool = True,
) -> dict[str, Any] | None:
    """Strict single-exposure, single-phenotype, single-effect extraction.

    Returns ``None`` when the clause is ambiguous. Ambiguity is a feature: the
    row goes to human review with a reason instead of producing a wrong edge.
    """
    effect = find_effect(clause)
    if effect is None:
        return None
    if require_link and not re.search(
        r"\b(associat|risk|odds|increased|decreased|higher|lower|excess|relation|related)",
        clause,
        re.I,
    ):
        return None

    exposures = exposures_in_clause(clause, candidate_exposures)
    if len(exposures) != 1:
        return None

    all_phenotypes = phenotypes_in_clause(clause, phenotype_vocabulary, phenotype_patterns)
    if len(all_phenotypes) != 1:
        return None
    phenotype = all_phenotypes[0]
    if phenotype not in set(candidate_phenotypes):
        return None

    return {
        "exposure_id": exposures[0],
        "phenotype_id": phenotype,
        "effect": effect,
    }
