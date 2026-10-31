"""PubMed / MEDLINE retrieval through NCBI E-utilities.

Only official E-utilities endpoints are used.  When ``NCBI_API_KEY`` is set the
request rate is 10 req/s, otherwise 3 req/s (the documented unauthenticated
limit).  Every query, its translation and its count are stored verbatim.
"""

from __future__ import annotations

import json
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from .. import config
from ..io_utils import get_logger, http_get, today, write_json

log = get_logger("pubmed")

BASE = config.PUBMED_BASE
BATCH = 200


@dataclass
class Study:
    pmid: str
    title: str = ""
    journal: str = ""
    year: str = ""
    first_author: str = ""
    doi: str = ""
    abstract: str = ""
    pubtypes: list[str] = field(default_factory=list)
    mesh_terms: list[str] = field(default_factory=list)
    language: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "pmid": self.pmid,
            "title": self.title,
            "journal": self.journal,
            "year": self.year,
            "first_author": self.first_author,
            "doi": self.doi,
            "abstract": self.abstract,
            "pubtypes": ";".join(self.pubtypes),
            "mesh_terms": ";".join(self.mesh_terms),
            "language": self.language,
        }


def _rate_limit() -> None:
    time.sleep(0.11 if config.NCBI_API_KEY else 0.36)


def _ncbi_params(extra: dict[str, Any]) -> dict[str, Any]:
    p = {"tool": config.NCBI_TOOL, "email": config.NCBI_EMAIL}
    if config.NCBI_API_KEY:
        p["api_key"] = config.NCBI_API_KEY
    p.update(extra)
    return p


def esearch(
    query: str,
    retmax: int = 100,
    mindate: str | None = None,
    maxdate: str | None = None,
    datetype: str = "pdat",
    sort: str = "relevance",
    use_cache: bool = True,
) -> dict[str, Any]:
    params = _ncbi_params(
        {
            "db": "pubmed",
            "term": query,
            "retmode": "json",
            "retmax": retmax,
            "sort": sort,
        }
    )
    if mindate:
        params["mindate"] = mindate
        params["maxdate"] = maxdate or "3000"
        params["datetype"] = datetype
    _rate_limit()
    raw = http_get(f"{BASE}/esearch.fcgi", params, cache=use_cache)
    res = json.loads(raw)["esearchresult"]
    return {
        "count": int(res.get("count", 0)),
        "pmids": res.get("idlist", []),
        "query_translation": res.get("querytranslation", ""),
        "query": query,
        "retrieved_at": today(),
        "mindate": mindate,
        "maxdate": maxdate,
        "sort": sort,
    }


def efetch(pmids: Iterable[str], use_cache: bool = True) -> list[Study]:
    pmids = [str(p) for p in pmids]
    studies: list[Study] = []
    for i in range(0, len(pmids), BATCH):
        chunk = pmids[i : i + BATCH]
        params = _ncbi_params({"db": "pubmed", "id": ",".join(chunk), "retmode": "xml"})
        _rate_limit()
        raw = http_get(f"{BASE}/efetch.fcgi", params, cache=use_cache, timeout=90)
        studies.extend(parse_pubmed_xml(raw))
    return studies


def parse_pubmed_xml(xml_text: str) -> list[Study]:
    if not xml_text.strip():
        return []
    root = ET.fromstring(xml_text)
    out: list[Study] = []
    for art in root.findall(".//PubmedArticle"):
        pmid = art.findtext(".//PMID") or ""
        title = _text(art.find(".//ArticleTitle"))
        abstract_parts = []
        for ab in art.findall(".//Abstract/AbstractText"):
            label = ab.get("Label")
            txt = _text(ab)
            if txt:
                abstract_parts.append(f"{label}: {txt}" if label else txt)
        journal = art.findtext(".//Journal/Title") or art.findtext(".//Journal/ISOAbbreviation") or ""
        year = (
            art.findtext(".//JournalIssue/PubDate/Year")
            or (art.findtext(".//JournalIssue/PubDate/MedlineDate") or "")[:4]
            or art.findtext(".//ArticleDate/Year")
            or ""
        )
        authors = art.findall(".//AuthorList/Author")
        first_author = ""
        if authors:
            first_author = (authors[0].findtext("LastName") or "") + (
                (" " + authors[0].findtext("Initials")) if authors[0].findtext("Initials") else ""
            )
        doi = ""
        for aid in art.findall(".//ArticleIdList/ArticleId"):
            if aid.get("IdType") == "doi":
                doi = (aid.text or "").strip()
                break
        pubtypes = [pt.text or "" for pt in art.findall(".//PublicationTypeList/PublicationType")]
        mesh = [m.findtext("DescriptorName") or "" for m in art.findall(".//MeshHeading")]
        lang = art.findtext(".//Language") or ""
        out.append(
            Study(
                pmid=pmid,
                title=title,
                journal=journal,
                year=year,
                first_author=first_author,
                doi=doi,
                abstract=" ".join(abstract_parts),
                pubtypes=pubtypes,
                mesh_terms=mesh,
                language=lang,
            )
        )
    return out


def _text(el: ET.Element | None) -> str:
    if el is None:
        return ""
    return "".join(el.itertext()).strip()


def search_and_fetch(
    name: str,
    query: str,
    retmax: int = 200,
    mindate: str | None = None,
    maxdate: str | None = None,
    sort: str = "relevance",
    save: bool = True,
) -> dict[str, Any]:
    """Run esearch then efetch; persist a provenance-rich search record."""
    res = esearch(query, retmax=retmax, mindate=mindate, maxdate=maxdate, sort=sort)
    studies = efetch(res["pmids"]) if res["pmids"] else []
    record = {
        "search_id": name,
        "database": "PubMed/MEDLINE",
        "query": query,
        "query_translation": res["query_translation"],
        "date_filter": {"mindate": mindate, "maxdate": maxdate, "datetype": "pdat"} if mindate else None,
        "sort": sort,
        "retrieved_at": res["retrieved_at"],
        "count_total": res["count"],
        "retrieved_n": len(studies),
        "studies": [s.as_dict() for s in studies],
    }
    if save:
        path = config.SEARCHES / f"{name}.json"
        write_json(path, record)
        log.info("%s: %s records (of %s) -> %s", name, len(studies), res["count"], path.name)
    return record


def load_search(name: str) -> dict[str, Any]:
    return json.loads((config.SEARCHES / f"{name}.json").read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# Pre-registered query builders
# --------------------------------------------------------------------------
def exposure_query(terms: list[str], phenotype_terms: list[str] | None = None) -> str:
    exposure = "(" + " OR ".join(terms) + ")"
    chd = config.SEARCH_CONCEPTS["population"]
    pheno = ""
    if phenotype_terms:
        pheno = " AND (" + " OR ".join(phenotype_terms) + ")"
    return f"{exposure} AND {chd}{pheno}"


def domain_queries() -> dict[str, str]:
    """Five pre-registered feasibility domains (Fase A)."""
    chd = config.SEARCH_CONCEPTS["population"]
    exposure = config.SEARCH_CONCEPTS["exposure"]
    mechanism = config.SEARCH_CONCEPTS["mechanism"]
    development = config.SEARCH_CONCEPTS["development"]
    return {
        "A1_exposure_chd": f"{exposure} AND {chd}",
        "A2_exposure_mechanism": f"{exposure} AND {mechanism} AND (cardiac OR heart OR embry* OR pregnancy OR placenta*)",
        "A3_mechanism_cardiogenesis": f"{mechanism} AND {development}",
        "A4_cardiogenesis_phenotype": f"{development} AND {chd}",
        "A5_gene_phenotype": '(NKX2-5 OR GATA4 OR TBX5 OR NOTCH1 OR TBX1 OR JAG1) AND ("congenital heart"[tiab] OR "heart defect"[tiab] OR "cardiac malformation"[tiab])',
    }
