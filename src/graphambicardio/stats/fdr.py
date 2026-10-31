"""Benjamini-Hochberg FDR control.

All inferential p-values produced by the study are adjusted with BH. Descriptive
counts (bibliometric matrices, annual case counts) are not hypothesis tests and
therefore carry no p-value.
"""

from __future__ import annotations

from typing import Iterable

from statsmodels.stats.multitest import multipletests


def bh_fdr(pvalues: Iterable[float]) -> list[float]:
    p = [float(x) for x in pvalues]
    if not p:
        return []
    return [float(q) for q in multipletests(p, method="fdr_bh")[1]]
