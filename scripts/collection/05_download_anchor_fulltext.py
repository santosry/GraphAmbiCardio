"""Download open-access full texts for the anchor studies (local only).

Outputs go to data_raw/anchor_fulltext/ (gitignored). For paywalled records we
save the abstract and the canonical links instead of pretending to have the PDF.
"""
from __future__ import annotations

import csv
import json
import re
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
ANCHORS = ROOT / "literature" / "curated" / "anchor_studies.csv"
OUT = ROOT / "data_raw" / "anchor_fulltext"
CAPES_ABS = ROOT / "literature" / "curated" / "capes_abstracts" / "7850222.json"
CAPES_HTML = ROOT / "data_raw" / "capes" / "7850222.html"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
EPMC_REST = "https://www.ebi.ac.uk/europepmc/webservices/rest"
HEADERS = {"User-Agent": "GraphAmbiCardio/0.1 (academic research; mailto:ryan.paulo@gsuite.iff.edu.br)"}


def slug(text: str) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "_", text or "").strip("_")
    return s[:70] or "study"


def get_epmc(pmid: str) -> dict:
    params = {"query": f"EXT_ID:{pmid}", "format": "json", "resultType": "core", "pageSize": 1}
    r = requests.get(EPMC, params=params, headers=HEADERS, timeout=60)
    r.raise_for_status()
    results = r.json().get("resultList", {}).get("result", [])
    return results[0] if results else {}


def pdf_urls(rec: dict) -> list[str]:
    out = []
    for item in (rec.get("fullTextUrlList", {}) or {}).get("fullTextUrl", []) or []:
        style = str(item.get("documentStyle", "")).lower()
        availability = str(item.get("availability", "")).lower()
        if style == "pdf" and ("open access" in availability or "free" in availability):
            url = item.get("url", "")
            if url:
                out.append(url)
    return out


def download_pdf(url: str, dest: Path) -> tuple[bool, str]:
    try:
        r = requests.get(url, headers=HEADERS, timeout=90, allow_redirects=True)
        if r.status_code == 200 and r.content[:4] == b"%PDF":
            dest.write_bytes(r.content)
            return True, f"PDF {len(r.content)} bytes"
        return False, f"HTTP {r.status_code}; content-type={r.headers.get('content-type','')}; not PDF"
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(ANCHORS.open(encoding="utf-8")))
    manifest = []
    for i, row in enumerate(rows, 1):
        pmid = (row.get("pmid") or "").strip()
        title = row.get("title", "")
        base = f"{i:02d}_{pmid or 'CAPES'}_{slug(title)}"
        rec = get_epmc(pmid) if pmid else {}
        abstract = rec.get("abstractText", "") or ""
        pmcid = rec.get("pmcid", "") or ""
        doi = rec.get("doi", "") or row.get("doi", "")
        links = [f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"] if pmid else []
        if doi:
            links.append(f"https://doi.org/{doi}")
        pdf_dest = OUT / f"{base}.pdf"
        xml_dest = OUT / f"{base}.fulltext.xml"
        status = "pdf" if pdf_dest.exists() else ("fulltext_xml" if xml_dest.exists() else "abstract_only")
        pdf_file = pdf_dest.name if pdf_dest.exists() else ""
        xml_file = xml_dest.name if xml_dest.exists() else ""
        for url in pdf_urls(rec):
            dest = pdf_dest
            ok, msg = download_pdf(url, dest)
            if ok:
                status = "pdf"
                pdf_file = dest.name
                break
            time.sleep(0.3)
        if not pdf_file and doi:
            try:
                ur = requests.get(
                    f"https://api.unpaywall.org/v2/{doi}",
                    params={"email": "ryan.paulo@gsuite.iff.edu.br"},
                    headers=HEADERS, timeout=60,
                )
                if ur.status_code == 200:
                    loc = ur.json().get("best_oa_location") or {}
                    pdf_url = loc.get("url_for_pdf")
                    if pdf_url:
                        dest = OUT / f"{base}.pdf"
                        ok, _ = download_pdf(pdf_url, dest)
                        if ok:
                            status = "pdf"
                            pdf_file = dest.name
            except Exception:
                pass
            time.sleep(0.2)
        if pmcid and not pdf_file and not xml_file:
            try:
                xr = requests.get(f"{EPMC_REST}/{pmcid}/fullTextXML", headers=HEADERS, timeout=90)
                if xr.status_code == 200 and xr.content.lstrip().startswith(b"<"):
                    xml_dest.write_bytes(xr.content)
                    status = "fulltext_xml"
                    xml_file = xml_dest.name
            except Exception:
                pass
            time.sleep(0.2)
        if abstract:
            (OUT / f"{base}.abstract.txt").write_text(
                f"TITLE: {title}\nPMID: {pmid}\nPMCID: {pmcid}\nDOI: {doi}\n\n{abstract}\n",
                encoding="utf-8",
            )
        (OUT / f"{base}.links.txt").write_text("\n".join(links) + "\n", encoding="utf-8")
        manifest.append(
            {
                "n": i,
                "pmid": pmid,
                "pmcid": pmcid,
                "doi": doi,
                "title": title,
                "journal": row.get("journal", ""),
                "year": row.get("year", ""),
                "status": status,
                "pdf_file": pdf_file,
                "abstract_file": f"{base}.abstract.txt" if abstract else "",
                "xml_file": xml_file,
                "links_file": f"{base}.links.txt",
                "links": ";".join(links),
            }
        )
        print(f"{i:02d}/{len(rows)} {pmid or 'CAPES'} {status} {title[:80]}", flush=True)
        time.sleep(0.2)

    # CAPES thesis: abstract and metadata are available; full text is not always open.
    if CAPES_ABS.exists():
        data = json.loads(CAPES_ABS.read_text(encoding="utf-8"))
        (OUT / "34_CAPES_7850222.abstract.txt").write_text(
            f"TITLE: {data.get('title','')}\nAUTHOR: {data.get('author','')}\nYEAR: {data.get('year','')}\n"
            f"INSTITUTION: {data.get('institution','')}\nURL: {data.get('source_url','')}\n\n{data.get('abstract','')}\n",
            encoding="utf-8",
        )
        if CAPES_HTML.exists():
            (OUT / "34_CAPES_7850222.metadata.html").write_bytes(CAPES_HTML.read_bytes())

    with (OUT / "manifest.csv").open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(manifest[0].keys()))
        writer.writeheader()
        writer.writerows(manifest)
    html = ["<!doctype html><html lang='pt-BR'><meta charset='utf-8'><title>Textos integrais dos estudos-âncora</title>",
            "<style>body{font-family:Arial,Helvetica,sans-serif;max-width:980px;margin:2rem auto;line-height:1.5;color:#222}",
            "li{margin:.55rem 0}small{color:#666}</style><h1>Textos integrais dos estudos-âncora</h1>",
            "<p>Arquivos locais. PDFs só foram salvos quando havia acesso aberto; os demais têm resumo e links.</p><ol>"]
    for m in manifest:
        target = m["pdf_file"] or m.get("xml_file") or m["abstract_file"]
        html.append(f"<li><b>{m['title']}</b><br><small>{m['journal']} ({m['year']}) · {m['status']}</small><br>"
                    f"<a href='{target}'>{target}</a> · <a href='{m['links'].split(';')[0]}'>fonte</a></li>")
    html.append("</ol></html>")
    (OUT / "index.html").write_text("\n".join(html), encoding="utf-8")
    print(f"written {OUT / 'manifest.csv'}")


if __name__ == "__main__":
    main()
