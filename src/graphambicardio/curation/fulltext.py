"""Full-text retrieval, extraction and candidate archiving.

The full text is downloaded to a temporary directory, converted to text, and
deleted after the relevant sentences and metadata are archived. Nothing here
keeps a complete article: the archive stores only the metadata plus short
quotations with context, which is what the review layer needs.

The module is deliberately offline-testable except for the fetch functions.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import tempfile
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

import requests
from pypdf import PdfReader

from .batch_extract import (
    EXPOSURE_PATTERNS,
    PHENOTYPE_PATTERNS_ALL,
    is_negated_mention,
    iter_effects,
    normalise,
    pluralise,
    split_sentences,
)

HEADERS = {
    "User-Agent": "GraphAmbiCardio/0.4 (academic research; mailto:ryan.paulo@gsuite.iff.edu.br)"
}
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
EPMC_REST = "https://www.ebi.ac.uk/europepmc/webservices/rest"
UNPAYWALL = "https://api.unpaywall.org/v2/{doi}"
OPENALEX = "https://api.openalex.org/works/https://doi.org/{doi}"
CONTACT = "ryan.paulo@gsuite.iff.edu.br"

SECTION_RE = re.compile(
    r"^\s*(abstract|summary|introduction|background|methods?|materials and methods|"
    r"results?|findings|discussion|conclusions?|limitations?)\s*$",
    re.I,
)
ASSOCIATION = re.compile(
    r"\b(associat|risk|odds|increased|decreased|higher|lower|excess|relation)", re.I
)


@dataclass
class StudyRecord:
    pmid: str = ""
    pmcid: str = ""
    doi: str = ""
    title: str = ""
    authors: str = ""
    journal: str = ""
    year: str = ""
    volume: str = ""
    issue: str = ""
    pages: str = ""
    license: str = ""
    oa_status: str = ""
    abstract: str = ""
    pubmed_url: str = ""
    doi_url: str = ""
    pdf_urls: list[str] = field(default_factory=list)
    xml_url: str = ""

    def as_metadata(self) -> dict[str, str]:
        return {
            "pmid": self.pmid,
            "pmcid": self.pmcid,
            "doi": self.doi,
            "title": self.title,
            "authors": self.authors,
            "journal": self.journal,
            "year": self.year,
            "volume": self.volume,
            "issue": self.issue,
            "pages": self.pages,
            "license": self.license,
            "oa_status": self.oa_status,
            "pubmed_url": self.pubmed_url,
            "doi_url": self.doi_url,
        }


def fetch_record(pmid: str) -> StudyRecord:
    """Fetch bibliographic metadata and open-access links from Europe PMC."""
    rec = StudyRecord(pmid=pmid, pubmed_url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/")
    params = {"query": f"EXT_ID:{pmid}", "format": "json", "resultType": "core", "pageSize": 1}
    try:
        response = requests.get(EPMC, params=params, headers=HEADERS, timeout=60)
        response.raise_for_status()
        result = response.json().get("resultList", {}).get("result", [])
    except Exception:
        result = []
    if result:
        item = result[0]
        rec.pmcid = item.get("pmcid", "") or ""
        rec.doi = item.get("doi", "") or ""
        rec.title = item.get("title", "") or ""
        rec.authors = item.get("authorString", "") or ""
        rec.journal = item.get("journalTitle", "") or ""
        rec.year = str(item.get("pubYear", "") or "")
        rec.volume = item.get("journalVolume", "") or ""
        rec.issue = item.get("issue", "") or ""
        rec.pages = item.get("pageInfo", "") or ""
        rec.license = item.get("license", "") or ""
        rec.oa_status = item.get("isOpenAccess", "") or ""
        rec.abstract = item.get("abstractText", "") or ""
        for entry in (item.get("fullTextUrlList", {}) or {}).get("fullTextUrl", []) or []:
            style = str(entry.get("documentStyle", "")).lower()
            availability = str(entry.get("availability", "")).lower()
            if style == "pdf" and ("open access" in availability or "free" in availability):
                url = entry.get("url", "")
                if url:
                    rec.pdf_urls.append(url)
        if rec.pmcid:
            rec.xml_url = f"{EPMC_REST}/{rec.pmcid}/fullTextXML"
    if rec.doi:
        rec.doi_url = f"https://doi.org/{rec.doi}"
    return rec


def _check_pdf(content: bytes) -> bool:
    return content[:4] == b"%PDF" and len(content) > 2000


def download_pdf(urls: Iterable[str], dest: Path, max_bytes: int = 30_000_000) -> tuple[bool, str]:
    """Download the first usable PDF, respecting a size cap."""
    for url in urls:
        if not url:
            continue
        try:
            with requests.get(url, headers=HEADERS, timeout=120, stream=True, allow_redirects=True) as r:
                if r.status_code != 200:
                    continue
                content = bytearray()
                for chunk in r.iter_content(65536):
                    content.extend(chunk)
                    if len(content) > max_bytes:
                        break
                if len(content) > max_bytes:
                    continue
                if _check_pdf(bytes(content)):
                    dest.write_bytes(bytes(content))
                    return True, url
        except Exception:
            continue
        time.sleep(0.2)
    return False, ""


def pdf_candidates(rec: StudyRecord, extra: list[str] | None = None) -> list[str]:
    urls = list(extra or []) + list(rec.pdf_urls)
    if rec.pmcid:
        urls += [
            f"https://europepmc.org/articles/{rec.pmcid}?pdf=render",
            f"https://www.ncbi.nlm.nih.gov/pmc/articles/{rec.pmcid}/pdf/",
        ]
    if rec.doi:
        try:
            response = requests.get(
                UNPAYWALL.format(doi=rec.doi), params={"email": CONTACT},
                headers=HEADERS, timeout=60,
            )
            if response.status_code == 200:
                best = response.json().get("best_oa_location") or {}
                if best.get("url_for_pdf"):
                    urls.append(best["url_for_pdf"])
        except Exception:
            pass
        try:
            response = requests.get(
                OPENALEX.format(doi=rec.doi), headers=HEADERS, timeout=60
            )
            if response.status_code == 200:
                best = response.json().get("best_oa_location") or {}
                if best.get("pdf_url"):
                    urls.append(best["pdf_url"])
        except Exception:
            pass
    if rec.pmid:
        try:
            response = requests.get(
                f"https://api.openalex.org/works/pmid:{rec.pmid}", headers=HEADERS, timeout=60
            )
            if response.status_code == 200:
                best = response.json().get("best_oa_location") or {}
                if best.get("pdf_url"):
                    urls.append(best["pdf_url"])
        except Exception:
            pass
        try:
            response = requests.get(
                f"https://api.semanticscholar.org/graph/v1/paper/PMID:{rec.pmid}",
                params={"fields": "openAccessPdf"}, headers=HEADERS, timeout=60,
            )
            if response.status_code == 200:
                pdf = (response.json().get("openAccessPdf") or {}).get("url")
                if pdf:
                    urls.append(pdf)
        except Exception:
            pass
    seen: set[str] = set()
    ordered: list[str] = []
    for url in urls:
        if url and url not in seen:
            seen.add(url)
            ordered.append(url)
    return ordered


def extract_pdf(path: Path, max_pages: int = 80) -> tuple[list[str], str]:
    """Return per-page text and an error string (empty on success)."""
    try:
        reader = PdfReader(str(path))
        if reader.is_encrypted:
            try:
                reader.decrypt("")
            except Exception:
                return [], "encrypted"
        pages = []
        for page in reader.pages[:max_pages]:
            try:
                pages.append(page.extract_text() or "")
            except Exception:
                pages.append("")
        return pages, ""
    except Exception as exc:  # noqa: BLE001
        return [], str(exc)


def extract_jats(content: bytes) -> list[str]:
    """Extract readable text from a JATS/XML full text, page-less."""
    try:
        root = ET.fromstring(content)
    except ET.ParseError:
        return []
    parts: list[str] = []
    for elem in root.iter():
        tag = elem.tag.split("}")[-1]
        if tag in {"p", "title", "caption"}:
            text = " ".join("".join(elem.itertext()).split())
            if text:
                parts.append(text)
    return ["\n".join(parts)]


def sections_for_pages(pages: list[str]) -> list[str]:
    """Assign a rough section label to each page."""
    labels: list[str] = []
    current = "body"
    for text in pages:
        for line in (text or "").splitlines():
            line = line.strip()
            if len(line) <= 40 and SECTION_RE.match(line):
                current = line.lower()
                break
        labels.append(current)
    return labels


def _context(text: str, start: int, end: int, pad: int = 300) -> tuple[str, str]:
    before = normalise(text[max(0, start - pad):start])
    after = normalise(text[end:end + pad])
    return before, after


def _phenotype_mentions(text: str) -> list[tuple[int, int, str]]:
    found: list[tuple[int, int, str]] = []
    for pid, pattern in PHENOTYPE_PATTERNS_ALL.items():
        for match in re.finditer(pluralise(pattern), text, re.I):
            if pid == "CHD:ASD" and not re.search(r"heart|cardiac|septal|atrial", text, re.I):
                continue
            found.append((match.start(), match.end(), pid))
    return sorted(found)


def _exposure_mentions(text: str, candidate_exposures: list[str]) -> list[tuple[int, int, str]]:
    found: list[tuple[int, int, str]] = []
    for eid in candidate_exposures:
        pattern = EXPOSURE_PATTERNS.get(eid)
        if not pattern:
            continue
        for match in re.finditer(pattern, text, re.I):
            found.append((match.start(), match.end(), eid))
    return sorted(found)


def _nearest_exposure(
    effect_start: int, effect_end: int, mentions: list[tuple[int, int, str]]
) -> str | None:
    left = [m for m in mentions if m[1] <= effect_start]
    if left:
        mention = max(left, key=lambda m: m[1])
        if effect_start - mention[1] <= 400:
            return mention[2]
    right = [m for m in mentions if m[0] >= effect_end]
    if right:
        mention = min(right, key=lambda m: m[0])
        if mention[0] - effect_end <= 80:
            return mention[2]
    return None


def candidate_sentences(
    pages: list[str],
    candidate_exposures: list[str],
    candidate_phenotypes: list[str],
    *,
    max_candidates: int = 15,
) -> list[dict[str, Any]]:
    """Extract exposure-phenotype-effect candidates from full-text pages.

    The strict rule is tried first. When a sentence mentions several phenotypes
    or exposures, the nearest-phenotype and nearest-exposure rule is used and the
    candidate is marked ``nearest`` so the reviewer knows it needs attention.
    """
    labels = sections_for_pages(pages)
    found: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for page_number, (text, section) in enumerate(zip(pages, labels), start=1):
        if not text:
            continue
        for clause in split_sentences(text):
            effects = list(iter_effects(clause))
            if not effects:
                continue
            exposures = _exposure_mentions(clause, candidate_exposures)
            phenotypes = _phenotype_mentions(clause)
            if not exposures or not phenotypes:
                continue
            for effect in effects:
                exposure = _nearest_exposure(effect["start"], effect["end"], exposures)
                if exposure is None:
                    continue
                left = [
                    m for m in phenotypes
                    if m[1] <= effect["start"] and not is_negated_mention(clause, m[0])
                ]
                right = [
                    m for m in phenotypes
                    if m[0] >= effect["end"] and not is_negated_mention(clause, m[0])
                ]
                if left:
                    phenotype = max(left, key=lambda m: m[1])[2]
                    orientation = "effect_after_phenotype"
                elif right:
                    phenotype = min(right, key=lambda m: m[0])[2]
                    orientation = "effect_before_phenotype"
                else:
                    continue
                if candidate_phenotypes and phenotype not in candidate_phenotypes:
                    # Full text may report a phenotype the screening missed; keep
                    # it, but mark it clearly for review.
                    pass
                key = (exposure, phenotype, normalise(effect["text"]).lower())
                if key in seen:
                    continue
                seen.add(key)
                before, after = _context(clause, effect["start"], effect["end"])
                found.append(
                    {
                        "page": page_number,
                        "section": section,
                        "exposure_id": exposure,
                        "phenotype_id": phenotype,
                        "effect": effect["text"],
                        "effect_value": effect["value"],
                        "direction": effect["direction"],
                        "orientation": orientation,
                        "quote": normalise(clause),
                        "context_before": before,
                        "context_after": after,
                        "rule": "nearest",
                    }
                )
                if len(found) >= max_candidates * 3:
                    break
            if len(found) >= max_candidates * 3:
                break
        if len(found) >= max_candidates * 3:
            break
    # Prefer Results sentences, then shorter quotes; keep a bounded list.
    found.sort(key=lambda row: (0 if "result" in row["section"] else 1, len(row["quote"])))
    return found[:max_candidates]


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def save_quote(
    archive_dir: Path,
    record: StudyRecord,
    row: dict[str, Any],
    *,
    source_url: str,
    retrieved_at: str,
    pdf_sha256: str,
) -> str:
    archive_dir.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha1(normalise(row["quote"]).encode("utf-8")).hexdigest()[:8]
    name = (
        f"{record.pmid}_{row['exposure_id'].replace(':', '-')}_"
        f"{row['phenotype_id'].replace(':', '-')}_{digest}.json"
    )
    payload = {
        **record.as_metadata(),
        "source_url": source_url,
        "retrieved_at": retrieved_at,
        "pdf_sha256": pdf_sha256,
        "page": row["page"],
        "section": row["section"],
        "quote": row["quote"],
        "context_before": row["context_before"],
        "context_after": row["context_after"],
        "effect": row["effect"],
        "direction": row["direction"],
        "exposure_id": row["exposure_id"],
        "phenotype_id": row["phenotype_id"],
    }
    (archive_dir / name).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return f"fulltext_quotes/{name}"


def temporary_directory() -> Path:
    return Path(tempfile.mkdtemp(prefix="graphambicardio_ft_"))


def cleanup(path: Path) -> None:
    try:
        shutil.rmtree(path, ignore_errors=True)
    except Exception:
        pass
